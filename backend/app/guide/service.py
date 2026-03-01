import logging
from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.guide.model import GuideChunk, GuideDocument
from app.shared.crawling import ContentFormat, get_parser
from app.shared.crawling.crawler import crawl_site
from app.shared.embedding import embed_text, embed_texts

logger = logging.getLogger(__name__)

_SITE_NOISE = {"식스샵 프로 가이드", "(클릭) "}
_REQUIRED_BREADCRUMB_PREFIX = "식스샵 프로 활용하기"
_MIN_BREADCRUMB_DEPTH = 4  # "가이드 > 활용하기 > 카테고리 > 페이지" = 콘텐츠
_SIMILARITY_THRESHOLD = 0.45

_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)


def _is_guide_content(breadcrumb: str | None) -> bool:
    """브레드크럼 기반으로 가이드 콘텐츠 페이지인지 판단한다.

    - '식스샵 프로 활용하기' 하위 페이지만 허용
    - 인덱스 페이지(3단계) 제외, 실제 콘텐츠(4단계+)만 포함
    """
    if not breadcrumb:
        return False
    parts = [p.strip() for p in breadcrumb.split(" > ")]
    if len(parts) < 2 or parts[1] != _REQUIRED_BREADCRUMB_PREFIX:
        return False
    return len(parts) >= _MIN_BREADCRUMB_DEPTH


def _remove_noise(content: str, noise: set[str]) -> str:
    """파싱된 콘텐츠에서 사이트 고유의 불필요한 텍스트를 제거한다."""
    lines = content.split("\n")
    for n in noise:
        lines = [line.replace(n, "") for line in lines]
    return "\n".join(line for line in lines if line.strip())


def _create_chunks(db: Session, doc: GuideDocument) -> list[GuideChunk]:
    """문서를 청킹하고 임베딩하여 GuideChunk를 생성한다."""
    chunks = _text_splitter.split_text(doc.content)
    if not chunks:
        return []

    embedding_inputs = [f"{doc.title}\n\n{chunk}" for chunk in chunks]
    embeddings = embed_texts(embedding_inputs)

    guide_chunks = []
    for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        guide_chunk = GuideChunk(
            document_id=doc.id,
            content=chunk_text,
            embedding=embedding,
            chunk_index=i,
        )
        db.add(guide_chunk)
        guide_chunks.append(guide_chunk)

    return guide_chunks


def crawl_and_ingest(
    db: Session, url: str, *, html: str | None = None
) -> GuideDocument | None:
    """URL에서 가이드 문서를 크롤링하여 DB에 저장한다. 이미 존재하면 업데이트한다.

    브레드크럼 기반으로 가이드 콘텐츠가 아닌 페이지는 건너뛴다.
    """
    parser = get_parser(url)
    if html is None:
        html, _ = parser.fetch_html(url)
    result = parser.parse(html, content_format=ContentFormat.MARKDOWN)
    content = _remove_noise(result.content, _SITE_NOISE)

    if not _is_guide_content(result.breadcrumb):
        logger.info(f"  건너뜀 (비가이드): {url} (breadcrumb: {result.breadcrumb})")
        return None

    existing = db.execute(
        select(GuideDocument).where(GuideDocument.url == url)
    ).scalar_one_or_none()

    if existing:
        existing.title = result.title
        existing.content = content
        existing.breadcrumb = result.breadcrumb
        db.flush()
        db.execute(
            delete(GuideChunk).where(GuideChunk.document_id == existing.id)
        )
        db.flush()
        _create_chunks(db, existing)
        db.commit()
        db.refresh(existing)
        return existing

    doc = GuideDocument(
        url=url,
        title=result.title,
        content=content,
        breadcrumb=result.breadcrumb,
    )
    db.add(doc)
    db.flush()
    _create_chunks(db, doc)
    db.commit()
    db.refresh(doc)
    return doc


@dataclass
class GuideCrawlResult:
    """가이드 사이트 크롤링 결과 요약."""

    total_pages: int = 0
    new_pages: int = 0
    updated_pages: int = 0
    skipped_pages: int = 0
    failed_urls: list[str] = field(default_factory=list)


def crawl_guide_site(
    db: Session,
    root_url: str,
    *,
    max_pages: int = 200,
    max_depth: int = 5,
    delay: float = 1.0,
) -> GuideCrawlResult:
    """루트 URL에서 가이드 페이지를 재귀 크롤링하여 DB에 저장한다."""
    guide_result = GuideCrawlResult()

    def on_page(url: str, html: str):
        is_existing = db.execute(
            select(GuideDocument).where(GuideDocument.url == url)
        ).scalar_one_or_none()
        doc = crawl_and_ingest(db, url, html=html)
        if doc is None:
            guide_result.skipped_pages += 1
            return
        if is_existing:
            guide_result.updated_pages += 1
        else:
            guide_result.new_pages += 1

    crawl_result = crawl_site(
        root_url,
        on_page=on_page,
        max_pages=max_pages,
        max_depth=max_depth,
        delay=delay,
    )
    guide_result.total_pages = crawl_result.total_pages
    guide_result.failed_urls = crawl_result.failed_urls
    return guide_result


def search_guide(db: Session, query: str, top_k: int = 3) -> list[dict]:
    """사용자 질문과 유사한 가이드 청크를 검색한다."""
    query_vector = embed_text(query)

    results = db.execute(
        select(
            GuideChunk,
            GuideDocument,
            GuideChunk.embedding.cosine_distance(query_vector).label("distance"),
        )
        .join(GuideDocument, GuideChunk.document_id == GuideDocument.id)
        .order_by("distance")
        .limit(top_k)
    ).all()

    return [
        {
            "title": doc.title,
            "content": chunk.content,
            "url": doc.url,
            "breadcrumb": doc.breadcrumb,
            "similarity": round(1 - distance, 4),
        }
        for chunk, doc, distance in results
        if 1 - distance >= _SIMILARITY_THRESHOLD
    ]

"""
테이블별 Display ID 유틸리티.

내부 PK(int)는 유지하고, 외부(API 응답)에서는 사람이 읽기 쉬운 형태로 변환한다.
예: conversations.id=1 → "CON-1", messages.id=42 → "MSG-42"
"""

PREFIXES = {
    "conversations": "CON",
    "messages": "MSG",
    "products": "PRD",
    "sellers": "SLR",
}


def to_display_id(table: str, pk: int) -> str:
    prefix = PREFIXES[table]
    return f"{prefix}-{pk}"


def from_display_id(display_id: str) -> tuple[str, int]:
    """Display ID를 (테이블명, PK)로 역변환한다."""
    prefix, _, pk_str = display_id.upper().partition("-")

    if not pk_str:
        raise ValueError(f"잘못된 display ID 형식: {display_id}")

    table = _prefix_to_table(prefix)
    return table, int(pk_str)


def parse_pk(display_id: str, expected_table: str) -> int:
    """Display ID에서 PK만 추출한다. 숫자만 들어오면 바로 PK로 처리한다."""
    if display_id.isdigit():
        return int(display_id)

    table, pk = from_display_id(display_id)

    if table != expected_table:
        raise ValueError(
            f"잘못된 ID 타입: {display_id} (expected: {PREFIXES[expected_table]})"
        )

    return pk


_REVERSE_PREFIXES = {v: k for k, v in PREFIXES.items()}


def _prefix_to_table(prefix: str) -> str:
    table = _REVERSE_PREFIXES.get(prefix)

    if not table:
        raise ValueError(f"알 수 없는 prefix: {prefix}")

    return table

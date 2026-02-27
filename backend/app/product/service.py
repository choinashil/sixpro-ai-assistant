from sqlalchemy.orm import Session

from app.product.model import Product, ProductStatus

_UPDATABLE_FIELDS = {"name", "price", "status"}


_MIN_PRICE = 0
_MAX_PRICE = 10_000_000


def _validate_price(price: int) -> None:
    if price < _MIN_PRICE:
        raise ValueError(f"가격은 {_MIN_PRICE:,}원 이상이어야 합니다")
    if price > _MAX_PRICE:
        raise ValueError(f"가격은 {_MAX_PRICE:,}원 이하여야 합니다")


def create_product(db: Session, seller_id: int, name: str, price: int) -> Product:
    """상품을 생성한다."""
    _validate_price(price)
    product = Product(
        name=name,
        price=price,
        seller_id=seller_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, seller_id: int, product_id: int, **fields) -> Product:
    """상품 정보를 수정한다. name, price, status만 변경 가능."""
    product = _get_product_or_raise(db, seller_id, product_id)

    for key, value in fields.items():
        if key not in _UPDATABLE_FIELDS:
            raise ValueError(f"수정할 수 없는 필드: {key}")
        if key == "price":
            _validate_price(value)
        if key == "status":
            value = ProductStatus(value)
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, seller_id: int, product_id: int) -> Product:
    """상품을 삭제한다. (soft delete: is_deleted = True)"""
    product = _get_product_or_raise(db, seller_id, product_id)
    product.is_deleted = True
    db.commit()
    db.refresh(product)
    return product


def list_products(
    db: Session,
    seller_id: int | None = None,
    status: str | None = None,
    name: str | None = None,
) -> list[Product]:
    """상품 목록을 조회한다. 삭제된 상품은 제외."""
    query = db.query(Product).filter(Product.is_deleted == False)  # noqa: E712

    if seller_id is not None:
        query = query.filter(Product.seller_id == seller_id)

    if status is not None:
        query = query.filter(Product.status == ProductStatus(status))

    if name is not None:
        query = query.filter(Product.name.ilike(f"%{name}%"))

    return query.order_by(Product.id.desc()).all()


def _get_product_or_raise(db: Session, seller_id: int, product_id: int) -> Product:
    """seller_id에 속한 삭제되지 않은 상품을 조회한다. 없으면 ValueError."""
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.seller_id == seller_id,
            Product.is_deleted == False,  # noqa: E712
        )
        .first()
    )

    if product is None:
        raise ValueError(f"상품을 찾을 수 없습니다 (id={product_id})")

    return product

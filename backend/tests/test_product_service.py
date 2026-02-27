import pytest

from app.product.model import ProductStatus
from app.product.service import create_product, delete_product, list_products, update_product
from app.seller.service import create_seller


class TestCreateProduct:
    def test_creates_product(self, db):
        seller = create_seller(db)
        product = create_product(db, name="테스트 상품", price=10000, seller_id=seller.id)

        assert product.name == "테스트 상품"
        assert product.price == 10000
        assert product.seller_id == seller.id
        assert product.id is not None

    def test_default_status_is_active(self, db):
        seller = create_seller(db)
        product = create_product(db, name="테스트 상품", price=10000, seller_id=seller.id)

        assert product.status == ProductStatus.ACTIVE

    def test_raises_for_negative_price(self, db):
        seller = create_seller(db)

        with pytest.raises(ValueError, match="가격은 0원 이상이어야 합니다"):
            create_product(db, name="상품", price=-1000, seller_id=seller.id)

    def test_raises_for_exceeding_max_price(self, db):
        seller = create_seller(db)

        with pytest.raises(ValueError, match="가격은 10,000,000원 이하여야 합니다"):
            create_product(db, name="상품", price=10_000_001, seller_id=seller.id)


class TestListProducts:
    def test_returns_all_products_for_seller(self, db):
        seller = create_seller(db)
        create_product(db, name="상품A", price=1000, seller_id=seller.id)
        create_product(db, name="상품B", price=2000, seller_id=seller.id)

        result = list_products(db, seller_id=seller.id)

        assert len(result) == 2

    def test_filters_by_seller(self, db):
        seller_a = create_seller(db)
        seller_b = create_seller(db)
        create_product(db, name="A의 상품", price=1000, seller_id=seller_a.id)
        create_product(db, name="B의 상품", price=2000, seller_id=seller_b.id)

        result = list_products(db, seller_id=seller_a.id)

        assert len(result) == 1
        assert result[0].name == "A의 상품"

    def test_filter_by_active(self, db):
        seller = create_seller(db)
        create_product(db, name="활성 상품", price=1000, seller_id=seller.id)
        inactive = create_product(db, name="비활성 상품", price=2000, seller_id=seller.id)
        inactive.status = ProductStatus.INACTIVE
        db.commit()

        result = list_products(db, status="active", seller_id=seller.id)

        assert len(result) == 1
        assert result[0].name == "활성 상품"

    def test_filter_by_inactive(self, db):
        seller = create_seller(db)
        create_product(db, name="활성 상품", price=1000, seller_id=seller.id)
        inactive = create_product(db, name="비활성 상품", price=2000, seller_id=seller.id)
        inactive.status = ProductStatus.INACTIVE
        db.commit()

        result = list_products(db, status="inactive", seller_id=seller.id)

        assert len(result) == 1
        assert result[0].name == "비활성 상품"

    def test_empty_list(self, db):
        seller = create_seller(db)

        result = list_products(db, seller_id=seller.id)

        assert result == []

    def test_ordered_by_latest_first(self, db):
        seller = create_seller(db)
        create_product(db, name="먼저", price=1000, seller_id=seller.id)
        create_product(db, name="나중에", price=2000, seller_id=seller.id)

        result = list_products(db, seller_id=seller.id)

        assert result[0].name == "나중에"
        assert result[1].name == "먼저"

    def test_filters_by_name(self, db):
        seller = create_seller(db)
        create_product(db, name="바나나", price=1000, seller_id=seller.id)
        create_product(db, name="바나나 우유", price=2000, seller_id=seller.id)
        create_product(db, name="딸기", price=3000, seller_id=seller.id)

        result = list_products(db, seller_id=seller.id, name="바나나")

        assert len(result) == 2
        assert all("바나나" in p.name for p in result)

    def test_filters_by_name_case_insensitive(self, db):
        seller = create_seller(db)
        create_product(db, name="Banana", price=1000, seller_id=seller.id)
        create_product(db, name="banana juice", price=2000, seller_id=seller.id)

        result = list_products(db, seller_id=seller.id, name="banana")

        assert len(result) == 2

    def test_excludes_deleted_products(self, db):
        seller = create_seller(db)
        create_product(db, name="정상 상품", price=1000, seller_id=seller.id)
        deleted = create_product(db, name="삭제된 상품", price=2000, seller_id=seller.id)
        deleted.is_deleted = True
        db.commit()

        result = list_products(db, seller_id=seller.id)

        assert len(result) == 1
        assert result[0].name == "정상 상품"


class TestUpdateProduct:
    def test_updates_name(self, db):
        seller = create_seller(db)
        product = create_product(db, name="원래 이름", price=10000, seller_id=seller.id)

        updated = update_product(db, seller_id=seller.id, product_id=product.id, name="새 이름")

        assert updated.name == "새 이름"
        assert updated.price == 10000

    def test_updates_price(self, db):
        seller = create_seller(db)
        product = create_product(db, name="상품", price=10000, seller_id=seller.id)

        updated = update_product(db, seller_id=seller.id, product_id=product.id, price=20000)

        assert updated.price == 20000

    def test_updates_status(self, db):
        seller = create_seller(db)
        product = create_product(db, name="상품", price=10000, seller_id=seller.id)

        updated = update_product(
            db, seller_id=seller.id, product_id=product.id, status="inactive"
        )

        assert updated.status == ProductStatus.INACTIVE

    def test_updates_multiple_fields(self, db):
        seller = create_seller(db)
        product = create_product(db, name="원래", price=10000, seller_id=seller.id)

        updated = update_product(
            db, seller_id=seller.id, product_id=product.id, name="변경", price=20000
        )

        assert updated.name == "변경"
        assert updated.price == 20000

    def test_raises_for_nonexistent_product(self, db):
        seller = create_seller(db)

        with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
            update_product(db, seller_id=seller.id, product_id=9999, name="변경")

    def test_raises_for_other_seller(self, db):
        seller_a = create_seller(db)
        seller_b = create_seller(db)
        product = create_product(db, name="A의 상품", price=10000, seller_id=seller_a.id)

        with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
            update_product(db, seller_id=seller_b.id, product_id=product.id, name="변경")

    def test_raises_for_deleted_product(self, db):
        seller = create_seller(db)
        product = create_product(db, name="상품", price=10000, seller_id=seller.id)
        product.is_deleted = True
        db.commit()

        with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
            update_product(db, seller_id=seller.id, product_id=product.id, name="변경")

    def test_raises_for_invalid_field(self, db):
        seller = create_seller(db)
        product = create_product(db, name="상품", price=10000, seller_id=seller.id)

        with pytest.raises(ValueError, match="수정할 수 없는 필드"):
            update_product(db, seller_id=seller.id, product_id=product.id, seller_id_=999)

    def test_raises_for_negative_price(self, db):
        seller = create_seller(db)
        product = create_product(db, name="상품", price=10000, seller_id=seller.id)

        with pytest.raises(ValueError, match="가격은 0원 이상이어야 합니다"):
            update_product(db, seller_id=seller.id, product_id=product.id, price=-500)

    def test_raises_for_exceeding_max_price(self, db):
        seller = create_seller(db)
        product = create_product(db, name="상품", price=10000, seller_id=seller.id)

        with pytest.raises(ValueError, match="가격은 10,000,000원 이하여야 합니다"):
            update_product(db, seller_id=seller.id, product_id=product.id, price=10_000_001)


class TestDeleteProduct:
    def test_soft_deletes_product(self, db):
        seller = create_seller(db)
        product = create_product(db, name="상품", price=10000, seller_id=seller.id)

        deleted = delete_product(db, seller_id=seller.id, product_id=product.id)

        assert deleted.is_deleted is True

    def test_raises_for_nonexistent_product(self, db):
        seller = create_seller(db)

        with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
            delete_product(db, seller_id=seller.id, product_id=9999)

    def test_raises_for_other_seller(self, db):
        seller_a = create_seller(db)
        seller_b = create_seller(db)
        product = create_product(db, name="A의 상품", price=10000, seller_id=seller_a.id)

        with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
            delete_product(db, seller_id=seller_b.id, product_id=product.id)

    def test_raises_for_already_deleted_product(self, db):
        seller = create_seller(db)
        product = create_product(db, name="상품", price=10000, seller_id=seller.id)
        product.is_deleted = True
        db.commit()

        with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
            delete_product(db, seller_id=seller.id, product_id=product.id)

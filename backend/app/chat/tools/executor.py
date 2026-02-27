from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.shared.display_id import parse_pk, to_display_id
from app.guide.service import search_guide
from app.product.service import create_product, delete_product, list_products, update_product


@dataclass
class ToolContext:
    db: Session
    seller_id: int


def execute_tool(ctx: ToolContext, tool_name: str, arguments: dict) -> dict:
    """tool_name에 해당하는 함수를 실행하고 결과를 dict로 반환한다."""
    handler = _TOOL_HANDLERS.get(tool_name)

    if handler is None:
        return {"error": f"알 수 없는 tool: {tool_name}"}

    try:
        return handler(ctx, arguments)
    except ValueError as e:
        return {"error": str(e)}


def _handle_search_guide(ctx: ToolContext, arguments: dict) -> dict:
    query = arguments["query"]
    results = search_guide(ctx.db, query)
    return {"results": results, "total": len(results)}


def _handle_create_product(ctx: ToolContext, arguments: dict) -> dict:
    product = create_product(
        ctx.db, seller_id=ctx.seller_id, name=arguments["name"], price=arguments["price"]
    )
    return _product_to_dict(product)


def _handle_list_products(ctx: ToolContext, arguments: dict) -> dict:
    product_id = parse_pk(arguments["id"], "products") if "id" in arguments else None
    status = arguments.get("status")
    name = arguments.get("name")
    products = list_products(
        ctx.db, seller_id=ctx.seller_id, product_id=product_id, status=status, name=name
    )
    return {
        "products": [_product_to_dict(p) for p in products],
        "total": len(products),
    }


def _handle_update_product(ctx: ToolContext, arguments: dict) -> dict:
    product_id = parse_pk(arguments["id"], "products")
    fields = {k: v for k, v in arguments.items() if k != "id"}
    product = update_product(ctx.db, seller_id=ctx.seller_id, product_id=product_id, **fields)
    return _product_to_dict(product)


def _handle_delete_product(ctx: ToolContext, arguments: dict) -> dict:
    product_id = parse_pk(arguments["id"], "products")
    product = delete_product(ctx.db, seller_id=ctx.seller_id, product_id=product_id)
    return _product_to_dict(product)


def _product_to_dict(product) -> dict:
    return {
        "id": to_display_id("products", product.id),
        "name": product.name,
        "price": product.price,
        "status": product.status.value,
        "created_at": product.created_at.isoformat(),
        "updated_at": product.updated_at.isoformat(),
    }


_TOOL_HANDLERS = {
    "search_guide": _handle_search_guide,
    "create_product": _handle_create_product,
    "list_products": _handle_list_products,
    "update_product": _handle_update_product,
    "delete_product": _handle_delete_product,
}

import os
import httpx
from langchain_core.tools import tool
from pydantic import BaseModel, Field

JAVA_BACKEND = os.getenv("JAVA_BACKEND_URL", "http://localhost:8080")


def _get(path: str, **params) -> dict:
    url = f"{JAVA_BACKEND}{path}"
    params = {k: v for k, v in params.items() if v is not None}
    with httpx.Client(timeout=10) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()["data"]


class OrderSearchArgs(BaseModel):
    order_no: str | None = Field(default=None, description="订单号")
    user_id: int | None = Field(default=None, description="用户ID")
    order_status: str | None = Field(default=None, description="订单状态")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=OrderSearchArgs)
def search_orders(order_no: str | None = None, user_id: int | None = None,
                  order_status: str | None = None, page_num: int = 1, page_size: int = 10) -> dict:
    """查询订单列表，按订单号、用户ID、状态筛选。"""
    if order_no:
        return _get(f"/api/orders/{order_no}")
    if order_status:
        return {"rows": _get(f"/api/orders/status/{order_status}"), "total": 0, "page_num": 1, "page_size": 20}
    if user_id:
        return {"rows": _get(f"/api/orders", user_id=user_id), "total": 0, "page_num": 1, "page_size": 20}
    return {"rows": _get("/api/orders", user_id=0), "total": 0, "page_num": 1, "page_size": 20}


class ProductSearchArgs(BaseModel):
    name: str | None = Field(default=None, description="商品名称关键词")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=ProductSearchArgs)
def search_products(name: str | None = None, page_num: int = 1, page_size: int = 10) -> dict:
    """查询商品列表，按名称关键词搜索。"""
    rows = _get("/api/products", keyword=name or "")
    return {"total": len(rows), "page_num": 1, "page_size": len(rows), "rows": rows}


class UserSearchArgs(BaseModel):
    keyword: str | None = Field(default=None, description="用户名/昵称/手机号关键词")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=UserSearchArgs)
def search_users(keyword: str | None = None, page_num: int = 1, page_size: int = 10) -> dict:
    """查询用户列表，按用户名/昵称/手机号搜索。"""
    rows = _get("/api/users", keyword=keyword or "")
    return {"total": len(rows), "page_num": 1, "page_size": len(rows), "rows": rows}


class AfterSaleSearchArgs(BaseModel):
    after_sale_no: str | None = Field(default=None, description="售后单号")
    after_sale_status: str | None = Field(default=None, description="售后状态")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=AfterSaleSearchArgs)
def search_after_sales(after_sale_no: str | None = None, after_sale_status: str | None = None,
                       page_num: int = 1, page_size: int = 10) -> dict:
    """查询售后单列表。"""
    return {"total": 0, "page_num": 1, "page_size": 10, "rows": [],
            "message": "售后功能需扩展 Java 后端，当前暂无数据"}


@tool
def get_analytics() -> dict:
    """获取运营数据概览：用户数、商品数、订单数、今日销售额。"""
    return _get("/api/analytics/summary")


ADMIN_TOOLS = [search_orders, search_products, search_users, search_after_sales, get_analytics]
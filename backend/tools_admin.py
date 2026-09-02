import os
import pymysql
from langchain_core.tools import tool
from pydantic import BaseModel, Field


def _get_conn():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "medicine"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


# ==================== 订单工具 ====================

class OrderSearchArgs(BaseModel):
    order_no: str | None = Field(default=None, description="订单号")
    order_status: str | None = Field(default=None, description="订单状态: pending/paid/shipped/completed/cancelled")
    receiver_name: str | None = Field(default=None, description="收货人姓名")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=OrderSearchArgs)
def search_orders(order_no: str | None = None, order_status: str | None = None,
                  receiver_name: str | None = None, page_num: int = 1, page_size: int = 10) -> dict:
    """查询订单列表，支持按订单号、状态、收货人筛选。"""
    conn = _get_conn()
    try:
        conditions = ["is_delete = 0"]
        params = []
        if order_no:
            conditions.append("order_no = %s")
            params.append(order_no)
        if order_status:
            conditions.append("order_status = %s")
            params.append(order_status)
        if receiver_name:
            conditions.append("receiver_name LIKE %s")
            params.append(f"%{receiver_name}%")
        where = " AND ".join(conditions)
        offset = (page_num - 1) * page_size
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) as total FROM `order` WHERE {where}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT id, order_no, order_status, total_amount, receiver_name, receiver_phone, "
                f"create_time FROM `order` WHERE {where} ORDER BY create_time DESC LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            rows = cur.fetchall()
        return {"total": total, "page_num": page_num, "page_size": page_size, "rows": rows}
    finally:
        conn.close()


# ==================== 商品工具 ====================

class ProductSearchArgs(BaseModel):
    name: str | None = Field(default=None, description="商品名称关键词")
    category_id: int | None = Field(default=None, description="分类ID")
    status: int | None = Field(default=None, description="状态: 1上架 0下架")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=ProductSearchArgs)
def search_products(name: str | None = None, category_id: int | None = None,
                    status: int | None = None, page_num: int = 1, page_size: int = 10) -> dict:
    """查询商品列表，支持按名称、分类、状态筛选。"""
    conn = _get_conn()
    try:
        conditions = ["is_delete = 0"]
        params = []
        if name:
            conditions.append("name LIKE %s")
            params.append(f"%{name}%")
        if category_id is not None:
            conditions.append("category_id = %s")
            params.append(category_id)
        if status is not None:
            conditions.append("status = %s")
            params.append(status)
        where = " AND ".join(conditions)
        offset = (page_num - 1) * page_size
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) as total FROM product WHERE {where}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT id, name, price, stock, status, category_id, create_time "
                f"FROM product WHERE {where} ORDER BY create_time DESC LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            rows = cur.fetchall()
        return {"total": total, "page_num": page_num, "page_size": page_size, "rows": rows}
    finally:
        conn.close()


# ==================== 用户工具 ====================

class UserSearchArgs(BaseModel):
    username: str | None = Field(default=None, description="用户名")
    nickname: str | None = Field(default=None, description="昵称")
    status: int | None = Field(default=None, description="状态: 1启用 0禁用")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=UserSearchArgs)
def search_users(username: str | None = None, nickname: str | None = None,
                 status: int | None = None, page_num: int = 1, page_size: int = 10) -> dict:
    """查询用户列表，支持按用户名、昵称、状态筛选。"""
    conn = _get_conn()
    try:
        conditions = ["is_delete = 0"]
        params = []
        if username:
            conditions.append("username LIKE %s")
            params.append(f"%{username}%")
        if nickname:
            conditions.append("nickname LIKE %s")
            params.append(f"%{nickname}%")
        if status is not None:
            conditions.append("status = %s")
            params.append(status)
        where = " AND ".join(conditions)
        offset = (page_num - 1) * page_size
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) as total FROM user WHERE {where}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT id, username, nickname, phone, status, create_time "
                f"FROM user WHERE {where} ORDER BY create_time DESC LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            rows = cur.fetchall()
        return {"total": total, "page_num": page_num, "page_size": page_size, "rows": rows}
    finally:
        conn.close()


# ==================== 售后工具 ====================

class AfterSaleSearchArgs(BaseModel):
    after_sale_no: str | None = Field(default=None, description="售后单号")
    after_sale_status: str | None = Field(default=None, description="售后状态: PENDING/APPROVED/REJECTED/COMPLETED")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=AfterSaleSearchArgs)
def search_after_sales(after_sale_no: str | None = None, after_sale_status: str | None = None,
                       page_num: int = 1, page_size: int = 10) -> dict:
    """查询售后单列表，支持按单号、状态筛选。"""
    conn = _get_conn()
    try:
        conditions = ["is_deleted = 0"]
        params = []
        if after_sale_no:
            conditions.append("after_sale_no = %s")
            params.append(after_sale_no)
        if after_sale_status:
            conditions.append("after_sale_status = %s")
            params.append(after_sale_status)
        where = " AND ".join(conditions)
        offset = (page_num - 1) * page_size
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) as total FROM mall_after_sale WHERE {where}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT id, after_sale_no, order_no, after_sale_type, after_sale_status, "
                f"refund_amount, apply_reason, apply_time FROM mall_after_sale "
                f"WHERE {where} ORDER BY apply_time DESC LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            rows = cur.fetchall()
        return {"total": total, "page_num": page_num, "page_size": page_size, "rows": rows}
    finally:
        conn.close()


# ==================== 数据分析工具 ====================

@tool
def get_analytics() -> dict:
    """获取运营数据概览：订单总数、销售额、用户数、商品数。"""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total_orders, COALESCE(SUM(total_amount), 0) as total_sales FROM `order` WHERE is_delete = 0")
            order_stats = cur.fetchone()
            cur.execute("SELECT COUNT(*) as total_users FROM user WHERE is_delete = 0")
            user_stats = cur.fetchone()
            cur.execute("SELECT COUNT(*) as total_products FROM product WHERE is_delete = 0")
            product_stats = cur.fetchone()
        return {
            "total_orders": order_stats["total_orders"],
            "total_sales": float(order_stats["total_sales"]),
            "total_users": user_stats["total_users"],
            "total_products": product_stats["total_products"],
        }
    finally:
        conn.close()


ADMIN_TOOLS = [search_orders, search_products, search_users, search_after_sales, get_analytics]
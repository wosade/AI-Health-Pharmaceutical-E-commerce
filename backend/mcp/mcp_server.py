import os
import pymysql
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("药智通 MCP Server")


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


@mcp.tool()
def query_drug(drug_name: str) -> str:
    """查询药品信息，返回药品名称、价格、库存、描述。

    Args:
        drug_name: 药品名称关键词
    """
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, price, stock, description FROM product "
                "WHERE name LIKE %s AND is_delete = 0 AND status = 1 LIMIT 5",
                (f"%{drug_name}%",)
            )
            rows = cur.fetchall()
        if not rows:
            return f"未找到与 '{drug_name}' 相关的药品"
        result = [f"共找到 {len(rows)} 个药品："]
        for r in rows:
            result.append(f"- {r['name']} | 价格: ¥{r['price']} | 库存: {r['stock']} | {r['description'] or ''}")
        return "\n".join(result)
    finally:
        conn.close()


@mcp.tool()
def query_order(order_no: str) -> str:
    """查询订单详情，返回订单状态、金额、收货信息。

    Args:
        order_no: 订单编号
    """
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT order_no, order_status, total_amount, receiver_name, receiver_phone, "
                "create_time FROM `order` WHERE order_no = %s AND is_delete = 0",
                (order_no,)
            )
            order = cur.fetchone()
        if not order:
            return f"订单 {order_no} 不存在"
        return (
            f"订单号: {order['order_no']}\n"
            f"状态: {order['order_status']}\n"
            f"金额: ¥{order['total_amount']}\n"
            f"收货人: {order['receiver_name']} ({order['receiver_phone']})\n"
            f"创建时间: {order['create_time']}"
        )
    finally:
        conn.close()


@mcp.resource("drugs://popular")
def get_popular_drugs() -> str:
    """获取热门药品列表。"""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name, price FROM product WHERE is_delete = 0 AND status = 1 "
                "ORDER BY create_time DESC LIMIT 10"
            )
            rows = cur.fetchall()
        return "\n".join(f"- {r['name']}: ¥{r['price']}" for r in rows)
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()
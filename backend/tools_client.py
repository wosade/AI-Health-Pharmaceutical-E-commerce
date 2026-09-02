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


# ==================== 商品搜索 ====================

class ProductSearchArgs(BaseModel):
    keyword: str | None = Field(default=None, description="搜索关键词")
    category_name: str | None = Field(default=None, description="分类名称")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=ProductSearchArgs)
def search_client_products(keyword: str | None = None, category_name: str | None = None,
                           page_num: int = 1, page_size: int = 10) -> dict:
    """搜索客户端商品。用户想找药、按用途选商品时调用。"""
    conn = _get_conn()
    try:
        conditions = ["p.is_delete = 0", "p.status = 1"]
        params = []
        if keyword:
            conditions.append("(p.name LIKE %s OR p.brand LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if category_name:
            conditions.append("c.name = %s")
            params.append(category_name)
        where = " AND ".join(conditions)
        offset = (page_num - 1) * page_size
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) as total FROM product p "
                f"LEFT JOIN category c ON p.category_id = c.id WHERE {where}", params
            )
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT p.id, p.name, p.price, p.stock, p.image_url, p.description "
                f"FROM product p LEFT JOIN category c ON p.category_id = c.id "
                f"WHERE {where} ORDER BY p.create_time DESC LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            rows = cur.fetchall()
        return {"total": total, "page_num": page_num, "page_size": page_size, "rows": rows}
    finally:
        conn.close()


# ==================== 订单查询 ====================

class OrderDetailArgs(BaseModel):
    order_no: str = Field(description="订单编号")


@tool(args_schema=OrderDetailArgs)
def get_client_order(order_no: str) -> dict:
    """查询客户端用户的订单详情。"""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, order_no, order_status, total_amount, pay_amount, receiver_name, "
                "receiver_phone, receiver_address, create_time, pay_time "
                "FROM `order` WHERE order_no = %s AND is_delete = 0", (order_no,)
            )
            order = cur.fetchone()
            if not order:
                return {"error": "订单不存在"}
            cur.execute(
                "SELECT product_name, product_price, quantity, product_image "
                "FROM order_item WHERE order_no = %s", (order_no,)
            )
            items = cur.fetchall()
            order["items"] = items
            return order
    finally:
        conn.close()


# ==================== 问诊卡工具 ====================

class SendQuestionnaireArgs(BaseModel):
    questions: list[str] = Field(description="追问问题列表，最多5个")
    title: str = Field(default="补充问诊信息", description="问诊卡标题")


@tool(args_schema=SendQuestionnaireArgs)
def send_questionnaire_card(questions: list[str], title: str = "补充问诊信息") -> dict:
    """发送问诊问卷卡，当需要补充症状信息时调用。"""
    return {
        "card_type": "questionnaire",
        "title": title,
        "questions": questions[:5],
        "message": "请用户填写以下问诊信息"
    }


# ==================== 处方确认卡 ====================

class SendPrescriptionArgs(BaseModel):
    drug_name: str = Field(description="推荐药品名称")
    reason: str = Field(description="推荐理由")
    price: float = Field(default=0, description="参考价格")


@tool(args_schema=SendPrescriptionArgs)
def send_prescription_card(drug_name: str, reason: str, price: float = 0) -> dict:
    """发送药品推荐确认卡，当诊断完成需要推荐药品时调用。"""
    return {
        "card_type": "prescription",
        "drug_name": drug_name,
        "reason": reason,
        "price": price,
        "message": f"推荐药品：{drug_name}，{reason}"
    }


# ==================== 导航工具 ====================

@tool
def open_user_patient_list() -> dict:
    """打开就诊人列表，让用户选择就诊人。"""
    return {"card_type": "patient_list", "message": "请选择就诊人"}


@tool
def open_user_order_list() -> dict:
    """打开用户订单列表，让用户选择订单。"""
    return {"card_type": "order_list", "message": "请选择订单"}


CLIENT_TOOLS = [
    search_client_products,
    get_client_order,
    send_questionnaire_card,
    send_prescription_card,
    open_user_patient_list,
    open_user_order_list,
]
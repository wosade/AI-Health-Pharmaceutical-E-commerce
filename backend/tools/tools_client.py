import os
import httpx
from langchain_core.tools import tool
from pydantic import BaseModel, Field

JAVA_BACKEND = os.getenv("JAVA_BACKEND_URL", "http://localhost:8080")


def _get(path: str, **params) -> dict | list:
    url = f"{JAVA_BACKEND}{path}"
    params = {k: v for k, v in params.items() if v is not None}
    with httpx.Client(timeout=10) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()["data"]


class ProductSearchArgs(BaseModel):
    keyword: str | None = Field(default=None, description="搜索关键词")
    page_num: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")


@tool(args_schema=ProductSearchArgs)
def search_client_products(keyword: str | None = None,
                           page_num: int = 1, page_size: int = 10) -> dict:
    """搜索客户端商品。用户想找药、按症状/用途选商品时调用。"""
    rows = _get("/api/products", keyword=keyword or "")
    return {"total": len(rows), "page_num": 1, "page_size": len(rows), "rows": rows}


class OrderDetailArgs(BaseModel):
    order_no: str = Field(description="订单编号")


@tool(args_schema=OrderDetailArgs)
def get_client_order(order_no: str) -> dict:
    """查询客户端用户的订单详情。"""
    return _get(f"/api/orders/{order_no}")


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
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from config.config import create_llm
from core.state import AgentState
from tools.tools_client import search_client_products, get_client_order, open_user_order_list

SERVICE_SYSTEM_PROMPT = """你是药智通客户端客服 AI，帮助用户处理商品咨询、订单查询、售后问题。

你可以使用以下工具：
- search_client_products: 搜索商品，用户想找药、按症状找药时主动调用
- get_client_order: 查询订单详情
- open_user_order_list: 打开订单列表让用户选择

核心原则：
1. 用户说症状/想买药时，主动搜索商品，不要反问用户
2. 找到商品后直接展示，让用户选择
3. 用亲切友好的语气回复"""


def service_agent(state: AgentState) -> dict:
    """客户端客服 Agent：处理商品咨询、订单查询。"""
    llm = create_llm()
    agent = create_agent(
        model=llm,
        tools=[search_client_products, get_client_order, open_user_order_list],
        system_prompt=SERVICE_SYSTEM_PROMPT,
    )
    messages = list(state.get("messages", []))
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SERVICE_SYSTEM_PROMPT)] + messages

    result = agent.invoke({"messages": messages})
    return {"messages": result["messages"]}
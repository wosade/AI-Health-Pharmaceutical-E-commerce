from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from config import create_llm
from state import AgentState
from tools_admin import ADMIN_TOOLS

ADMIN_SYSTEM_PROMPT = """你是药智通管理后台的 AI 助手，帮助运营人员管理药品电商平台。

你可以使用以下工具：
- search_orders: 查询订单
- search_products: 查询商品
- search_users: 查询用户
- search_after_sales: 查询售后单
- get_analytics: 查看运营数据概览

请用简洁专业的中文回复，必要时使用表格展示数据。"""


def admin_agent(state: AgentState) -> dict:
    """管理端 Agent 节点：加载管理端工具，执行对话。"""
    llm = create_llm()
    agent = create_agent(
        model=llm,
        tools=ADMIN_TOOLS,
        system_prompt=ADMIN_SYSTEM_PROMPT,
    )
    messages = list(state.get("messages", []))
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=ADMIN_SYSTEM_PROMPT)] + messages

    result = agent.invoke({"messages": messages})
    return {"messages": result["messages"]}
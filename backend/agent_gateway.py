from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from config import create_llm
from state import AgentState

GATEWAY_SYSTEM_PROMPT = """你是药智通客户端 AI 助手的意图路由节点。

分析用户的问题，判断应该交给哪个 Agent 处理：
- service_agent: 商品咨询、订单查询、售后服务、优惠券等电商相关
- medical_agent: 症状描述、疾病咨询、用药建议、健康问题等医疗相关

请只输出 JSON: {"route_target": "service_agent"} 或 {"route_target": "medical_agent"}"""


class GatewayOutput(BaseModel):
    route_target: str = Field(description="路由目标: service_agent 或 medical_agent")


def gateway_router(state: AgentState) -> dict:
    """客户端路由节点：分析用户意图，决定走 service 还是 medical。"""
    llm = create_llm(temperature=0)
    messages = state.get("messages", [])
    prompt = [SystemMessage(content=GATEWAY_SYSTEM_PROMPT)] + list(messages)

    agent = create_agent(
        model=llm,
        tools=[],
        system_prompt=GATEWAY_SYSTEM_PROMPT,
        response_format={"type": "json_object"},
    )
    result = agent.invoke({"messages": prompt})
    last_msg = result["messages"][-1]
    import json
    try:
        parsed = json.loads(last_msg.content)
        route_target = parsed.get("route_target", "service_agent")
        if route_target not in ("service_agent", "medical_agent"):
            route_target = "service_agent"
    except (json.JSONDecodeError, AttributeError):
        route_target = "service_agent"

    return {"routing": {"route_target": route_target}}
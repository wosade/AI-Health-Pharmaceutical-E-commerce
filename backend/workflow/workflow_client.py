from langgraph.constants import END, START
from langgraph.graph import StateGraph
from core.state import AgentState
from agent.agent_gateway import gateway_router
from agent.agent_service import service_agent
from agent.agent_medical import medical_agent


def _route_from_gateway(state: AgentState) -> str:
    """根据 gateway 路由结果分发到对应 Agent。"""
    routing = state.get("routing", {})
    target = routing.get("route_target", "service_agent")
    if target == "medical_agent":
        return "medical_agent"
    return "service_agent"


def build_client_graph():
    """构建客户端多 Agent LangGraph 图。"""
    graph = StateGraph(AgentState)

    graph.add_node("gateway_router", gateway_router)
    graph.add_node("service_agent", service_agent)
    graph.add_node("medical_agent", medical_agent)

    graph.add_edge(START, "gateway_router")
    graph.add_conditional_edges(
        "gateway_router",
        _route_from_gateway,
        {"service_agent": "service_agent", "medical_agent": "medical_agent"},
    )
    graph.add_edge("service_agent", END)
    graph.add_edge("medical_agent", END)

    return graph.compile()
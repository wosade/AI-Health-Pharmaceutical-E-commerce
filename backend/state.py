from typing import TypedDict
from langgraph.graph import MessagesState


class AgentState(MessagesState, total=False):
    """Agent 工作流共享状态。"""
    conversation_uuid: str
    assistant_message_uuid: str
    current_question: str
    routing: dict  # client 端路由结果 {"route_target": "service_agent" | "medical_agent"}
    result: str    # 最终输出文本
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from core.state import AgentState
from agent.agent_admin import admin_agent
from workflow.workflow_client import build_client_graph
from core.stream import astream_to_sse

router = APIRouter(prefix="/api/agent")


@router.post("/admin/chat")
async def admin_chat(request: Request):
    """管理端 AI 助手对话接口（非流式）。"""
    body = await request.json()
    question = body.get("question", "")
    conversation_uuid = body.get("conversation_uuid", str(uuid.uuid4()))

    state: AgentState = {
        "messages": [HumanMessage(content=question)],
        "conversation_uuid": conversation_uuid,
    }
    result = admin_agent(state)
    last_msg = result["messages"][-1]
    return {"answer": last_msg.content, "conversation_uuid": conversation_uuid}


@router.post("/client/chat")
async def client_chat(request: Request):
    """客户端 AI 助手对话接口（SSE 流式）。"""
    body = await request.json()
    question = body.get("question", "")
    conversation_uuid = body.get("conversation_uuid", str(uuid.uuid4()))

    state: AgentState = {
        "messages": [HumanMessage(content=question)],
        "conversation_uuid": conversation_uuid,
    }

    client_graph = build_client_graph()
    return StreamingResponse(
        astream_to_sse(client_graph, state, conversation_uuid),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
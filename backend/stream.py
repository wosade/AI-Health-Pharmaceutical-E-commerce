import json
import asyncio
from typing import AsyncIterable


async def astream_to_sse(graph, state: dict, conversation_uuid: str) -> AsyncIterable[str]:
    """将 LangGraph astream 输出转为 SSE 事件流。

    事件格式：
    - {"type": "thinking", "content": "..."}  - 思考过程
    - {"type": "answer", "content": "..."}     - 回答内容
    - {"type": "done", "conversation_uuid": "..."} - 结束
    - {"type": "error", "message": "..."}      - 错误
    """
    try:
        async for event in graph.astream(state, stream_mode=["messages", "values"]):
            for _, stream_data in event.items():
                if isinstance(stream_data, tuple):
                    msg, metadata = stream_data
                    if metadata.get("langgraph_node") == "gateway_router":
                        continue  # 路由节点不输出
                    content = msg.content if hasattr(msg, "content") else str(msg)
                    if isinstance(content, str) and content.strip():
                        yield f"data: {json.dumps({'type': 'answer', 'content': content}, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.01)

        yield f"data: {json.dumps({'type': 'done', 'conversation_uuid': conversation_uuid}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
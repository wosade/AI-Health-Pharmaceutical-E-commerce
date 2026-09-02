import os
from langchain_openai import ChatOpenAI


def create_llm(model_name: str | None = None, temperature: float = 0.1) -> ChatOpenAI:
    """创建阿里云百炼 LLM 客户端（兼容 OpenAI 协议）。"""
    return ChatOpenAI(
        model=model_name or os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
        api_key=os.getenv("DASHSCOPE_API_KEY", ""),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=temperature,
    )
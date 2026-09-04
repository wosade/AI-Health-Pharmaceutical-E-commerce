import os
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from pymilvus import MilvusClient


def _get_milvus_client():
    return MilvusClient(
        uri=f"http://{os.getenv('MILVUS_HOST', 'localhost')}:{os.getenv('MILVUS_PORT', '19530')}"
    )


def _get_embedding(text: str) -> list[float]:
    """使用阿里云 embedding 将文本向量化。"""
    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-v3",
        api_key=os.getenv("DASHSCOPE_API_KEY", ""),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    return embeddings.embed_query(text)


class MedicineSearchArgs(BaseModel):
    query: str = Field(description="搜索关键词，如'感冒药'、'布洛芬用法用量'")


@tool(args_schema=MedicineSearchArgs)
def search_medicine_knowledge(query: str) -> str:
    """搜索药品知识库，返回相关的药品说明、用法用量、禁忌等知识。"""
    client = _get_milvus_client()
    collection = os.getenv("MILVUS_COLLECTION", "medicine_knowledge")
    embedding = _get_embedding(query)

    results = client.search(
        collection_name=collection,
        data=[embedding],
        limit=3,
        output_fields=["content", "title"],
        search_params={"metric_type": "COSINE", "params": {"nprobe": 10}},
    )

    if not results or not results[0]:
        return "未找到相关知识"

    chunks = []
    for hit in results[0]:
        entity = hit.get("entity", {})
        title = entity.get("title", "未知")
        content = entity.get("content", "")
        chunks.append(f"【{title}】\n{content[:500]}")

    return "\n\n---\n\n".join(chunks)


class SymptomSearchArgs(BaseModel):
    symptom: str = Field(description="症状关键词，如'头痛'、'咳嗽'")


@tool(args_schema=SymptomSearchArgs)
def search_symptom_knowledge(symptom: str) -> str:
    """搜索症状相关知识，返回可能关联的疾病和用药建议。"""
    client = _get_milvus_client()
    collection = os.getenv("MILVUS_COLLECTION", "medicine_knowledge")
    embedding = _get_embedding(f"症状 {symptom} 疾病 用药")

    results = client.search(
        collection_name=collection,
        data=[embedding],
        limit=3,
        output_fields=["content", "title"],
        search_params={"metric_type": "COSINE", "params": {"nprobe": 10}},
    )

    if not results or not results[0]:
        return "未找到相关症状知识"

    chunks = []
    for hit in results[0]:
        entity = hit.get("entity", {})
        title = entity.get("title", "未知")
        content = entity.get("content", "")
        chunks.append(f"【{title}】\n{content[:500]}")

    return "\n\n---\n\n".join(chunks)


RAG_TOOLS = [search_medicine_knowledge, search_symptom_knowledge]
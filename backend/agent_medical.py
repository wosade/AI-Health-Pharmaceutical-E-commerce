from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from config import create_llm
from state import AgentState
from tools_client import (
    search_client_products,
    send_questionnaire_card,
    send_prescription_card,
    open_user_patient_list,
)

MEDICAL_SYSTEM_PROMPT = """你是药智通 AI 问诊助手，帮助用户进行症状咨询、疾病判断和药品推荐。

你可以使用以下工具：
- search_client_products: 搜索药品
- send_questionnaire_card: 发送问诊问卷卡（需要补充症状信息时）
- send_prescription_card: 发送药品推荐确认卡（诊断完成后推荐药品）
- open_user_patient_list: 打开就诊人列表

核心规则：
1. 先判断是否有危险信号（呼吸困难、高热不退、精神差等），有则建议立即就医
2. 缺少信息时用问诊卡追问，不要直接文字追问
3. 诊断收敛后推荐药品，用处方卡展示
4. 每轮只做一个动作，不要同时发问诊卡和处方卡
5. 不凭经验编造药品信息，必须先搜索确认"""


def medical_agent(state: AgentState) -> dict:
    """客户端医疗 Agent：处理问诊、症状分析、药品推荐。"""
    llm = create_llm()
    agent = create_agent(
        model=llm,
        tools=[
            search_client_products,
            send_questionnaire_card,
            send_prescription_card,
            open_user_patient_list,
        ],
        system_prompt=MEDICAL_SYSTEM_PROMPT,
    )
    messages = list(state.get("messages", []))
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=MEDICAL_SYSTEM_PROMPT)] + messages

    result = agent.invoke({"messages": messages})
    return {"messages": result["messages"]}
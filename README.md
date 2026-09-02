# 药智通 AI Agent (简化版)

基于 LangGraph + FastAPI + Vue 3 的医药电商 AI 助手系统。

## 项目结构

```
medicine-ai-simple/
├── backend/                  # Python 后端
│   ├── main.py               # FastAPI 入口
│   ├── config.py             # 阿里云百炼 LLM 配置
│   ├── state.py              # Agent 状态定义
│   ├── tools_admin.py        # 管理端工具（订单/商品/用户/售后/分析）
│   ├── tools_client.py       # 客户端工具（商品/订单/问诊卡/处方卡/导航）
│   ├── agent_admin.py        # 管理端 Agent
│   ├── agent_gateway.py      # 客户端路由节点
│   ├── agent_service.py      # 客服 Agent
│   ├── agent_medical.py      # 医疗 Agent
│   ├── workflow_client.py    # 客户端 LangGraph 图编排
│   ├── stream.py             # SSE 流式输出
│   ├── routes.py             # API 路由
│   ├── rag.py                # RAG 知识库检索（Milvus）
│   ├── skills.py             # Skill 系统（发现/加载）
│   ├── mcp_server.py         # MCP Server
│   ├── prompts/              # 系统提示词
│   │   ├── admin.md
│   │   ├── gateway.md
│   │   ├── service.md
│   │   └── medical.md
│   └── skills/               # Skill 定义
│       ├── diagnosis/        # 问诊 skill
│       ├── product_consultation/  # 商品咨询 skill
│       └── order_consultation/    # 订单咨询 skill
│
└── frontend/                 # Vue 前端
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── App.vue
        ├── api.js
        └── components/
            └── ChatBox.vue
```

## 核心架构

```
用户问题 → gateway_router（意图识别）
              ├── service_agent（商品/订单/售后）
              └── medical_agent（问诊/症状/药品推荐）
```

## 快速启动

### 1. 环境准备

需要以下服务：
- MySQL（业务数据）
- Redis（缓存）
- Milvus（向量检索，RAG 用）
- Neo4j（医学知识图谱，可选）

### 2. 后端

```bash
cd backend
cp .env.example .env
# 编辑 .env 填入阿里云 API Key 和数据库连接信息
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

### 4. MCP Server（可选）

```bash
cd backend
python mcp_server.py
```

## API 接口

| 接口 | 方法 | 说明 |
|---|---|---|
| /api/agent/admin/chat | POST | 管理端对话（非流式） |
| /api/agent/client/chat | POST | 客户端对话（SSE 流式） |
| /health | GET | 健康检查 |

## 技术栈

- **后端**: FastAPI + LangChain + LangGraph
- **LLM**: 阿里云百炼 DashScope
- **数据库**: MySQL + Redis + Milvus + Neo4j
- **前端**: Vue 3 + Vite
- **协议**: SSE（流式）+ MCP（工具暴露）
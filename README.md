# 药智通 AI Agent (简化版)

基于 LangGraph + FastAPI + Spring Boot + Vue 3 的医药电商 AI 助手系统。

## 架构

```
用户 → Vue 前端
         ↓
    Python Agent (AI 层)
    ├── gateway_router（意图识别）
    │     ├── service_agent（商品/订单/售后）
    │     └── medical_agent（问诊/症状/药品推荐）
    ├── RAG 知识库（Milvus 向量检索）
    ├── Skill 系统（问诊/商品/订单流程）
    └── MCP Server（工具暴露）
         ↓  HTTP API 调用
    Java Spring Boot（业务层）
    └── Controller → Service → Mapper → MySQL
```

**分层设计**：Python 管 AI，Java 管业务，各司其职。

## 项目结构

```
medicine-ai-simple/
├── backend/                     # Python AI Agent
│   ├── main.py                  # FastAPI 入口
│   ├── config.py                # 阿里云百炼 LLM
│   ├── state.py                 # Agent 状态
│   ├── tools_admin.py           # 管理端工具（调 Java API）
│   ├── tools_client.py          # 客户端工具（调 Java API + 问诊卡/处方卡）
│   ├── agent_admin.py           # 管理端 Agent
│   ├── agent_gateway.py         # 意图路由
│   ├── agent_service.py         # 客服 Agent
│   ├── agent_medical.py         # 医疗 Agent
│   ├── workflow_client.py       # LangGraph 图编排
│   ├── stream.py                # SSE 流式
│   ├── routes.py                # API 路由
│   ├── rag.py                   # RAG 知识库检索（Milvus）
│   ├── skills.py                # Skill 系统
│   ├── mcp_server.py            # MCP Server
│   ├── prompts/                 # 4 个 Agent 提示词
│   ├── skills/                  # 3 个 Skill 定义
│   ├── .env.example
│   └── requirements.txt
│
├── java-backend/                # Java 业务后端
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/medicine/
│       │   ├── Application.java
│       │   ├── common/Result.java
│       │   ├── entity/          # Product/Order/User/Category
│       │   ├── mapper/          # MyBatis-Plus BaseMapper
│       │   ├── service/         # 业务逻辑
│       │   └── controller/      # REST 接口
│       └── resources/
│           └── application.yml
│
└── frontend/                    # Vue 3 前端
    ├── package.json / vite.config.js
    └── src/
        ├── App.vue / main.js / api.js
        └── ChatBox.vue          # 流式对话组件
```

## 快速启动

### 1. 环境准备

需要以下服务：
- MySQL（业务数据，导入 `database/MySQL/medicine.sql`）
- Redis（可选，缓存）
- Milvus（可选，RAG 向量检索）
- JDK 17 + Maven（Java 后端）
- Python 3.11+（AI 后端）

### 2. Java 业务后端（端口 8080）

```bash
cd java-backend
# 编辑 application.yml 或设置环境变量 MYSQL_HOST/MYSQL_USER/MYSQL_PASSWORD
mvn spring-boot:run
```

### 3. Python AI 后端（端口 8000）

```bash
cd backend
cp .env.example .env
# 编辑 .env 填入 DASHSCOPE_API_KEY 和 JAVA_BACKEND_URL
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Vue 前端（端口 5173）

```bash
cd frontend
npm install && npm run dev
```

### 5. MCP Server（可选）

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

### Java 后端接口

| 接口 | 方法 | 说明 |
|---|---|---|
| /api/products?keyword=xxx | GET | 商品搜索 |
| /api/products/{id} | GET | 商品详情 |
| /api/orders?userId=xxx | GET | 订单列表 |
| /api/orders/{orderNo} | GET | 订单详情 |
| /api/orders/status/{status} | GET | 按状态查订单 |
| /api/users?keyword=xxx | GET | 用户搜索 |
| /api/users/{id} | GET | 用户详情 |
| /api/analytics/summary | GET | 数据概览 |

## 技术栈

- **AI Agent**: FastAPI + LangChain + LangGraph
- **业务后端**: Spring Boot 3 + MyBatis-Plus + MySQL
- **LLM**: 阿里云百炼 DashScope
- **向量检索**: Milvus（RAG）
- **前端**: Vue 3 + Vite
- **协议**: SSE（流式）+ MCP（工具暴露）
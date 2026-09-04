from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as agent_router
from api.auth import router as auth_router
from api.business import router as business_router
from api.knowledge_base import router as knowledge_base_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("服务启动中...")
    yield
    print("服务关闭中...")


app = FastAPI(title="药智通 AI Agent", version="2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(business_router)
app.include_router(knowledge_base_router)


@app.get("/health")
def health():
    return {"status": "ok"}
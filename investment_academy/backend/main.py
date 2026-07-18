"""投资学院 — FastAPI 后端入口"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
ACADEMY_ROOT = BACKEND_DIR.parent
if str(ACADEMY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACADEMY_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from backend.routers import content, quiz, progress, market, sandbox, user, knowledge, spas

app = FastAPI(
    title="投资学院 API",
    description="Investment Academy Backend — 本地投资学习系统",
    version="0.1.0",
)

# CORS — 允许 Vue devServer 和任何本地访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(content.router, tags=["内容系统"])
app.include_router(quiz.router, tags=["测验系统"])
app.include_router(progress.router, tags=["学习进度"])
app.include_router(market.router, tags=["市场数据"])
app.include_router(sandbox.router, tags=["交易沙盒"])
app.include_router(user.router, tags=["用户系统"])
app.include_router(knowledge.router, tags=["投资知识"])
app.include_router(spas.router, tags=["SPAS预测"])


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

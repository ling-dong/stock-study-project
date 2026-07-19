"""投资学院 — FastAPI 后端入口"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
ACADEMY_ROOT = BACKEND_DIR.parent
if str(ACADEMY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACADEMY_ROOT))

from dotenv import load_dotenv

# 从项目根目录加载 .env
_env_path = ACADEMY_ROOT.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from backend.routers import content, quiz, progress, market, sandbox, user, knowledge, spas, manual_analysis

app = FastAPI(
    title="投资学院 API",
    description="Investment Academy Backend — 本地投资学习系统",
    version="0.1.0",
)


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    """全局未捕获异常：记录日志并返回统一 500，不泄露内部堆栈"""
    import logging
    logging.getLogger("investment_academy").exception(
        "未处理的异常: %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "服务器内部错误，请稍后重试或查看日志"},
    )

# CORS — 仅允许本地开发源，生产环境应进一步收紧
_cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
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
app.include_router(spas.router, tags=["SPAS自动信号"])
app.include_router(manual_analysis.router, tags=["手动指标分析"])


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

"""
鸟类识别系统 - FastAPI 应用入口
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from config import CORS_ORIGINS, UPLOAD_DIR, DATASET_DIR, TRAINING_OUTPUT_DIR
from database import engine, Base, check_redis_connection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动鸟类识别系统...")
    
    # 创建数据库表（如果不存在）
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表检查完成")
    
    # 检查 Redis 连接
    if check_redis_connection():
        logger.info("Redis 连接成功")
    else:
        logger.warning("Redis 连接失败，缓存功能将不可用")
    
    # 确保上传目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, "original"), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, "annotated"), exist_ok=True)
    logger.info("上传目录检查完成")
    
    # 确保数据集和训练目录存在
    os.makedirs(DATASET_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATASET_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(DATASET_DIR, "labels"), exist_ok=True)
    os.makedirs(TRAINING_OUTPUT_DIR, exist_ok=True)
    logger.info("数据集目录检查完成")
    
    yield
    
    # 关闭时执行
    logger.info("鸟类识别系统已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="鸟类识别系统 API",
    description="基于 YOLOv8 的鸟类图像识别系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 注册路由
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.recognize import router as recognize_router
from routers.records import router as records_router
from routers.admin import router as admin_router
from routers.dataset import router as dataset_router

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(recognize_router)
app.include_router(records_router)
app.include_router(admin_router)
app.include_router(dataset_router)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None
        }
    )


# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "鸟类识别系统运行正常"}


# 根路径
@app.get("/")
async def root():
    return {
        "message": "欢迎使用鸟类识别系统 API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

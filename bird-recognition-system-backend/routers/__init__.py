"""
routers 包初始化文件
"""
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.recognize import router as recognize_router
from routers.birds import router as birds_router
from routers.records import router as records_router
from routers.admin import router as admin_router

__all__ = [
    "auth_router", "user_router", "recognize_router",
    "birds_router", "records_router", "admin_router"
]

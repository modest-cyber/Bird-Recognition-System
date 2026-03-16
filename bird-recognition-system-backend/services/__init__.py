"""
services 包初始化文件
"""
from services.auth_service import AuthService
from services.recognize_service import RecognizeService
from services.admin_service import AdminService

__all__ = ["AuthService", "RecognizeService", "AdminService"]

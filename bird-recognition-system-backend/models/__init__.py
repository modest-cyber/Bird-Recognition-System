"""
models 包初始化文件
导出所有 ORM 模型
"""
from models.user import User
from models.record import Record

__all__ = ["User", "Record"]

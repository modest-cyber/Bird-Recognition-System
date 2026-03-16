"""
models 包初始化文件
导出所有 ORM 模型
"""
from models.user import User
from models.bird import Bird
from models.record import Record
from models.bird_region import BirdRegion

__all__ = ["User", "Bird", "Record", "BirdRegion"]

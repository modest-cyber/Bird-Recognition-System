"""
鸟类表 ORM 模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class Bird(Base):
    __tablename__ = "bird"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # 中文名
    latin_name = Column(String(100), nullable=True)  # 学名
    family = Column(String(100), nullable=True, index=True)  # 科目
    description = Column(Text, nullable=True)  # 特征描述
    image_url = Column(String(255), nullable=True)  # 示例图片路径
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联分布地区
    regions = relationship("BirdRegion", back_populates="bird", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bird(id={self.id}, name='{self.name}', family='{self.family}')>"

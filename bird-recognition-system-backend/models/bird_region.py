"""
鸟类分布地区表 ORM 模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class BirdRegion(Base):
    __tablename__ = "bird_region"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    bird_id = Column(Integer, ForeignKey("bird.id"), nullable=False, index=True)
    region = Column(String(100), nullable=False)  # 分布地区
    
    # 关联鸟类
    bird = relationship("Bird", back_populates="regions")
    
    def __repr__(self):
        return f"<BirdRegion(id={self.id}, bird_id={self.bird_id}, region='{self.region}')>"

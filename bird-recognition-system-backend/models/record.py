"""
识别记录表 ORM 模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class Record(Base):
    __tablename__ = "record"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    image_url = Column(String(255), nullable=False)  # 上传图片路径
    annotated_image_url = Column(String(255), nullable=True)  # 标注图片路径
    result_json = Column(JSON, nullable=False)  # YOLOv8 识别结果
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联用户
    user = relationship("User", back_populates="records")
    
    def __repr__(self):
        return f"<Record(id={self.id}, user_id={self.user_id})>"

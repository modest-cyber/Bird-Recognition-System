"""
鸟类相关 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BirdCreate(BaseModel):
    """新增鸟类请求模型"""
    name: str = Field(..., description="中文名")
    latin_name: Optional[str] = Field(None, description="学名")
    family: Optional[str] = Field(None, description="科目")
    description: Optional[str] = Field(None, description="特征描述")
    image_url: Optional[str] = Field(None, description="图片路径")
    regions: Optional[List[str]] = Field(None, description="分布地区列表")


class BirdUpdate(BaseModel):
    """修改鸟类请求模型（所有字段可选）"""
    name: Optional[str] = Field(None, description="中文名")
    latin_name: Optional[str] = Field(None, description="学名")
    family: Optional[str] = Field(None, description="科目")
    description: Optional[str] = Field(None, description="特征描述")
    image_url: Optional[str] = Field(None, description="图片路径")
    regions: Optional[List[str]] = Field(None, description="分布地区列表")


class BirdInfo(BaseModel):
    """鸟类列表项信息"""
    id: int
    name: str
    latin_name: Optional[str] = None
    family: Optional[str] = None
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class BirdDetail(BaseModel):
    """鸟类详情信息"""
    id: int
    name: str
    latin_name: Optional[str] = None
    family: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    regions: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class BirdListResponse(BaseModel):
    """鸟类列表响应模型"""
    list: List[BirdInfo]
    total: int
    page: int
    size: int

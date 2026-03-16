"""
识别记录相关 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class BirdDetection(BaseModel):
    """单个鸟类检测结果"""
    bird_id: Optional[int] = None
    bird_name: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]


class RecognizeResult(BaseModel):
    """识别结果响应模型"""
    record_id: int
    original_image_url: str
    annotated_image_url: str
    results: List[BirdDetection]


class RecordInfo(BaseModel):
    """历史记录项信息"""
    id: int
    image_url: str
    annotated_image_url: Optional[str] = None
    result_json: List[Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecordWithUser(BaseModel):
    """含用户信息的记录（管理员视图）"""
    id: int
    user_id: int
    username: str
    image_url: str
    result_json: List[Any]
    created_at: datetime


class RecordListResponse(BaseModel):
    """历史记录列表响应模型"""
    list: List[RecordInfo]
    total: int
    page: int
    size: int


class AdminRecordListResponse(BaseModel):
    """管理员记录列表响应模型"""
    list: List[RecordWithUser]
    total: int
    page: int
    size: int

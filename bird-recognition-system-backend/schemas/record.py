from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class BirdDetection(BaseModel):
    """??????????"""

    bird_id: Optional[int] = None
    bird_name: str = Field(description="????")
    confidence: float = Field(description="?????")
    bbox: List[int] = Field(description="????? [x1, y1, x2, y2]")
    center: List[float] = Field(default_factory=list, description="????? [x, y]")
    area: int = Field(default=0, description="?????")


class RecognizeResult(BaseModel):
    """?????????"""

    record_id: int
    original_image_url: str
    annotated_image_url: str
    bird_count: int
    results: List[BirdDetection]


class RecordInfo(BaseModel):
    """??????"""

    id: int
    image_url: str
    annotated_image_url: Optional[str] = None
    result_json: List[Any]
    created_at: datetime

    class Config:
        from_attributes = True


class RecordWithUser(BaseModel):
    """??????????"""

    id: int
    user_id: int
    username: str
    image_url: str
    result_json: List[Any]
    created_at: datetime


class RecordListResponse(BaseModel):
    """???????????"""

    list: List[RecordInfo]
    total: int
    page: int
    size: int


class AdminRecordListResponse(BaseModel):
    """????????????"""

    list: List[RecordWithUser]
    total: int
    page: int
    size: int

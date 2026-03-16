"""
schemas 包初始化文件
导出所有 Pydantic 模型
"""
from schemas.user import (
    UserCreate, UserLogin, UserInfo, UserProfile, 
    PasswordChange, UserStatusUpdate
)
from schemas.bird import (
    BirdCreate, BirdUpdate, BirdInfo, BirdDetail, BirdListResponse
)
from schemas.record import (
    RecognizeResult, RecordInfo, RecordListResponse
)
from schemas.response import ResponseModel

__all__ = [
    "UserCreate", "UserLogin", "UserInfo", "UserProfile",
    "PasswordChange", "UserStatusUpdate",
    "BirdCreate", "BirdUpdate", "BirdInfo", "BirdDetail", "BirdListResponse",
    "RecognizeResult", "RecordInfo", "RecordListResponse",
    "ResponseModel"
]

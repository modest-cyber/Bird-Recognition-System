"""
统一响应模型
"""
from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar

T = TypeVar("T")


class ResponseModel(BaseModel):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
    
    @classmethod
    def success(cls, data: Any = None, message: str = "success"):
        return cls(code=200, message=message, data=data)
    
    @classmethod
    def error(cls, code: int = 400, message: str = "error", data: Any = None):
        return cls(code=code, message=message, data=data)

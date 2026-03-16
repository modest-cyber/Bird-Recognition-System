"""
用户相关 Pydantic 模型
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """用户注册请求模型"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    email: EmailStr = Field(..., description="邮箱")


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserInfo(BaseModel):
    """用户基本信息"""
    id: int
    username: str
    email: str
    role: str
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """用户详细信息（含创建时间）"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """修改个人信息请求模型"""
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")


class UserStatusUpdate(BaseModel):
    """更新用户状态请求模型"""
    is_active: bool = Field(..., description="账号状态")


class LoginResponse(BaseModel):
    """登录响应模型"""
    token: str
    userInfo: UserInfo

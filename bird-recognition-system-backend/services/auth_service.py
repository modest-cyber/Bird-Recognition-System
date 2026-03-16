"""
认证服务 - JWT Token 生成、校验、密码加密
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid
import bcrypt

from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE
from database import get_db, redis_client
from models.user import User

# HTTP Bearer 认证
security = HTTPBearer()


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码加密"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def create_access_token(user_id: int, username: str, role: str) -> str:
        """创建 JWT Token"""
        expire = datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRE
        jti = str(uuid.uuid4())  # Token 唯一标识
        
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "exp": expire,
            "jti": jti
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """解码 JWT Token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def is_token_blacklisted(jti: str) -> bool:
        """检查 Token 是否在黑名单中"""
        return redis_client.exists(f"blacklist:token:{jti}")
    
    @staticmethod
    def add_token_to_blacklist(jti: str, exp: datetime):
        """将 Token 加入黑名单"""
        ttl = int((exp - datetime.utcnow()).total_seconds())
        if ttl > 0:
            redis_client.setex(f"blacklist:token:{jti}", ttl, "1")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户（依赖注入）"""
    token = credentials.credentials
    
    payload = AuthService.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期"
        )
    
    # 检查黑名单
    jti = payload.get("jti")
    if jti and AuthService.is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已失效"
        )
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """获取当前管理员用户（依赖注入）"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user

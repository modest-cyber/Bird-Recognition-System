"""
认证路由 - 用户注册、登录
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserInfo, LoginResponse
from schemas.response import ResponseModel
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=ResponseModel)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return ResponseModel.error(code=400, message="用户名已存在")
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        return ResponseModel.error(code=400, message="邮箱已被注册")
    
    # 创建新用户
    hashed_password = AuthService.hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        password=hashed_password,
        email=user_data.email
    )
    
    db.add(new_user)
    db.commit()
    
    return ResponseModel.success(message="注册成功")


@router.post("/login", response_model=ResponseModel)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查询用户
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user:
        return ResponseModel.error(code=400, message="用户名或密码错误")
    
    # 验证密码
    if not AuthService.verify_password(login_data.password, user.password):
        return ResponseModel.error(code=400, message="用户名或密码错误")
    
    # 检查账号状态
    if not user.is_active:
        return ResponseModel.error(code=403, message="账号已被禁用")
    
    # 生成 Token
    token = AuthService.create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role.value
    )
    
    # 构造用户信息
    user_info = UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value
    )
    
    return ResponseModel.success(
        message="登录成功",
        data=LoginResponse(token=token, userInfo=user_info)
    )

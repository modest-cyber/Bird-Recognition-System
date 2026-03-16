"""
用户路由 - 个人信息、密码修改
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import UserProfile, ProfileUpdate, PasswordChange
from schemas.response import ResponseModel
from services.auth_service import AuthService, get_current_user

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.get("/profile", response_model=ResponseModel)
def get_profile(current_user: User = Depends(get_current_user)):
    """获取个人信息"""
    profile = UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
    return ResponseModel.success(data=profile)


@router.put("/profile", response_model=ResponseModel)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改个人信息"""
    if profile_data.email:
        # 检查邮箱是否已被其他用户使用
        existing = db.query(User).filter(
            User.email == profile_data.email,
            User.id != current_user.id
        ).first()
        if existing:
            return ResponseModel.error(code=400, message="邮箱已被其他用户使用")
        
        current_user.email = profile_data.email
        db.commit()
    
    return ResponseModel.success(message="修改成功")


@router.put("/password", response_model=ResponseModel)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证原密码
    if not AuthService.verify_password(password_data.old_password, current_user.password):
        return ResponseModel.error(code=400, message="原密码错误")
    
    # 更新密码
    current_user.password = AuthService.hash_password(password_data.new_password)
    db.commit()
    
    return ResponseModel.success(message="密码修改成功")

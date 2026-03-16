"""
管理员路由 - 统计、用户管理、全量记录
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.record import Record
from schemas.user import UserProfile, UserStatusUpdate
from schemas.record import RecordWithUser, AdminRecordListResponse
from schemas.response import ResponseModel
from services.auth_service import get_current_admin
from services.admin_service import AdminService

router = APIRouter(prefix="/api/admin", tags=["管理员"])


@router.get("/stats", response_model=ResponseModel)
def get_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取系统统计数据"""
    stats = AdminService.get_stats(db)
    return ResponseModel.success(data=stats)


@router.get("/users", response_model=ResponseModel)
def get_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="按用户名搜索"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    # 构建查询
    query = db.query(User)
    
    if username:
        query = query.filter(User.username.like(f"%{username}%"))
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * size
    users = query.order_by(User.id.desc()).offset(offset).limit(size).all()
    
    # 构造响应
    user_list = [
        UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at
        )
        for user in users
    ]
    
    return ResponseModel.success(data={
        "list": user_list,
        "total": total,
        "page": page,
        "size": size
    })


@router.patch("/users/{user_id}/status", response_model=ResponseModel)
def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """启用/禁用用户账号"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return ResponseModel.error(code=404, message="用户不存在")
    
    # 不能禁用自己
    if user.id == current_admin.id:
        return ResponseModel.error(code=400, message="不能修改自己的账号状态")
    
    user.is_active = status_data.is_active
    db.commit()
    
    return ResponseModel.success(message="状态更新成功")


@router.get("/records", response_model=ResponseModel)
def get_all_records(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, description="按用户筛选"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取全量识别记录"""
    # 构建查询（联表查询用户名）
    query = db.query(Record, User.username).join(User, Record.user_id == User.id)
    
    if user_id:
        query = query.filter(Record.user_id == user_id)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * size
    records = query.order_by(Record.created_at.desc()).offset(offset).limit(size).all()
    
    # 构造响应
    record_list = [
        RecordWithUser(
            id=record.id,
            user_id=record.user_id,
            username=username,
            image_url=record.image_url,
            result_json=record.result_json,
            created_at=record.created_at
        )
        for record, username in records
    ]
    
    result = AdminRecordListResponse(
        list=record_list,
        total=total,
        page=page,
        size=size
    )
    
    return ResponseModel.success(data=result)

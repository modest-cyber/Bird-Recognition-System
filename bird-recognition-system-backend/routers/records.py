"""
历史记录路由 - 用户识别历史
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.record import Record
from schemas.record import RecordInfo, RecordListResponse
from schemas.response import ResponseModel
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/records", tags=["历史记录"])


@router.get("", response_model=ResponseModel)
def get_records(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的历史记录"""
    # 构建查询
    query = db.query(Record).filter(Record.user_id == current_user.id)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * size
    records = query.order_by(Record.created_at.desc()).offset(offset).limit(size).all()
    
    # 构造响应
    record_list = [
        RecordInfo(
            id=record.id,
            image_url=record.image_url,
            annotated_image_url=record.annotated_image_url,
            result_json=record.result_json,
            created_at=record.created_at
        )
        for record in records
    ]
    
    result = RecordListResponse(
        list=record_list,
        total=total,
        page=page,
        size=size
    )
    
    return ResponseModel.success(data=result)


@router.delete("/{record_id}", response_model=ResponseModel)
def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除历史记录"""
    record = db.query(Record).filter(Record.id == record_id).first()
    
    if not record:
        return ResponseModel.error(code=404, message="记录不存在")
    
    # 检查记录归属
    if record.user_id != current_user.id:
        return ResponseModel.error(code=403, message="无权删除该记录")
    
    db.delete(record)
    db.commit()
    
    return ResponseModel.success(message="删除成功")

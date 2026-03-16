"""
鸟类百科路由 - 鸟类列表、详情、CRUD
"""
import json
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db, redis_client
from models.user import User
from models.bird import Bird
from models.bird_region import BirdRegion
from schemas.bird import BirdCreate, BirdUpdate, BirdInfo, BirdDetail, BirdListResponse
from schemas.response import ResponseModel
from services.auth_service import get_current_admin
from config import CACHE_BIRD_LIST_TTL

router = APIRouter(prefix="/api/birds", tags=["鸟类百科"])


@router.get("", response_model=ResponseModel)
def get_bird_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(12, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="按名称搜索"),
    family: Optional[str] = Query(None, description="按科目筛选"),
    db: Session = Depends(get_db)
):
    """获取鸟类列表"""
    # 尝试从缓存获取
    cache_key = f"cache:birds:page:{page}:size:{size}:name:{name}:family:{family}"
    cached = redis_client.get(cache_key)
    if cached:
        return ResponseModel.success(data=json.loads(cached))
    
    # 构建查询
    query = db.query(Bird)
    
    if name:
        query = query.filter(or_(
            Bird.name.like(f"%{name}%"),
            Bird.latin_name.like(f"%{name}%")
        ))
    
    if family:
        query = query.filter(Bird.family == family)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * size
    birds = query.order_by(Bird.id.desc()).offset(offset).limit(size).all()
    
    # 构造响应
    bird_list = [
        BirdInfo(
            id=bird.id,
            name=bird.name,
            latin_name=bird.latin_name,
            family=bird.family,
            image_url=bird.image_url
        )
        for bird in birds
    ]
    
    result = BirdListResponse(
        list=bird_list,
        total=total,
        page=page,
        size=size
    )
    
    # 缓存结果
    redis_client.setex(cache_key, CACHE_BIRD_LIST_TTL, result.model_dump_json())
    
    return ResponseModel.success(data=result)


@router.get("/{bird_id}", response_model=ResponseModel)
def get_bird_detail(bird_id: int, db: Session = Depends(get_db)):
    """获取鸟类详情"""
    bird = db.query(Bird).filter(Bird.id == bird_id).first()
    
    if not bird:
        return ResponseModel.error(code=404, message="鸟类不存在")
    
    # 获取分布地区
    regions = [r.region for r in bird.regions]
    
    detail = BirdDetail(
        id=bird.id,
        name=bird.name,
        latin_name=bird.latin_name,
        family=bird.family,
        description=bird.description,
        image_url=bird.image_url,
        regions=regions,
        created_at=bird.created_at
    )
    
    return ResponseModel.success(data=detail)


@router.post("", response_model=ResponseModel)
def create_bird(
    bird_data: BirdCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """新增鸟类（管理员）"""
    # 创建鸟类
    new_bird = Bird(
        name=bird_data.name,
        latin_name=bird_data.latin_name,
        family=bird_data.family,
        description=bird_data.description,
        image_url=bird_data.image_url
    )
    
    db.add(new_bird)
    db.flush()  # 获取 ID
    
    # 添加分布地区
    if bird_data.regions:
        for region in bird_data.regions:
            db.add(BirdRegion(bird_id=new_bird.id, region=region))
    
    db.commit()
    
    # 清除缓存
    _clear_bird_cache()
    
    return ResponseModel.success(message="添加成功", data={"id": new_bird.id})


@router.put("/{bird_id}", response_model=ResponseModel)
def update_bird(
    bird_id: int,
    bird_data: BirdUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """修改鸟类（管理员）"""
    bird = db.query(Bird).filter(Bird.id == bird_id).first()
    
    if not bird:
        return ResponseModel.error(code=404, message="鸟类不存在")
    
    # 更新字段
    if bird_data.name is not None:
        bird.name = bird_data.name
    if bird_data.latin_name is not None:
        bird.latin_name = bird_data.latin_name
    if bird_data.family is not None:
        bird.family = bird_data.family
    if bird_data.description is not None:
        bird.description = bird_data.description
    if bird_data.image_url is not None:
        bird.image_url = bird_data.image_url
    
    # 更新分布地区
    if bird_data.regions is not None:
        # 删除原有地区
        db.query(BirdRegion).filter(BirdRegion.bird_id == bird_id).delete()
        # 添加新地区
        for region in bird_data.regions:
            db.add(BirdRegion(bird_id=bird_id, region=region))
    
    db.commit()
    
    # 清除缓存
    _clear_bird_cache()
    
    return ResponseModel.success(message="修改成功")


@router.delete("/{bird_id}", response_model=ResponseModel)
def delete_bird(
    bird_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除鸟类（管理员）"""
    bird = db.query(Bird).filter(Bird.id == bird_id).first()
    
    if not bird:
        return ResponseModel.error(code=404, message="鸟类不存在")
    
    db.delete(bird)
    db.commit()
    
    # 清除缓存
    _clear_bird_cache()
    
    return ResponseModel.success(message="删除成功")


def _clear_bird_cache():
    """清除鸟类相关缓存"""
    # 使用 SCAN 命令查找并删除所有鸟类缓存
    cursor = 0
    while True:
        cursor, keys = redis_client.scan(cursor, match="cache:birds:*", count=100)
        if keys:
            redis_client.delete(*keys)
        if cursor == 0:
            break

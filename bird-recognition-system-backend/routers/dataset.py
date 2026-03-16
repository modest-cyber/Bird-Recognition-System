"""
数据集管理和模型训练路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from fastapi.responses import FileResponse

from models.user import User
from schemas.response import ResponseModel
from schemas.dataset import (
    DatasetStats, DatasetListResponse, ClassMappingUpdate,
    TrainingConfig, TrainingProgress, ModelListResponse
)
from services.auth_service import get_current_admin
from services.dataset_service import DatasetService
from services.training_service import TrainingService

router = APIRouter(prefix="/api/admin/dataset", tags=["数据集管理"])


# ==================== 数据集统计 ====================

@router.get("/stats", response_model=ResponseModel)
def get_dataset_stats(
    current_admin: User = Depends(get_current_admin)
):
    """获取数据集统计信息"""
    stats = DatasetService.get_stats()
    return ResponseModel.success(data=stats.model_dump())


# ==================== 数据集文件管理 ====================

@router.get("/files", response_model=ResponseModel)
def get_dataset_files(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_admin: User = Depends(get_current_admin)
):
    """获取数据集文件列表"""
    files, total = DatasetService.get_file_list(page, size)
    return ResponseModel.success(data={
        'images': [f.model_dump() for f in files],
        'total': total,
        'page': page,
        'size': size
    })


@router.post("/upload/images", response_model=ResponseModel)
async def upload_images(
    files: List[UploadFile] = File(..., description="图片文件列表"),
    current_admin: User = Depends(get_current_admin)
):
    """批量上传图片"""
    if not files:
        return ResponseModel.error(code=400, message="请选择要上传的文件")
    
    # 读取文件内容
    file_data = []
    for file in files:
        content = await file.read()
        file_data.append((file.filename, content))
    
    result = await DatasetService.upload_images(file_data)
    
    if result['failed_count'] > 0:
        return ResponseModel.success(
            data=result,
            message=f"上传完成: 成功 {result['success_count']} 个, 失败 {result['failed_count']} 个"
        )
    return ResponseModel.success(data=result, message=f"成功上传 {result['success_count']} 个文件")


@router.post("/upload/labels", response_model=ResponseModel)
async def upload_labels(
    files: List[UploadFile] = File(..., description="标注文件列表"),
    current_admin: User = Depends(get_current_admin)
):
    """批量上传标注文件"""
    if not files:
        return ResponseModel.error(code=400, message="请选择要上传的文件")
    
    # 读取文件内容
    file_data = []
    for file in files:
        content = await file.read()
        file_data.append((file.filename, content))
    
    result = await DatasetService.upload_labels(file_data)
    
    if result['failed_count'] > 0:
        return ResponseModel.success(
            data=result,
            message=f"上传完成: 成功 {result['success_count']} 个, 失败 {result['failed_count']} 个"
        )
    return ResponseModel.success(data=result, message=f"成功上传 {result['success_count']} 个文件")


@router.delete("/files/{filename}", response_model=ResponseModel)
def delete_file(
    filename: str,
    file_type: str = Query("image", description="文件类型: image 或 label"),
    current_admin: User = Depends(get_current_admin)
):
    """删除数据集文件"""
    success = DatasetService.delete_file(filename, file_type)
    if success:
        return ResponseModel.success(message="文件已删除")
    return ResponseModel.error(code=404, message="文件不存在或删除失败")


@router.delete("/clear", response_model=ResponseModel)
def clear_dataset(
    current_admin: User = Depends(get_current_admin)
):
    """清空数据集"""
    success = DatasetService.clear_dataset()
    if success:
        return ResponseModel.success(message="数据集已清空")
    return ResponseModel.error(code=500, message="清空数据集失败")


# ==================== 类别管理 ====================

@router.get("/classes", response_model=ResponseModel)
def get_classes(
    current_admin: User = Depends(get_current_admin)
):
    """获取类别列表"""
    classes = DatasetService.get_class_names()
    return ResponseModel.success(data={
        'classes': classes,
        'total': len(classes)
    })


@router.put("/classes", response_model=ResponseModel)
def update_classes(
    data: ClassMappingUpdate,
    current_admin: User = Depends(get_current_admin)
):
    """更新类别列表"""
    success = DatasetService.update_class_names(data.classes)
    if success:
        return ResponseModel.success(message="类别已更新")
    return ResponseModel.error(code=500, message="更新类别失败")


# ==================== 模型训练 ====================

@router.post("/training/start", response_model=ResponseModel)
def start_training(
    config: TrainingConfig,
    current_admin: User = Depends(get_current_admin)
):
    """启动模型训练"""
    result = TrainingService.start_training(config)
    if result['success']:
        return ResponseModel.success(message=result['message'])
    return ResponseModel.error(code=400, message=result['message'])


@router.post("/training/stop", response_model=ResponseModel)
def stop_training(
    current_admin: User = Depends(get_current_admin)
):
    """停止模型训练"""
    result = TrainingService.stop_training()
    if result['success']:
        return ResponseModel.success(message=result['message'])
    return ResponseModel.error(code=400, message=result['message'])


@router.get("/training/progress", response_model=ResponseModel)
def get_training_progress(
    current_admin: User = Depends(get_current_admin)
):
    """获取训练进度"""
    progress = TrainingService.get_progress()
    return ResponseModel.success(data=progress.model_dump())


@router.get("/training/logs", response_model=ResponseModel)
def get_training_logs(
    limit: int = Query(100, ge=1, le=1000, description="日志条数"),
    current_admin: User = Depends(get_current_admin)
):
    """获取训练日志"""
    logs = TrainingService.get_logs(limit)
    return ResponseModel.success(data={
        'logs': [log.model_dump() for log in logs],
        'total': len(logs)
    })


# ==================== 模型管理 ====================

@router.get("/models", response_model=ResponseModel)
def get_models(
    current_admin: User = Depends(get_current_admin)
):
    """获取模型列表"""
    models = TrainingService.get_model_list()
    return ResponseModel.success(data={
        'models': [m.model_dump() for m in models],
        'total': len(models)
    })


@router.post("/models/activate", response_model=ResponseModel)
def activate_model(
    model_path: str = Form(..., description="模型文件路径"),
    current_admin: User = Depends(get_current_admin)
):
    """激活指定模型"""
    result = TrainingService.activate_model(model_path)
    if result['success']:
        return ResponseModel.success(message=result['message'])
    return ResponseModel.error(code=400, message=result['message'])


@router.delete("/models", response_model=ResponseModel)
def delete_model(
    model_path: str = Query(..., description="模型文件路径"),
    current_admin: User = Depends(get_current_admin)
):
    """删除模型"""
    result = TrainingService.delete_model(model_path)
    if result['success']:
        return ResponseModel.success(message=result['message'])
    return ResponseModel.error(code=400, message=result['message'])

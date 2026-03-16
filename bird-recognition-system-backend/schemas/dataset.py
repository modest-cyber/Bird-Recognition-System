"""
数据集和训练相关的 Schema 定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TrainingStatus(str, Enum):
    """训练状态枚举"""
    IDLE = "idle"           # 空闲
    PREPARING = "preparing"  # 准备中
    TRAINING = "training"    # 训练中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


# ==================== 数据集相关 ====================

class DatasetStats(BaseModel):
    """数据集统计信息"""
    total_images: int = Field(default=0, description="图片总数")
    total_labels: int = Field(default=0, description="标注文件总数")
    labeled_images: int = Field(default=0, description="已标注图片数")
    unlabeled_images: int = Field(default=0, description="未标注图片数")
    total_classes: int = Field(default=0, description="类别总数")
    class_names: List[str] = Field(default=[], description="类别名称列表")
    class_distribution: Dict[str, int] = Field(default={}, description="各类别样本数")


class DatasetFileInfo(BaseModel):
    """数据集文件信息"""
    filename: str = Field(description="文件名")
    file_type: str = Field(description="文件类型 (image/label)")
    size: int = Field(description="文件大小 (bytes)")
    has_label: bool = Field(default=False, description="是否有对应标注")
    created_at: Optional[datetime] = None


class DatasetListResponse(BaseModel):
    """数据集文件列表响应"""
    images: List[DatasetFileInfo]
    total: int
    page: int
    size: int


class ClassMapping(BaseModel):
    """类别映射"""
    class_id: int = Field(description="类别ID")
    class_name: str = Field(description="类别名称")


class ClassMappingUpdate(BaseModel):
    """类别映射更新"""
    classes: List[str] = Field(description="类别名称列表，索引即为类别ID")


# ==================== 训练相关 ====================

class TrainingConfig(BaseModel):
    """训练配置"""
    epochs: int = Field(default=100, ge=1, le=500, description="训练轮数")
    batch_size: int = Field(default=16, ge=1, le=64, description="批次大小")
    learning_rate: float = Field(default=0.01, gt=0, le=1, description="学习率")
    val_split: float = Field(default=0.2, ge=0.1, le=0.5, description="验证集比例")
    img_size: int = Field(default=640, ge=320, le=1280, description="图像尺寸")
    pretrained: bool = Field(default=True, description="是否使用预训练模型")
    model_name: str = Field(default="yolov8n", description="基础模型名称")


class TrainingProgress(BaseModel):
    """训练进度"""
    status: TrainingStatus = Field(default=TrainingStatus.IDLE)
    current_epoch: int = Field(default=0)
    total_epochs: int = Field(default=0)
    progress_percent: float = Field(default=0.0)
    train_loss: Optional[float] = None
    val_loss: Optional[float] = None
    metrics: Dict[str, Any] = Field(default={})
    message: str = Field(default="")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    log_file: Optional[str] = None


class TrainingHistory(BaseModel):
    """训练历史记录"""
    epoch: int
    train_loss: float
    val_loss: Optional[float] = None
    mAP50: Optional[float] = None
    mAP50_95: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None


class TrainingResult(BaseModel):
    """训练结果"""
    success: bool
    model_path: Optional[str] = None
    best_mAP: Optional[float] = None
    total_epochs: int = 0
    training_time: float = 0.0  # 秒
    history: List[TrainingHistory] = []
    message: str = ""


class TrainingLog(BaseModel):
    """训练日志"""
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR
    message: str


class TrainingLogsResponse(BaseModel):
    """训练日志响应"""
    logs: List[TrainingLog]
    total: int


# ==================== 模型管理 ====================

class ModelInfo(BaseModel):
    """模型信息"""
    name: str
    path: str
    size: int  # bytes
    created_at: datetime
    is_active: bool = False
    metrics: Optional[Dict[str, float]] = None


class ModelListResponse(BaseModel):
    """模型列表响应"""
    models: List[ModelInfo]
    active_model: Optional[str] = None

"""
模型训练服务
处理 YOLOv8 模型的训练、进度监控、模型管理等功能
"""
import os
import time
import shutil
import threading
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

from config import (
    TRAINING_OUTPUT_DIR, DATASET_DIR, YOLO_WEIGHTS_PATH,
    DEFAULT_EPOCHS, DEFAULT_BATCH_SIZE, DEFAULT_LEARNING_RATE,
    DEFAULT_VAL_SPLIT, DEFAULT_IMG_SIZE
)
from schemas.dataset import (
    TrainingStatus, TrainingProgress, TrainingConfig,
    TrainingHistory, TrainingResult, ModelInfo, TrainingLog
)
from services.dataset_service import DatasetService

logger = logging.getLogger(__name__)

# 尝试导入 ultralytics
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("ultralytics 未安装，训练功能不可用")


class TrainingService:
    """模型训练服务"""
    
    # 训练状态（进程内共享）
    _training_progress: TrainingProgress = TrainingProgress()
    _training_lock = threading.Lock()
    _training_thread: Optional[threading.Thread] = None
    _stop_training = False
    _training_logs: List[TrainingLog] = []
    
    @classmethod
    def get_progress(cls) -> TrainingProgress:
        """获取当前训练进度"""
        with cls._training_lock:
            return cls._training_progress.model_copy()
    
    @classmethod
    def _update_progress(cls, **kwargs):
        """更新训练进度"""
        with cls._training_lock:
            for key, value in kwargs.items():
                if hasattr(cls._training_progress, key):
                    setattr(cls._training_progress, key, value)
    
    @classmethod
    def _add_log(cls, level: str, message: str):
        """添加训练日志"""
        log = TrainingLog(
            timestamp=datetime.now(),
            level=level,
            message=message
        )
        with cls._training_lock:
            cls._training_logs.append(log)
            # 只保留最近 1000 条日志
            if len(cls._training_logs) > 1000:
                cls._training_logs = cls._training_logs[-1000:]
        logger.info(f"[Training {level}] {message}")
    
    @classmethod
    def get_logs(cls, limit: int = 100) -> List[TrainingLog]:
        """获取训练日志"""
        with cls._training_lock:
            return cls._training_logs[-limit:]
    
    @classmethod
    def start_training(cls, config: TrainingConfig) -> Dict[str, Any]:
        """
        启动模型训练
        
        Args:
            config: 训练配置
            
        Returns:
            启动结果
        """
        # 检查是否正在训练
        if cls._training_progress.status in [TrainingStatus.TRAINING, TrainingStatus.PREPARING]:
            return {'success': False, 'message': '已有训练任务正在进行中'}
        
        # 检查 YOLO 是否可用
        if not YOLO_AVAILABLE:
            return {'success': False, 'message': 'ultralytics 未安装，无法进行训练'}
        
        # 检查数据集
        stats = DatasetService.get_stats()
        if stats.labeled_images < 10:
            return {'success': False, 'message': f'已标注图片数量不足，当前 {stats.labeled_images} 张，至少需要 10 张'}
        
        if stats.total_classes == 0:
            return {'success': False, 'message': '请先配置类别映射文件 (classes.txt)'}
        
        # 清空日志
        with cls._training_lock:
            cls._training_logs = []
        
        # 启动训练线程
        cls._stop_training = False
        cls._training_thread = threading.Thread(
            target=cls._training_worker,
            args=(config,),
            daemon=True
        )
        cls._training_thread.start()
        
        return {'success': True, 'message': '训练任务已启动'}
    
    @classmethod
    def stop_training(cls) -> Dict[str, Any]:
        """停止训练"""
        if cls._training_progress.status != TrainingStatus.TRAINING:
            return {'success': False, 'message': '当前没有正在进行的训练'}
        
        cls._stop_training = True
        cls._add_log('WARNING', '收到停止训练请求，正在终止...')
        
        return {'success': True, 'message': '正在停止训练...'}
    
    @classmethod
    def _training_worker(cls, config: TrainingConfig):
        """训练工作线程"""
        start_time = time.time()
        
        try:
            # 更新状态为准备中
            cls._update_progress(
                status=TrainingStatus.PREPARING,
                current_epoch=0,
                total_epochs=config.epochs,
                progress_percent=0,
                train_loss=None,
                val_loss=None,
                metrics={},
                message='正在准备训练数据...',
                started_at=datetime.now(),
                completed_at=None
            )
            cls._add_log('INFO', '开始准备训练数据')
            
            # 准备训练数据
            data_yaml = DatasetService.prepare_training_data(config.val_split)
            if not data_yaml:
                cls._update_progress(
                    status=TrainingStatus.FAILED,
                    message='准备训练数据失败'
                )
                cls._add_log('ERROR', '准备训练数据失败')
                return
            
            cls._add_log('INFO', f'训练数据准备完成: {data_yaml}')
            
            # 确保输出目录存在
            os.makedirs(TRAINING_OUTPUT_DIR, exist_ok=True)
            
            # 创建本次训练的输出目录
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            run_dir = os.path.join(TRAINING_OUTPUT_DIR, f'train_{timestamp}')
            os.makedirs(run_dir, exist_ok=True)
            
            # 加载基础模型
            cls._add_log('INFO', f'加载基础模型: {config.model_name}')
            if config.pretrained:
                model = YOLO(f'{config.model_name}.pt')
            else:
                model = YOLO(f'{config.model_name}.yaml')
            
            # 更新状态为训练中
            cls._update_progress(
                status=TrainingStatus.TRAINING,
                message='正在训练模型...'
            )
            cls._add_log('INFO', f'开始训练: epochs={config.epochs}, batch={config.batch_size}, lr={config.learning_rate}')
            
            # 定义回调函数来更新进度
            def on_train_epoch_end(trainer):
                if cls._stop_training:
                    raise KeyboardInterrupt("用户停止训练")
                
                epoch = trainer.epoch + 1
                progress = (epoch / config.epochs) * 100
                
                # 获取训练损失
                train_loss = None
                if hasattr(trainer, 'loss') and trainer.loss is not None:
                    train_loss = float(trainer.loss)
                
                # 获取验证指标
                metrics = {}
                val_loss = None
                if hasattr(trainer, 'metrics'):
                    for k, v in trainer.metrics.items():
                        if isinstance(v, (int, float)):
                            metrics[k] = round(float(v), 4)
                    val_loss = metrics.get('val/box_loss')
                
                cls._update_progress(
                    current_epoch=epoch,
                    progress_percent=round(progress, 1),
                    train_loss=train_loss,
                    val_loss=val_loss,
                    metrics=metrics,
                    message=f'Epoch {epoch}/{config.epochs}'
                )
                
                cls._add_log('INFO', f'Epoch {epoch}/{config.epochs} 完成, loss={train_loss}')
            
            # 添加回调
            model.add_callback('on_train_epoch_end', on_train_epoch_end)
            
            # 开始训练
            results = model.train(
                data=data_yaml,
                epochs=config.epochs,
                batch=config.batch_size,
                imgsz=config.img_size,
                lr0=config.learning_rate,
                project=TRAINING_OUTPUT_DIR,
                name=f'train_{timestamp}',
                exist_ok=True,
                verbose=True,
                device='0' if cls._check_cuda() else 'cpu'
            )
            
            # 训练完成，复制最佳模型
            best_model_path = os.path.join(run_dir, 'weights', 'best.pt')
            if os.path.exists(best_model_path):
                # 复制到 yolo/weights 目录
                target_path = YOLO_WEIGHTS_PATH
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy2(best_model_path, target_path)
                cls._add_log('INFO', f'最佳模型已保存到: {target_path}')
                
                # 重新加载模型
                cls._reload_model()
            
            # 计算训练时间
            training_time = time.time() - start_time
            
            # 更新状态为完成
            cls._update_progress(
                status=TrainingStatus.COMPLETED,
                progress_percent=100,
                message=f'训练完成，耗时 {training_time/60:.1f} 分钟',
                completed_at=datetime.now()
            )
            cls._add_log('INFO', f'训练完成，总耗时: {training_time/60:.1f} 分钟')
            
        except KeyboardInterrupt:
            cls._update_progress(
                status=TrainingStatus.CANCELLED,
                message='训练已被用户取消',
                completed_at=datetime.now()
            )
            cls._add_log('WARNING', '训练已被用户取消')
            
        except Exception as e:
            logger.exception(f'训练失败: {e}')
            cls._update_progress(
                status=TrainingStatus.FAILED,
                message=f'训练失败: {str(e)}',
                completed_at=datetime.now()
            )
            cls._add_log('ERROR', f'训练失败: {str(e)}')
    
    @classmethod
    def _check_cuda(cls) -> bool:
        """检查 CUDA 是否可用"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    @classmethod
    def _reload_model(cls):
        """重新加载模型"""
        try:
            # 清除缓存，下次使用时重新加载
            import yolo.model as yolo_model
            yolo_model._detector = None
            cls._add_log('INFO', '模型缓存已清除，下次识别将使用新模型')
        except Exception as e:
            logger.warning(f'重新加载模型失败: {e}')
    
    @classmethod
    def get_model_list(cls) -> List[ModelInfo]:
        """获取已训练的模型列表"""
        models = []
        
        # 检查 yolo/weights 目录
        weights_dir = os.path.dirname(YOLO_WEIGHTS_PATH)
        if os.path.exists(weights_dir):
            for f in os.listdir(weights_dir):
                if f.endswith('.pt'):
                    file_path = os.path.join(weights_dir, f)
                    stat = os.stat(file_path)
                    models.append(ModelInfo(
                        name=f,
                        path=file_path,
                        size=stat.st_size,
                        created_at=datetime.fromtimestamp(stat.st_mtime),
                        is_active=(file_path == YOLO_WEIGHTS_PATH)
                    ))
        
        # 检查 training_output 目录
        if os.path.exists(TRAINING_OUTPUT_DIR):
            for run_dir in os.listdir(TRAINING_OUTPUT_DIR):
                weights_path = os.path.join(TRAINING_OUTPUT_DIR, run_dir, 'weights')
                if os.path.exists(weights_path):
                    for f in ['best.pt', 'last.pt']:
                        file_path = os.path.join(weights_path, f)
                        if os.path.exists(file_path):
                            stat = os.stat(file_path)
                            models.append(ModelInfo(
                                name=f'{run_dir}/{f}',
                                path=file_path,
                                size=stat.st_size,
                                created_at=datetime.fromtimestamp(stat.st_mtime),
                                is_active=False
                            ))
        
        # 按创建时间排序
        models.sort(key=lambda x: x.created_at, reverse=True)
        return models
    
    @classmethod
    def activate_model(cls, model_path: str) -> Dict[str, Any]:
        """激活指定模型"""
        if not os.path.exists(model_path):
            return {'success': False, 'message': '模型文件不存在'}
        
        try:
            # 复制到默认位置
            os.makedirs(os.path.dirname(YOLO_WEIGHTS_PATH), exist_ok=True)
            shutil.copy2(model_path, YOLO_WEIGHTS_PATH)
            
            # 重新加载模型
            cls._reload_model()
            
            return {'success': True, 'message': '模型已激活'}
        except Exception as e:
            logger.error(f'激活模型失败: {e}')
            return {'success': False, 'message': f'激活失败: {str(e)}'}
    
    @classmethod
    def delete_model(cls, model_path: str) -> Dict[str, Any]:
        """删除模型"""
        if model_path == YOLO_WEIGHTS_PATH:
            return {'success': False, 'message': '不能删除当前激活的模型'}
        
        if not os.path.exists(model_path):
            return {'success': False, 'message': '模型文件不存在'}
        
        try:
            os.remove(model_path)
            return {'success': True, 'message': '模型已删除'}
        except Exception as e:
            logger.error(f'删除模型失败: {e}')
            return {'success': False, 'message': f'删除失败: {str(e)}'}

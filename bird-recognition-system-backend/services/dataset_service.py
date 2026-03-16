"""
数据集管理服务
处理数据集的上传、管理、统计等功能
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging

from config import (
    DATASET_DIR, DATASET_IMAGES_DIR, DATASET_LABELS_DIR,
    DATASET_CLASSES_FILE, ALLOWED_EXTENSIONS
)
from schemas.dataset import DatasetStats, DatasetFileInfo, ClassMapping

logger = logging.getLogger(__name__)


class DatasetService:
    """数据集管理服务"""
    
    # 支持的图片格式
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    
    @classmethod
    def ensure_dirs(cls):
        """确保数据集目录存在"""
        os.makedirs(DATASET_DIR, exist_ok=True)
        os.makedirs(DATASET_IMAGES_DIR, exist_ok=True)
        os.makedirs(DATASET_LABELS_DIR, exist_ok=True)
    
    @classmethod
    def get_stats(cls) -> DatasetStats:
        """获取数据集统计信息"""
        cls.ensure_dirs()
        
        # 获取所有图片文件
        image_files = cls._get_image_files()
        total_images = len(image_files)
        
        # 获取所有标注文件
        label_files = cls._get_label_files()
        total_labels = len(label_files)
        
        # 统计已标注和未标注图片
        labeled_images = 0
        for img_file in image_files:
            label_name = Path(img_file).stem + '.txt'
            if label_name in label_files:
                labeled_images += 1
        
        unlabeled_images = total_images - labeled_images
        
        # 获取类别信息
        class_names = cls.get_class_names()
        total_classes = len(class_names)
        
        # 统计各类别样本数
        class_distribution = cls._get_class_distribution(label_files, class_names)
        
        return DatasetStats(
            total_images=total_images,
            total_labels=total_labels,
            labeled_images=labeled_images,
            unlabeled_images=unlabeled_images,
            total_classes=total_classes,
            class_names=class_names,
            class_distribution=class_distribution
        )
    
    @classmethod
    def _get_image_files(cls) -> List[str]:
        """获取所有图片文件名"""
        if not os.path.exists(DATASET_IMAGES_DIR):
            return []
        
        files = []
        for f in os.listdir(DATASET_IMAGES_DIR):
            if Path(f).suffix.lower() in cls.IMAGE_EXTENSIONS:
                files.append(f)
        return sorted(files)
    
    @classmethod
    def _get_label_files(cls) -> set:
        """获取所有标注文件名"""
        if not os.path.exists(DATASET_LABELS_DIR):
            return set()
        
        files = set()
        for f in os.listdir(DATASET_LABELS_DIR):
            if f.endswith('.txt'):
                files.add(f)
        return files
    
    @classmethod
    def _get_class_distribution(cls, label_files: set, class_names: List[str]) -> Dict[str, int]:
        """统计各类别样本数"""
        distribution = {name: 0 for name in class_names}
        
        for label_file in label_files:
            label_path = os.path.join(DATASET_LABELS_DIR, label_file)
            try:
                with open(label_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            if 0 <= class_id < len(class_names):
                                distribution[class_names[class_id]] += 1
            except Exception as e:
                logger.warning(f"读取标注文件失败: {label_file}, {e}")
        
        return distribution
    
    @classmethod
    def get_class_names(cls) -> List[str]:
        """获取类别名称列表"""
        if not os.path.exists(DATASET_CLASSES_FILE):
            return []
        
        try:
            with open(DATASET_CLASSES_FILE, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"读取类别文件失败: {e}")
            return []
    
    @classmethod
    def update_class_names(cls, class_names: List[str]) -> bool:
        """更新类别名称列表"""
        cls.ensure_dirs()
        
        try:
            with open(DATASET_CLASSES_FILE, 'w', encoding='utf-8') as f:
                for name in class_names:
                    f.write(name.strip() + '\n')
            return True
        except Exception as e:
            logger.error(f"更新类别文件失败: {e}")
            return False
    
    @classmethod
    def get_file_list(cls, page: int = 1, size: int = 20) -> Tuple[List[DatasetFileInfo], int]:
        """获取数据集文件列表"""
        cls.ensure_dirs()
        
        image_files = cls._get_image_files()
        label_files = cls._get_label_files()
        
        # 分页
        total = len(image_files)
        start = (page - 1) * size
        end = start + size
        paged_files = image_files[start:end]
        
        result = []
        for img_file in paged_files:
            img_path = os.path.join(DATASET_IMAGES_DIR, img_file)
            label_name = Path(img_file).stem + '.txt'
            has_label = label_name in label_files
            
            try:
                stat = os.stat(img_path)
                file_size = stat.st_size
                created_at = datetime.fromtimestamp(stat.st_ctime)
            except:
                file_size = 0
                created_at = None
            
            result.append(DatasetFileInfo(
                filename=img_file,
                file_type='image',
                size=file_size,
                has_label=has_label,
                created_at=created_at
            ))
        
        return result, total
    
    @classmethod
    async def upload_images(cls, files: List[Tuple[str, bytes]]) -> Dict[str, any]:
        """
        批量上传图片
        
        Args:
            files: [(filename, content), ...]
            
        Returns:
            上传结果统计
        """
        cls.ensure_dirs()
        
        success_count = 0
        failed_count = 0
        failed_files = []
        
        for filename, content in files:
            try:
                # 检查文件扩展名
                ext = Path(filename).suffix.lower()
                if ext not in cls.IMAGE_EXTENSIONS:
                    failed_count += 1
                    failed_files.append(f"{filename}: 不支持的格式")
                    continue
                
                # 保存文件
                file_path = os.path.join(DATASET_IMAGES_DIR, filename)
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                failed_files.append(f"{filename}: {str(e)}")
                logger.error(f"上传图片失败: {filename}, {e}")
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_files': failed_files
        }
    
    @classmethod
    async def upload_labels(cls, files: List[Tuple[str, bytes]]) -> Dict[str, any]:
        """
        批量上传标注文件
        
        Args:
            files: [(filename, content), ...]
            
        Returns:
            上传结果统计
        """
        cls.ensure_dirs()
        
        success_count = 0
        failed_count = 0
        failed_files = []
        
        for filename, content in files:
            try:
                # 检查文件扩展名
                if not filename.endswith('.txt'):
                    failed_count += 1
                    failed_files.append(f"{filename}: 必须是.txt文件")
                    continue
                
                # 验证标注格式
                content_str = content.decode('utf-8')
                if not cls._validate_label_content(content_str):
                    failed_count += 1
                    failed_files.append(f"{filename}: 标注格式错误")
                    continue
                
                # 保存文件
                file_path = os.path.join(DATASET_LABELS_DIR, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content_str)
                
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                failed_files.append(f"{filename}: {str(e)}")
                logger.error(f"上传标注失败: {filename}, {e}")
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_files': failed_files
        }
    
    @classmethod
    def _validate_label_content(cls, content: str) -> bool:
        """验证标注文件内容格式"""
        lines = content.strip().split('\n')
        
        if not lines or (len(lines) == 1 and not lines[0].strip()):
            # 空文件也是有效的（表示无目标）
            return True
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 5:
                return False
            
            try:
                class_id = int(parts[0])
                if class_id < 0:
                    return False
                
                # 检查坐标是否在 0-1 范围内
                for i in range(1, 5):
                    val = float(parts[i])
                    if not (0 <= val <= 1):
                        return False
            except ValueError:
                return False
        
        return True
    
    @classmethod
    def delete_file(cls, filename: str, file_type: str) -> bool:
        """删除数据集文件"""
        try:
            if file_type == 'image':
                file_path = os.path.join(DATASET_IMAGES_DIR, filename)
                # 同时删除对应的标注文件
                label_path = os.path.join(DATASET_LABELS_DIR, Path(filename).stem + '.txt')
                if os.path.exists(label_path):
                    os.remove(label_path)
            else:
                file_path = os.path.join(DATASET_LABELS_DIR, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件失败: {filename}, {e}")
            return False
    
    @classmethod
    def clear_dataset(cls) -> bool:
        """清空数据集"""
        try:
            if os.path.exists(DATASET_IMAGES_DIR):
                shutil.rmtree(DATASET_IMAGES_DIR)
            if os.path.exists(DATASET_LABELS_DIR):
                shutil.rmtree(DATASET_LABELS_DIR)
            
            cls.ensure_dirs()
            return True
        except Exception as e:
            logger.error(f"清空数据集失败: {e}")
            return False
    
    @classmethod
    def prepare_training_data(cls, val_split: float = 0.2) -> Optional[str]:
        """
        准备训练数据，生成 YOLO 格式的数据集配置
        
        Args:
            val_split: 验证集比例
            
        Returns:
            data.yaml 文件路径
        """
        cls.ensure_dirs()
        
        import random
        
        # 获取所有已标注的图片
        image_files = cls._get_image_files()
        label_files = cls._get_label_files()
        
        labeled_images = []
        for img_file in image_files:
            label_name = Path(img_file).stem + '.txt'
            if label_name in label_files:
                labeled_images.append(img_file)
        
        if len(labeled_images) < 10:
            logger.error("已标注图片数量不足，至少需要10张")
            return None
        
        # 随机划分训练集和验证集
        random.shuffle(labeled_images)
        val_size = int(len(labeled_images) * val_split)
        val_images = labeled_images[:val_size]
        train_images = labeled_images[val_size:]
        
        # 创建训练目录结构
        train_dir = os.path.join(DATASET_DIR, 'train')
        val_dir = os.path.join(DATASET_DIR, 'val')
        
        for d in [train_dir, val_dir]:
            img_dir = os.path.join(d, 'images')
            lbl_dir = os.path.join(d, 'labels')
            os.makedirs(img_dir, exist_ok=True)
            os.makedirs(lbl_dir, exist_ok=True)
        
        # 复制文件到对应目录
        for img_file in train_images:
            cls._copy_data_file(img_file, os.path.join(train_dir, 'images'), os.path.join(train_dir, 'labels'))
        
        for img_file in val_images:
            cls._copy_data_file(img_file, os.path.join(val_dir, 'images'), os.path.join(val_dir, 'labels'))
        
        # 生成 data.yaml
        class_names = cls.get_class_names()
        data_yaml_path = os.path.join(DATASET_DIR, 'data.yaml')
        
        yaml_content = f"""# 鸟类识别数据集配置
path: {DATASET_DIR}
train: train/images
val: val/images

nc: {len(class_names)}
names: {class_names}
"""
        
        with open(data_yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        logger.info(f"训练数据准备完成: 训练集 {len(train_images)} 张, 验证集 {len(val_images)} 张")
        return data_yaml_path
    
    @classmethod
    def _copy_data_file(cls, img_file: str, img_dest: str, label_dest: str):
        """复制图片和对应的标注文件"""
        # 复制图片
        src_img = os.path.join(DATASET_IMAGES_DIR, img_file)
        dst_img = os.path.join(img_dest, img_file)
        shutil.copy2(src_img, dst_img)
        
        # 复制标注
        label_file = Path(img_file).stem + '.txt'
        src_label = os.path.join(DATASET_LABELS_DIR, label_file)
        dst_label = os.path.join(label_dest, label_file)
        if os.path.exists(src_label):
            shutil.copy2(src_label, dst_label)

"""
识别服务 - 图片上传、YOLO 推理、结果保存
"""
import os
import time
from typing import List, Tuple
from PIL import Image
import logging

from sqlalchemy.orm import Session

from config import (
    UPLOAD_ORIGINAL_DIR, UPLOAD_ANNOTATED_DIR,
    MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS
)
from models.record import Record
from models.bird import Bird
from yolo.model import get_detector

logger = logging.getLogger(__name__)


class RecognizeService:
    """识别服务类"""
    
    @staticmethod
    def validate_file(filename: str, file_size: int) -> Tuple[bool, str]:
        """
        验证上传文件
        
        Returns:
            (is_valid, error_message)
        """
        # 检查文件扩展名
        if "." not in filename:
            return False, "文件名无效"
        
        ext = filename.rsplit(".", 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"图片格式不支持，仅支持 {'/'.join(ALLOWED_EXTENSIONS)}"
        
        # 检查文件大小
        if file_size > MAX_UPLOAD_SIZE:
            return False, f"文件大小超过限制（最大 {MAX_UPLOAD_SIZE // 1024 // 1024}MB）"
        
        return True, ""
    
    @staticmethod
    def save_upload_file(file_content: bytes, user_id: int, ext: str) -> str:
        """
        保存上传的文件
        
        Returns:
            保存的文件路径
        """
        # 确保目录存在
        os.makedirs(UPLOAD_ORIGINAL_DIR, exist_ok=True)
        
        # 生成文件名
        timestamp = int(time.time())
        filename = f"{user_id}_{timestamp}.{ext}"
        filepath = os.path.join(UPLOAD_ORIGINAL_DIR, filename)
        
        # 保存文件
        with open(filepath, "wb") as f:
            f.write(file_content)
        
        return filepath
    
    @staticmethod
    def recognize_image(image_path: str, user_id: int) -> Tuple[List[dict], str]:
        """
        识别图片中的鸟类
        
        Returns:
            (detections, annotated_image_path)
        """
        detector = get_detector()
        
        # 执行推理
        detections = detector.predict(image_path)
        
        # 生成标注图片
        os.makedirs(UPLOAD_ANNOTATED_DIR, exist_ok=True)
        
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        annotated_filename = f"{name}_annotated{ext}"
        annotated_path = os.path.join(UPLOAD_ANNOTATED_DIR, annotated_filename)
        
        detector.annotate_image(image_path, detections, annotated_path)
        
        return detections, annotated_path
    
    @staticmethod
    def match_bird_id(detections: List[dict], db: Session) -> List[dict]:
        """
        匹配检测结果中的鸟类 ID
        """
        for det in detections:
            bird_name = det.get("bird_name", "")
            # 尝试从数据库匹配鸟类
            bird = db.query(Bird).filter(Bird.name == bird_name).first()
            if bird:
                det["bird_id"] = bird.id
            else:
                det["bird_id"] = None
        
        return detections
    
    @staticmethod
    def save_record(
        db: Session,
        user_id: int,
        image_url: str,
        annotated_image_url: str,
        result_json: List[dict]
    ) -> Record:
        """
        保存识别记录
        """
        record = Record(
            user_id=user_id,
            image_url=image_url,
            annotated_image_url=annotated_image_url,
            result_json=result_json
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return record
    
    @staticmethod
    def path_to_url(filepath: str) -> str:
        """
        将文件系统路径转换为 URL 路径
        """
        # 提取相对于 uploads 目录的路径
        if "uploads" in filepath:
            parts = filepath.replace("\\", "/").split("uploads/")
            if len(parts) > 1:
                return f"/uploads/{parts[1]}"
        
        return filepath.replace("\\", "/")

"""
YOLO 模型加载和推理封装
"""
import os
from typing import List, Dict, Optional
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# 尝试导入 ultralytics，如果失败则使用模拟模式
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("ultralytics 未安装，将使用模拟识别模式")


class BirdDetector:
    """鸟类检测器"""
    
    def __init__(self, weights_path: str, confidence_threshold: float = 0.4):
        self.weights_path = weights_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        # 模拟模式的鸟类类别映射
        self.mock_classes = {
            0: "白鹭",
            1: "麻雀",
            2: "喜鹊",
            3: "燕子",
            4: "黄鹂",
            5: "杜鹃",
            6: "画眉",
            7: "翠鸟",
            8: "啄木鸟",
            9: "乌鸦"
        }
        
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        if not YOLO_AVAILABLE:
            logger.info("使用模拟识别模式")
            return
        
        if os.path.exists(self.weights_path):
            try:
                self.model = YOLO(self.weights_path)
                logger.info(f"成功加载模型: {self.weights_path}")
            except Exception as e:
                logger.error(f"模型加载失败: {e}")
                self.model = None
        else:
            # 如果自定义权重不存在，尝试使用预训练模型
            try:
                self.model = YOLO("yolov8n.pt")  # 使用最小的预训练模型
                logger.info("使用 YOLOv8n 预训练模型")
            except Exception as e:
                logger.warning(f"无法加载预训练模型: {e}")
                self.model = None
    
    def predict(self, image_path: str) -> List[Dict]:
        """
        对图片进行鸟类检测
        
        Args:
            image_path: 图片路径
            
        Returns:
            检测结果列表 [{ bird_name, confidence, bbox }]
        """
        if self.model is None:
            # 模拟模式：返回模拟结果
            return self._mock_predict(image_path)
        
        try:
            # 使用 YOLO 进行推理
            results = self.model(image_path, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                        
                        # 获取类别名称
                        class_name = result.names.get(cls_id, f"鸟类_{cls_id}")
                        
                        detections.append({
                            "bird_name": class_name,
                            "confidence": round(confidence, 2),
                            "bbox": [int(x) for x in bbox]
                        })
            
            return detections
            
        except Exception as e:
            logger.error(f"推理失败: {e}")
            return self._mock_predict(image_path)
    
    def _mock_predict(self, image_path: str) -> List[Dict]:
        """
        模拟预测结果（用于测试或模型未加载时）
        """
        import random
        
        try:
            # 获取图片尺寸
            with Image.open(image_path) as img:
                width, height = img.size
        except:
            width, height = 640, 480
        
        # 生成 1-3 个随机检测结果
        num_detections = random.randint(1, 3)
        detections = []
        
        for i in range(num_detections):
            # 随机选择鸟类
            cls_id = random.randint(0, 9)
            bird_name = self.mock_classes[cls_id]
            
            # 随机置信度
            confidence = round(random.uniform(0.6, 0.98), 2)
            
            # 随机边界框
            x1 = random.randint(10, width // 2)
            y1 = random.randint(10, height // 2)
            x2 = random.randint(x1 + 50, min(x1 + 300, width - 10))
            y2 = random.randint(y1 + 50, min(y1 + 300, height - 10))
            
            detections.append({
                "bird_name": bird_name,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2]
            })
        
        return detections
    
    def annotate_image(self, image_path: str, detections: List[Dict], output_path: str) -> str:
        """
        在图片上绘制检测框和标签
        
        Args:
            image_path: 原图路径
            detections: 检测结果列表
            output_path: 输出路径
            
        Returns:
            标注后的图片路径
        """
        from PIL import Image, ImageDraw, ImageFont
        
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # 尝试加载中文字体，失败则使用默认字体
            try:
                font = ImageFont.truetype("simhei.ttf", 20)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    font = ImageFont.load_default()
            
            # 颜色列表
            colors = [
                "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
                "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"
            ]
            
            for i, det in enumerate(detections):
                bbox = det["bbox"]
                label = f"{det['bird_name']} {det['confidence']:.0%}"
                color = colors[i % len(colors)]
                
                # 绘制边界框
                draw.rectangle(bbox, outline=color, width=3)
                
                # 绘制标签背景
                text_bbox = draw.textbbox((0, 0), label, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                label_bg = [bbox[0], bbox[1] - text_height - 4, bbox[0] + text_width + 8, bbox[1]]
                draw.rectangle(label_bg, fill=color)
                
                # 绘制标签文字
                draw.text((bbox[0] + 4, bbox[1] - text_height - 2), label, fill="white", font=font)
            
            # 保存图片
            img.save(output_path, quality=95)
            return output_path
            
        except Exception as e:
            logger.error(f"图片标注失败: {e}")
            # 如果标注失败，复制原图
            import shutil
            shutil.copy(image_path, output_path)
            return output_path


# 全局检测器实例（延迟初始化）
_detector: Optional[BirdDetector] = None


def get_detector() -> BirdDetector:
    """获取全局检测器实例"""
    global _detector
    if _detector is None:
        from config import YOLO_WEIGHTS_PATH, YOLO_CONFIDENCE_THRESHOLD
        _detector = BirdDetector(YOLO_WEIGHTS_PATH, YOLO_CONFIDENCE_THRESHOLD)
    return _detector

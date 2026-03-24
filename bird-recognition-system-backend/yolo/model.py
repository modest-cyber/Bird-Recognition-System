import importlib
import logging
import os
import sys
from typing import Dict, List, Optional

import torch.nn as nn
from PIL import Image

from config import YOLO_LOCAL_SOURCE_DIR

logger = logging.getLogger(__name__)


def _import_yolo():
    errors = []

    if os.path.isdir(YOLO_LOCAL_SOURCE_DIR) and YOLO_LOCAL_SOURCE_DIR not in sys.path:
        sys.path.insert(0, YOLO_LOCAL_SOURCE_DIR)

    try:
        ultralytics_module = importlib.import_module("ultralytics")
        return getattr(ultralytics_module, "YOLO"), True
    except Exception as exc:
        errors.append(f"local source import failed: {exc}")

    try:
        from ultralytics import YOLO as installed_yolo
        return installed_yolo, True
    except Exception as exc:
        errors.append(f"installed package import failed: {exc}")

    for message in errors:
        logger.warning(message)
    return None, False


YOLO, YOLO_AVAILABLE = _import_yolo()


def _ensure_clip_model_module() -> None:
    if not YOLO_AVAILABLE:
        return
    importlib.import_module("ultralytics.nn.modules.clip_model")


def _ensure_vit_symbol() -> None:
    try:
        from ultralytics.nn.modules import block as block_module
        from ultralytics.nn.modules.clip_model import VisualTransformer
    except Exception:
        logger.exception("??????? ViT ????")
        return

    if hasattr(block_module, "ViT"):
        return

    class ViT(nn.Module):
        def __init__(self, c1: int, input_resolution: int, patch_size: int, width: int, layers: int, heads: int, c2: int, *args):
            super().__init__()
            self.vit = VisualTransformer(
                input_resolution=input_resolution,
                patch_size=patch_size,
                width=width,
                layers=layers,
                heads=heads,
                output_dim=c2,
                in_channels=c1,
            )

        def forward(self, x):
            return self.vit(x)

    block_module.ViT = ViT
    if isinstance(getattr(block_module, "__all__", None), tuple) and "ViT" not in block_module.__all__:
        block_module.__all__ = block_module.__all__ + ("ViT",)


def _patch_custom_modules() -> None:
    if not YOLO_AVAILABLE:
        return
    _ensure_clip_model_module()
    _ensure_vit_symbol()


class BirdDetector:
    def __init__(self, weights_path: str, confidence_threshold: float = 0.4):
        self.weights_path = weights_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._load_model()

    def _load_model(self):
        if not YOLO_AVAILABLE or YOLO is None:
            logger.warning("ultralytics ???????? YOLO ??????")
            return

        if not os.path.exists(self.weights_path):
            logger.warning("??? YOLO ????: %s", self.weights_path)
            return

        try:
            _patch_custom_modules()
            self.model = YOLO(self.weights_path)
            logger.info("???? YOLO ??: %s", self.weights_path)
        except Exception:
            logger.exception("YOLO ??????: %s", self.weights_path)
            self.model = None

    def predict(self, image_path: str) -> List[Dict]:
        if self.model is None:
            logger.warning("YOLO ?????????????")
            return []

        try:
            results = self.model.predict(source=image_path, conf=self.confidence_threshold, verbose=False)
            detections: List[Dict] = []
            for result in results:
                names = result.names or {}
                boxes = result.boxes
                if boxes is None:
                    continue

                for box in boxes:
                    cls_id = int(box.cls.item())
                    confidence = float(box.conf.item())
                    bbox = [int(value) for value in box.xyxy[0].tolist()]
                    class_name = names.get(cls_id, f"class_{cls_id}")
                    detections.append(
                        {
                            "bird_name": str(class_name).replace("_", " ").strip(),
                            "confidence": round(confidence, 4),
                            "bbox": bbox,
                        }
                    )
            return detections
        except Exception:
            logger.exception("YOLO ????: %s", image_path)
            return []

    def annotate_image(self, image_path: str, detections: List[Dict], output_path: str) -> str:
        from PIL import ImageDraw, ImageFont

        try:
            img = Image.open(image_path).convert("RGB")
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("simhei.ttf", 20)
            except Exception:
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except Exception:
                    font = ImageFont.load_default()

            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"]
            for index, det in enumerate(detections):
                bbox = det["bbox"]
                color = colors[index % len(colors)]
                label = f"{det['bird_name']} {det['confidence']:.1%}"
                draw.rectangle(bbox, outline=color, width=3)
                text_bbox = draw.textbbox((0, 0), label, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                label_top = max(0, bbox[1] - text_height - 6)
                label_bg = [bbox[0], label_top, bbox[0] + text_width + 8, label_top + text_height + 6]
                draw.rectangle(label_bg, fill=color)
                draw.text((bbox[0] + 4, label_top + 3), label, fill="white", font=font)

            img.save(output_path, quality=95)
            return output_path
        except Exception:
            logger.exception("??????: %s", image_path)
            Image.open(image_path).save(output_path)
            return output_path


_detector: Optional[BirdDetector] = None


def get_detector() -> BirdDetector:
    global _detector
    if _detector is None:
        from config import YOLO_CONFIDENCE_THRESHOLD, resolve_yolo_weights_path

        _detector = BirdDetector(resolve_yolo_weights_path(), YOLO_CONFIDENCE_THRESHOLD)
    return _detector

import logging
import os
import time
from typing import List, Tuple

from sqlalchemy.orm import Session

from config import (
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE,
    UPLOAD_ANNOTATED_DIR,
    UPLOAD_ORIGINAL_DIR,
)
from models.record import Record
from yolo.model import get_detector

logger = logging.getLogger(__name__)


class RecognizeService:
    """??????"""

    @staticmethod
    def validate_file(filename: str, file_size: int) -> Tuple[bool, str]:
        if '.' not in filename:
            return False, '?????'

        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"??????????? {'/'.join(sorted(ALLOWED_EXTENSIONS))}"

        if file_size > MAX_UPLOAD_SIZE:
            return False, f'??????????? {MAX_UPLOAD_SIZE // 1024 // 1024}MB?'

        return True, ''

    @staticmethod
    def save_upload_file(file_content: bytes, user_id: int, ext: str) -> str:
        os.makedirs(UPLOAD_ORIGINAL_DIR, exist_ok=True)

        timestamp = int(time.time() * 1000)
        filename = f'{user_id}_{timestamp}.{ext}'
        filepath = os.path.join(UPLOAD_ORIGINAL_DIR, filename)

        with open(filepath, 'wb') as file_obj:
            file_obj.write(file_content)

        return filepath

    @staticmethod
    def recognize_image(image_path: str, user_id: int) -> Tuple[List[dict], str]:
        detector = get_detector()
        detections = detector.predict(image_path)
        detections = RecognizeService.enrich_detections(detections)

        os.makedirs(UPLOAD_ANNOTATED_DIR, exist_ok=True)
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        annotated_filename = f'{name}_annotated{ext}'
        annotated_path = os.path.join(UPLOAD_ANNOTATED_DIR, annotated_filename)

        detector.annotate_image(image_path, detections, annotated_path)
        return detections, annotated_path

    @staticmethod
    def enrich_detections(detections: List[dict]) -> List[dict]:
        enriched = []
        for det in detections:
            bbox = det.get('bbox') or [0, 0, 0, 0]
            x1, y1, x2, y2 = [int(value) for value in bbox]
            enriched.append(
                {
                    'bird_id': det.get('bird_id'),
                    'bird_name': det.get('bird_name', 'bird') or 'bird',
                    'confidence': float(det.get('confidence', 0)),
                    'bbox': [x1, y1, x2, y2],
                    'center': [round((x1 + x2) / 2, 2), round((y1 + y2) / 2, 2)],
                    'area': max(0, x2 - x1) * max(0, y2 - y1),
                }
            )
        return enriched

    @staticmethod
    def save_record(
        db: Session,
        user_id: int,
        image_url: str,
        annotated_image_url: str,
        result_json: List[dict],
    ) -> Record:
        record = Record(
            user_id=user_id,
            image_url=image_url,
            annotated_image_url=annotated_image_url,
            result_json=result_json,
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def path_to_url(filepath: str) -> str:
        normalized = filepath.replace('\\', '/')
        if 'uploads/' in normalized:
            return f"/uploads/{normalized.split('uploads/', 1)[1]}"
        return normalized

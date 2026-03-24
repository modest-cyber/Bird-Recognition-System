from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.record import BirdDetection, RecognizeResult
from schemas.response import ResponseModel
from services.auth_service import get_current_user
from services.recognize_service import RecognizeService

router = APIRouter(prefix='/api', tags=['识别'])


@router.post('/recognize', response_model=ResponseModel)
async def recognize(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传图片并执行鸟区域识别。"""
    file_content = await file.read()
    file_size = len(file_content)

    is_valid, error_msg = RecognizeService.validate_file(file.filename, file_size)
    if not is_valid:
        return ResponseModel.error(code=400, message=error_msg)

    ext = file.filename.rsplit('.', 1)[1].lower()
    image_path = RecognizeService.save_upload_file(file_content, current_user.id, ext)

    try:
        detections, annotated_path = RecognizeService.recognize_image(image_path, current_user.id)

        original_url = RecognizeService.path_to_url(image_path)
        annotated_url = RecognizeService.path_to_url(annotated_path)

        record = RecognizeService.save_record(
            db=db,
            user_id=current_user.id,
            image_url=original_url,
            annotated_image_url=annotated_url,
            result_json=detections,
        )

        result = RecognizeResult(
            record_id=record.id,
            original_image_url=original_url,
            annotated_image_url=annotated_url,
            bird_count=len(detections),
            results=[BirdDetection(**det) for det in detections],
        )
        return ResponseModel.success(message='识别成功', data=result)
    except Exception as exc:
        return ResponseModel.error(code=500, message=f'识别失败: {exc}')

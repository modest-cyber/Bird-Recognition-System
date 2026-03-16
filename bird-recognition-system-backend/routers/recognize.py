"""
识别路由 - 图片上传识别
"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.response import ResponseModel
from schemas.record import RecognizeResult, BirdDetection
from services.auth_service import get_current_user
from services.recognize_service import RecognizeService

router = APIRouter(prefix="/api", tags=["识别"])


@router.post("/recognize", response_model=ResponseModel)
async def recognize(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传图片识别鸟类"""
    # 读取文件内容
    file_content = await file.read()
    file_size = len(file_content)
    
    # 验证文件
    is_valid, error_msg = RecognizeService.validate_file(file.filename, file_size)
    if not is_valid:
        return ResponseModel.error(code=400, message=error_msg)
    
    # 获取文件扩展名
    ext = file.filename.rsplit(".", 1)[1].lower()
    
    # 保存原图
    image_path = RecognizeService.save_upload_file(file_content, current_user.id, ext)
    
    try:
        # 执行识别
        detections, annotated_path = RecognizeService.recognize_image(image_path, current_user.id)
        
        # 匹配鸟类 ID
        detections = RecognizeService.match_bird_id(detections, db)
        
        # 转换路径为 URL
        original_url = RecognizeService.path_to_url(image_path)
        annotated_url = RecognizeService.path_to_url(annotated_path)
        
        # 保存记录
        record = RecognizeService.save_record(
            db=db,
            user_id=current_user.id,
            image_url=original_url,
            annotated_image_url=annotated_url,
            result_json=detections
        )
        
        # 构造响应
        result = RecognizeResult(
            record_id=record.id,
            original_image_url=original_url,
            annotated_image_url=annotated_url,
            results=[
                BirdDetection(
                    bird_id=det.get("bird_id"),
                    bird_name=det["bird_name"],
                    confidence=det["confidence"],
                    bbox=det["bbox"]
                )
                for det in detections
            ]
        )
        
        return ResponseModel.success(message="识别成功", data=result)
        
    except Exception as e:
        return ResponseModel.error(code=500, message=f"识别失败: {str(e)}")

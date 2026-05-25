import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.config import MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS
from app.services import storage
from app.services.model_storage import get_current_model_path
from app.api.deps import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/detect")
async def detect_pcb(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension '{ext}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {MAX_UPLOAD_SIZE // (1024*1024)}MB limit",
        )

    try:
        upload_path = storage.save_upload(contents, file.filename)
        model_path = get_current_model_path(user_id)
        result = storage.run_detection(upload_path, user_id=user_id, model_path=model_path)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")

import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.api.deps import get_current_user_id
from app.services import model_storage
from app.config import MAX_UPLOAD_SIZE

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_MODEL_SIZE = 200 * 1024 * 1024


@router.post("/models/upload")
async def upload_model(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    if not file.filename or not file.filename.endswith(".pt"):
        raise HTTPException(status_code=400, detail="仅支持 .pt 格式的模型文件")

    contents = await file.read()
    if len(contents) > MAX_MODEL_SIZE:
        raise HTTPException(status_code=400, detail="模型文件不能超过200MB")

    result = model_storage.upload_model(user_id, contents, file.filename, len(contents))
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/models/list")
async def list_models(user_id: int = Depends(get_current_user_id)):
    return model_storage.list_models(user_id)


@router.post("/models/switch")
async def switch_model(
    model_id: int,
    user_id: int = Depends(get_current_user_id),
):
    result = model_storage.switch_model(user_id, model_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: int,
    user_id: int = Depends(get_current_user_id),
):
    result = model_storage.delete_model(model_id, user_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

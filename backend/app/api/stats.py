from fastapi import APIRouter, Query, Depends

from app.config import DEFECT_CLASSES
from app.services import storage
from app.api.deps import get_current_user_id

router = APIRouter()


@router.get("/stats")
async def get_stats(user_id: int = Depends(get_current_user_id)):
    return storage.get_stats(user_id=user_id)


@router.get("/stats/trend")
async def get_stats_trend(
    days: int = Query(7, ge=1, le=90),
    user_id: int = Depends(get_current_user_id),
):
    trend = storage.get_trend(user_id=user_id, days=days)
    return {"trend": trend}


@router.get("/defect-classes")
async def get_defect_classes():
    return {"classes": DEFECT_CLASSES}

from fastapi import APIRouter, Query

from app.config import DEFECT_CLASSES
from app.services import storage

router = APIRouter()


@router.get("/stats")
async def get_stats():
    return storage.get_stats()


@router.get("/stats/trend")
async def get_stats_trend(days: int = Query(7, ge=1, le=90)):
    trend = storage.get_trend(days=days)
    return {"trend": trend}


@router.get("/defect-classes")
async def get_defect_classes():
    return {"classes": DEFECT_CLASSES}

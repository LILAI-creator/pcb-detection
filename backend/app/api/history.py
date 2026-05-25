from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends

from app.services import storage
from app.api.deps import get_current_user_id

router = APIRouter()


@router.get("/history")
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    defect_class: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user_id),
):
    return storage.get_history(
        user_id=user_id,
        page=page,
        page_size=page_size,
        defect_class=defect_class,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/history/{record_id}")
async def get_history_detail(
    record_id: str,
    user_id: int = Depends(get_current_user_id),
):
    result = storage.get_history_detail(record_id, user_id=user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return result

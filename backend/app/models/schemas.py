from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class BBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Defect(BaseModel):
    class_name: str
    confidence: float
    bbox: BBox


class DetectionResult(BaseModel):
    id: str
    image_url: str
    result_image_url: str
    timestamp: datetime
    defects: List[Defect]


class DetectionResponse(BaseModel):
    id: str
    image_url: str
    result_image_url: str
    timestamp: datetime
    defects: List[dict]


class HistoryItem(BaseModel):
    id: str
    timestamp: datetime
    defects: List[dict]


class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatsResponse(BaseModel):
    total_detections: int
    total_defects: int
    defect_rate: float
    top_defect_class: str
    class_distribution: dict


class TrendItem(BaseModel):
    date: str
    count: int


class TrendResponse(BaseModel):
    trend: List[TrendItem]


class DefectClassesResponse(BaseModel):
    classes: dict

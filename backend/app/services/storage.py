import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from sqlalchemy import func

from app.config import UPLOADS_DIR, RESULTS_DIR
from app.database import SessionLocal
from app.models.db_models import DetectionRecord, Defect
from app.services.detector import detect

CLASS_COLORS = {
    "missing_hole": (0, 0, 255),
    "mouse_bite": (0, 165, 255),
    "open_circuit": (0, 255, 255),
    "short": (0, 255, 0),
    "spur": (0, 140, 255),
    "spurious_copper": (255, 0, 180),
}


def save_upload(file_bytes: bytes, filename: str) -> Path:
    ext = Path(filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    path = UPLOADS_DIR / unique_name
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path


def save_result_image(image: np.ndarray, defects: list) -> Path:
    result_img = image.copy()
    h, w = result_img.shape[:2]
    scale = max(w, h) / 1000.0
    font_scale = max(0.6, scale * 0.5)
    thickness = max(1, int(scale * 1.2))
    box_thickness = max(2, int(scale * 1.5))

    for det in defects:
        bbox = det.get("bbox", {})
        x1 = int(bbox.get("x", 0))
        y1 = int(bbox.get("y", 0))
        x2 = int(x1 + bbox.get("width", 0))
        y2 = int(y1 + bbox.get("height", 0))
        color = CLASS_COLORS.get(det.get("class"), (94, 86, 214))

        cv2.rectangle(result_img, (x1, y1), (x2, y2), color, box_thickness)

        label = f"{det.get('class', 'unknown')} {det.get('confidence', 0) * 100:.1f}%"
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        label_y = max(y1, th + baseline + 6)
        cv2.rectangle(result_img, (x1, label_y - th - baseline - 4), (x1 + tw + 4, label_y), color, -1)
        cv2.putText(result_img, label, (x1 + 2, label_y - baseline - 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

    unique_name = f"{uuid.uuid4().hex}.jpg"
    path = RESULTS_DIR / unique_name
    cv2.imwrite(str(path), result_img)
    return path


def _defect_orm_to_dict(d: Defect) -> dict:
    return {
        "class": d.class_name,
        "confidence": d.confidence,
        "bbox": {
            "x": d.bbox_x,
            "y": d.bbox_y,
            "width": d.bbox_width,
            "height": d.bbox_height,
        },
    }


def _record_orm_to_dict(r: DetectionRecord) -> dict:
    return {
        "id": r.id,
        "image_url": r.image_url,
        "result_image_url": r.result_image_url,
        "timestamp": r.timestamp.isoformat(),
        "defects": [_defect_orm_to_dict(d) for d in r.defects],
    }


def run_detection(upload_path: Path, user_id: int, model_path: Optional[str] = None) -> dict:
    image = cv2.imread(str(upload_path))
    if image is None:
        raise ValueError("Failed to read image file")

    defects = detect(image, model_path=model_path)

    result_path = save_result_image(image, defects)

    record_id = uuid.uuid4().hex
    now = datetime.now()

    db = SessionLocal()
    try:
        record = DetectionRecord(
            id=record_id,
            user_id=user_id,
            image_url=f"/uploads/{upload_path.name}",
            result_image_url=f"/results/{result_path.name}",
            timestamp=now,
        )
        for det in defects:
            bbox = det.get("bbox", {})
            defect = Defect(
                record_id=record_id,
                class_name=det.get("class", "unknown"),
                confidence=det.get("confidence", 0.0),
                bbox_x=bbox.get("x", 0),
                bbox_y=bbox.get("y", 0),
                bbox_width=bbox.get("width", 0),
                bbox_height=bbox.get("height", 0),
            )
            record.defects.append(defect)

        db.add(record)
        db.commit()
        db.refresh(record)

        return _record_orm_to_dict(record)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_history(
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    defect_class: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    db = SessionLocal()
    try:
        query = db.query(DetectionRecord).filter(DetectionRecord.user_id == user_id)

        if defect_class:
            query = query.join(Defect).filter(Defect.class_name == defect_class).distinct()

        if start_date:
            query = query.filter(DetectionRecord.timestamp >= start_date)
        if end_date:
            query = query.filter(DetectionRecord.timestamp <= end_date + "T23:59:59")

        query = query.order_by(DetectionRecord.timestamp.desc())
        total = query.count()
        total_pages = max(1, (total + page_size - 1) // page_size)
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return {
            "items": [_record_orm_to_dict(r) for r in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    finally:
        db.close()


def get_history_detail(record_id: str, user_id: int) -> Optional[dict]:
    db = SessionLocal()
    try:
        record = db.query(DetectionRecord).filter(
            DetectionRecord.id == record_id,
            DetectionRecord.user_id == user_id,
        ).first()
        if record is None:
            return None
        return _record_orm_to_dict(record)
    finally:
        db.close()


def get_stats(user_id: int) -> dict:
    db = SessionLocal()
    try:
        total_detections = db.query(DetectionRecord).filter(DetectionRecord.user_id == user_id).count()

        class_count_rows = (
            db.query(Defect.class_name, func.count(Defect.id))
            .join(DetectionRecord)
            .filter(DetectionRecord.user_id == user_id)
            .group_by(Defect.class_name)
            .all()
        )
        class_count = {row[0]: row[1] for row in class_count_rows}

        total_defects = sum(class_count.values())
        defect_rate = total_defects / total_detections if total_detections > 0 else 0.0
        top_class = max(class_count, key=class_count.get) if class_count else ""

        return {
            "total_detections": total_detections,
            "total_defects": total_defects,
            "defect_rate": round(defect_rate, 4),
            "top_defect_class": top_class,
            "class_distribution": class_count,
        }
    finally:
        db.close()


def get_trend(user_id: int, days: int = 7) -> list:
    db = SessionLocal()
    try:
        now = datetime.now()
        trend = []

        for i in range(days - 1, -1, -1):
            date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            date_start = datetime.strptime(date, "%Y-%m-%d")
            date_end = date_start + timedelta(days=1)
            count = (
                db.query(DetectionRecord)
                .filter(DetectionRecord.user_id == user_id)
                .filter(DetectionRecord.timestamp >= date_start)
                .filter(DetectionRecord.timestamp < date_end)
                .count()
            )
            trend.append({"date": date, "count": count})

        return trend
    finally:
        db.close()

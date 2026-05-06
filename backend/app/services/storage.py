import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import cv2
import numpy as np

from app.config import UPLOADS_DIR, RESULTS_DIR
from app.services.detector import detect

DB_FILE = UPLOADS_DIR / "history_db.json"

CLASS_COLORS = {
    "missing_hole": (0, 59, 255),
    "mouse_bite": (0, 149, 255),
    "open_circuit": (0, 204, 255),
    "short": (89, 199, 52),
    "spur": (255, 127, 0),
    "spurious_copper": (222, 82, 175),
}


def _load_db() -> list:
    if DB_FILE.exists():
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_db(data: list):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_upload(file_bytes: bytes, filename: str) -> Path:
    ext = Path(filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    path = UPLOADS_DIR / unique_name
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path


def save_result_image(image: np.ndarray, defects: list) -> Path:
    result_img = image.copy()
    for det in defects:
        bbox = det.get("bbox", {})
        x1 = int(bbox.get("x", 0))
        y1 = int(bbox.get("y", 0))
        x2 = int(x1 + bbox.get("width", 0))
        y2 = int(y1 + bbox.get("height", 0))
        color = CLASS_COLORS.get(det.get("class"), (94, 86, 214))

        cv2.rectangle(result_img, (x1, y1), (x2, y2), color, 2)

        label = f"{det.get('class', 'unknown')} {det.get('confidence', 0) * 100:.1f}%"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(result_img, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(result_img, label, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    unique_name = f"{uuid.uuid4().hex}.jpg"
    path = RESULTS_DIR / unique_name
    cv2.imwrite(str(path), result_img)
    return path


def run_detection(upload_path: Path) -> dict:
    image = cv2.imread(str(upload_path))
    if image is None:
        raise ValueError("Failed to read image file")

    defects = detect(image)

    result_path = save_result_image(image, defects)

    record_id = uuid.uuid4().hex
    now = datetime.now()

    record = {
        "id": record_id,
        "image_url": f"/uploads/{upload_path.name}",
        "result_image_url": f"/results/{result_path.name}",
        "timestamp": now.isoformat(),
        "defects": defects,
    }

    db = _load_db()
    db.insert(0, record)
    _save_db(db)

    return record


def get_history(
    page: int = 1,
    page_size: int = 10,
    defect_class: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    db = _load_db()

    if defect_class:
        db = [r for r in db if any(d.get("class") == defect_class for d in r.get("defects", []))]

    if start_date:
        db = [r for r in db if r["timestamp"] >= start_date]
    if end_date:
        db = [r for r in db if r["timestamp"] <= end_date + "T23:59:59"]

    total = len(db)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    items = db[start : start + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def get_history_detail(record_id: str) -> Optional[dict]:
    db = _load_db()
    for r in db:
        if r["id"] == record_id:
            return r
    return None


def get_stats() -> dict:
    db = _load_db()
    total_detections = len(db)
    class_count = {}

    for r in db:
        for d in r.get("defects", []):
            cls = d.get("class", "unknown")
            class_count[cls] = class_count.get(cls, 0) + 1

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


def get_trend(days: int = 7) -> list:
    from datetime import timedelta

    db = _load_db()
    now = datetime.now()
    trend = []

    for i in range(days - 1, -1, -1):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        count = sum(
            1
            for r in db
            if r["timestamp"].startswith(date)
        )
        trend.append({"date": date, "count": count})

    return trend

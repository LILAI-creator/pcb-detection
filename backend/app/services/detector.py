import logging
from pathlib import Path
from typing import List, Optional

import numpy as np

from app.config import MODEL_PATH, CONFIDENCE_THRESHOLD, IOU_THRESHOLD, DEFECT_CLASSES

logger = logging.getLogger(__name__)

_model = None


def load_model(model_path: Optional[str] = None):
    global _model
    path = Path(model_path) if model_path else MODEL_PATH

    if not path.exists():
        logger.warning(f"Model file not found: {path}. Detector will run in mock mode.")
        _model = None
        return

    try:
        from ultralytics import YOLO
        _model = YOLO(str(path))
        logger.info(f"YOLOv8 model loaded from: {path}")
    except ImportError:
        logger.warning("ultralytics not installed. Detector will run in mock mode.")
        _model = None
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        _model = None


def detect(
    image: np.ndarray,
    conf_threshold: Optional[float] = None,
    iou_threshold: Optional[float] = None,
) -> List[dict]:
    conf = conf_threshold or CONFIDENCE_THRESHOLD
    iou = iou_threshold or IOU_THRESHOLD

    if _model is None:
        return _mock_detect(image)

    try:
        results = _model.predict(
            source=image,
            conf=conf,
            iou=iou,
            verbose=False,
        )
        return _parse_results(results[0])
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise RuntimeError(f"Detection inference failed: {e}")


def _parse_results(result) -> List[dict]:
    defects = []
    boxes = result.boxes
    if boxes is None:
        return defects

    for i in range(len(boxes)):
        xyxy = boxes.xyxy[i].cpu().numpy()
        cls_id = int(boxes.cls[i].cpu().numpy())
        confidence = float(boxes.conf[i].cpu().numpy())

        class_name = DEFECT_CLASSES.get(cls_id, f"class_{cls_id}")

        bbox = {
            "x": float(xyxy[0]),
            "y": float(xyxy[1]),
            "width": float(xyxy[2] - xyxy[0]),
            "height": float(xyxy[3] - xyxy[1]),
        }

        defects.append({
            "class": class_name,
            "confidence": round(confidence, 4),
            "bbox": bbox,
        })

    return defects


def _mock_detect(image: np.ndarray) -> List[dict]:
    logger.info("Running mock detection (no model loaded)")
    h, w = image.shape[:2]
    return [
        {
            "class": "missing_hole",
            "confidence": 0.85,
            "bbox": {"x": w * 0.2, "y": h * 0.3, "width": w * 0.1, "height": h * 0.08},
        },
        {
            "class": "short",
            "confidence": 0.72,
            "bbox": {"x": w * 0.5, "y": h * 0.5, "width": w * 0.12, "height": h * 0.06},
        },
    ]


def is_loaded() -> bool:
    return _model is not None

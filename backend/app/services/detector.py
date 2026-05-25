import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np

from app.config import MODEL_PATH, CONFIDENCE_THRESHOLD, IOU_THRESHOLD

logger = logging.getLogger(__name__)

_model_available = None

_YOLO_SCRIPT = r"""
import sys
import json
import os

image_path = sys.argv[1]
model_path = sys.argv[2]
conf = float(sys.argv[3])
iou = float(sys.argv[4])

import torch
device = "0" if torch.cuda.is_available() else "cpu"

from ultralytics import YOLO
model = YOLO(model_path)
results = model.predict(source=image_path, conf=conf, iou=iou, device=device, verbose=False)

r = results[0]
boxes = r.boxes
defects = []
if boxes is not None:
    for i in range(len(boxes)):
        xyxy = boxes.xyxy[i].cpu().numpy()
        cls_id = int(boxes.cls[i].cpu().numpy())
        confidence = float(boxes.conf[i].cpu().numpy())
        class_name = model.names.get(cls_id, str(cls_id))
        bbox = {
            "x": float(xyxy[0]),
            "y": float(xyxy[1]),
            "width": float(xyxy[2] - xyxy[0]),
            "height": float(xyxy[3] - xyxy[1]),
        }
        defects.append({"class": class_name, "confidence": round(confidence, 4), "bbox": bbox})

print(json.dumps(defects, ensure_ascii=False))
"""


def load_model(model_path: Optional[str] = None):
    global _model_available
    path = Path(model_path) if model_path else MODEL_PATH

    if not path.exists():
        logger.warning(f"Model file not found: {path}. Detector will run in mock mode.")
        _model_available = False
        return

    try:
        result = subprocess.run(
            [sys.executable, "-c", "import ultralytics; print('ok')"],
            capture_output=True, text=True, timeout=30,
        )
        if "ok" in result.stdout:
            _model_available = True
            logger.info(f"YOLOv8 model available at: {path} (subprocess mode, GPU auto-detect)")
        else:
            _model_available = False
            logger.warning("ultralytics import failed in subprocess. Running in mock mode.")
    except Exception as e:
        _model_available = False
        logger.warning(f"Model check failed: {e}. Running in mock mode.")


def detect(
    image: np.ndarray,
    conf_threshold: Optional[float] = None,
    iou_threshold: Optional[float] = None,
    model_path: Optional[str] = None,
) -> List[dict]:
    conf = conf_threshold or CONFIDENCE_THRESHOLD
    iou = iou_threshold or IOU_THRESHOLD
    use_model = model_path if model_path else str(MODEL_PATH)

    if not _model_available:
        return _mock_detect(image)

    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
            cv2.imwrite(tmp_path, image)

        result = subprocess.run(
            [sys.executable, "-c", _YOLO_SCRIPT, tmp_path, use_model, str(conf), str(iou)],
            capture_output=True, text=True, timeout=120,
        )

        try:
            os.unlink(tmp_path)
        except Exception:
            pass

        if result.returncode != 0:
            logger.error(f"Subprocess detection failed: {result.stderr}")
            raise RuntimeError(f"Detection subprocess failed: {result.stderr[:200]}")

        defects = json.loads(result.stdout.strip())
        return defects

    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise RuntimeError(f"Detection inference failed: {e}")


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
    return _model_available is True

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

WEIGHTS_DIR = BASE_DIR / "weights"
UPLOADS_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"

MODEL_PATH = WEIGHTS_DIR / os.getenv("PCB_MODEL_NAME", "best.pt")

CONFIDENCE_THRESHOLD = float(os.getenv("PCB_CONF_THRESHOLD", "0.25"))
IOU_THRESHOLD = float(os.getenv("PCB_IOU_THRESHOLD", "0.45"))

MAX_UPLOAD_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

HOST = os.getenv("PCB_HOST", "0.0.0.0")
PORT = int(os.getenv("PCB_PORT", "8000"))

CORS_ORIGINS = os.getenv("PCB_CORS_ORIGINS", "*").split(",")

DEFECT_CLASSES = {
    0: "missing_hole",
    1: "mouse_bite",
    2: "open_circuit",
    3: "short",
    4: "spur",
    5: "spurious_copper",
}

for d in [WEIGHTS_DIR, UPLOADS_DIR, RESULTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

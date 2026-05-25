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

DB_DRIVER = os.getenv("PCB_DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_HOST = os.getenv("PCB_DB_HOST", "localhost\\SQLEXPRESS")
DB_PORT = os.getenv("PCB_DB_PORT", "")
DB_NAME = os.getenv("PCB_DB_NAME", "pcb_detector")
DB_USER = os.getenv("PCB_DB_USER", "sa")
DB_PASSWORD = os.getenv("PCB_DB_PASSWORD", "h4fFwT77dNQj")

JWT_SECRET = os.getenv("PCB_JWT_SECRET", "pcb_detector_jwt_secret_key_2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("PCB_JWT_EXPIRE_MINUTES", "1440"))

if DB_PORT:
    _db_host_port = f"{DB_HOST},{DB_PORT}"
else:
    _db_host_port = DB_HOST

DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{_db_host_port}/{DB_NAME}"
    f"?driver={DB_DRIVER}"
)

for d in [WEIGHTS_DIR, UPLOADS_DIR, RESULTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

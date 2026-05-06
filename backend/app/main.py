import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pathlib import Path

from app.config import CORS_ORIGINS, UPLOADS_DIR, RESULTS_DIR

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
from app.api import detect, history, stats
from app.services.detector import load_model, is_loaded

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading YOLOv8 model...")
    load_model()
    if is_loaded():
        logger.info("Model loaded successfully")
    else:
        logger.warning("No model loaded - running in mock mode")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="PCB Defect Detection API",
    description="Web PCB板缺陷检测后端服务，基于YOLOv8",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(stats.router, prefix="/api")

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


@app.get("/")
async def root():
    if FRONTEND_DIR.exists():
        return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/{page_name}")
async def serve_page(page_name: str):
    if FRONTEND_DIR.exists() and page_name in ("history.html", "stats.html"):
        return FileResponse(str(FRONTEND_DIR / page_name))
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"detail": "Not found"})

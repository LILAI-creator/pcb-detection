import os
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import MODEL_PATH
from app.database import SessionLocal
from app.models.db_models import ModelInfo, UserCurrentModel

USER_MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "weights" / "user_models"
USER_MODELS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL_NAME = "默认模型 (best.pt)"


def save_model_file(file_bytes: bytes, filename: str) -> Path:
    unique_name = f"{uuid.uuid4().hex}.pt"
    path = USER_MODELS_DIR / unique_name
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path


def validate_model(model_path: str) -> bool:
    try:
        escaped_path = model_path.replace("\\", "\\\\")
        result = subprocess.run(
            [sys.executable, "-c",
             f"from ultralytics import YOLO; m=YOLO('{escaped_path}'); print('ok')"],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
        )
        return "ok" in result.stdout
    except Exception:
        return False


def get_current_model_path(user_id: int) -> str:
    db = SessionLocal()
    try:
        ucm = db.query(UserCurrentModel).filter(UserCurrentModel.user_id == user_id).first()
        if ucm:
            model = db.query(ModelInfo).filter(ModelInfo.id == ucm.model_id).first()
            if model and Path(model.file_path).exists():
                return model.file_path
        return str(MODEL_PATH)
    finally:
        db.close()


def get_current_model_info(user_id: int) -> Optional[dict]:
    db = SessionLocal()
    try:
        ucm = db.query(UserCurrentModel).filter(UserCurrentModel.user_id == user_id).first()
        if ucm:
            model = db.query(ModelInfo).filter(ModelInfo.id == ucm.model_id).first()
            if model:
                return {"id": model.id, "name": model.name, "is_default": model.is_default}
        return {"id": 0, "name": DEFAULT_MODEL_NAME, "is_default": True}
    finally:
        db.close()


def upload_model(user_id: int, file_bytes: bytes, filename: str, file_size: int) -> dict:
    path = save_model_file(file_bytes, filename)

    if not validate_model(str(path)):
        try:
            os.unlink(str(path))
        except Exception:
            pass
        return {"success": False, "message": "模型文件无效，无法被YOLO加载"}

    db = SessionLocal()
    try:
        model = ModelInfo(
            user_id=user_id,
            name=filename,
            file_path=str(path),
            file_size=file_size,
            is_default=False,
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return {
            "success": True,
            "id": model.id,
            "name": model.name,
            "file_size": model.file_size,
            "created_at": model.created_at.isoformat(),
        }
    except Exception as e:
        db.rollback()
        try:
            os.unlink(str(path))
        except Exception:
            pass
        return {"success": False, "message": f"保存失败: {e}"}
    finally:
        db.close()


def list_models(user_id: int) -> dict:
    db = SessionLocal()
    try:
        models = db.query(ModelInfo).filter(ModelInfo.user_id == user_id).order_by(ModelInfo.created_at.desc()).all()

        default_exists = any(m.is_default for m in models)
        if not default_exists:
            default_model = ModelInfo(
                user_id=user_id,
                name=DEFAULT_MODEL_NAME,
                file_path=str(MODEL_PATH),
                file_size=MODEL_PATH.stat().st_size if MODEL_PATH.exists() else 0,
                is_default=True,
            )
            db.add(default_model)
            db.commit()
            db.refresh(default_model)
            models = [default_model] + list(models)

        ucm = db.query(UserCurrentModel).filter(UserCurrentModel.user_id == user_id).first()
        current_model_id = ucm.model_id if ucm else 0

        if current_model_id == 0:
            for m in models:
                if m.is_default:
                    current_model_id = m.id
                    break

        items = []
        for m in models:
            items.append({
                "id": m.id,
                "name": m.name,
                "file_size": m.file_size,
                "is_default": m.is_default,
                "is_active": m.id == current_model_id,
                "created_at": m.created_at.isoformat(),
            })

        return {"items": items, "current_model_id": current_model_id}
    finally:
        db.close()


def switch_model(user_id: int, model_id: int) -> dict:
    db = SessionLocal()
    try:
        model = db.query(ModelInfo).filter(ModelInfo.id == model_id).first()
        if not model:
            return {"success": False, "message": "模型不存在"}

        if not Path(model.file_path).exists():
            return {"success": False, "message": "模型文件已丢失"}

        ucm = db.query(UserCurrentModel).filter(UserCurrentModel.user_id == user_id).first()
        if ucm:
            ucm.model_id = model_id
            ucm.updated_at = datetime.now()
        else:
            ucm = UserCurrentModel(user_id=user_id, model_id=model_id)
            db.add(ucm)

        db.commit()
        return {
            "success": True,
            "current_model_id": model_id,
            "current_model_name": model.name,
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"切换失败: {e}"}
    finally:
        db.close()


def delete_model(model_id: int, user_id: int) -> dict:
    db = SessionLocal()
    try:
        model = db.query(ModelInfo).filter(ModelInfo.id == model_id, ModelInfo.user_id == user_id).first()
        if not model:
            return {"success": False, "message": "模型不存在"}

        if model.is_default:
            return {"success": False, "message": "不能删除默认模型"}

        ucm = db.query(UserCurrentModel).filter(UserCurrentModel.user_id == user_id).first()
        if ucm and ucm.model_id == model_id:
            return {"success": False, "message": "正在使用的模型不能删除，请先切换"}

        try:
            os.unlink(model.file_path)
        except Exception:
            pass

        db.delete(model)
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"删除失败: {e}"}
    finally:
        db.close()

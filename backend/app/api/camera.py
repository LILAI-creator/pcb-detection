import asyncio
import base64
import json
import logging
from typing import Optional

import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.api.deps import get_current_user_id
from app.services.detector import detect, is_loaded

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/camera")
async def camera_detect(ws: WebSocket):
    await ws.accept()

    token_str = ws.query_params.get("token", "")
    if not token_str:
        await ws.close(code=4001, reason="Not authenticated")
        return

    from app.services import auth
    username = auth.decode_access_token(token_str)
    if not username:
        await ws.close(code=4001, reason="Invalid token")
        return

    try:
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                await ws.send_json({"error": "Invalid JSON"})
                continue

            image_b64 = msg.get("image", "")
            if not image_b64:
                await ws.send_json({"error": "No image data"})
                continue

            try:
                image_bytes = base64.b64decode(image_b64)
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if image is None:
                    await ws.send_json({"error": "Failed to decode image"})
                    continue

                defects = detect(image)

                await ws.send_json({"defects": defects, "count": len(defects)})

            except Exception as e:
                logger.error(f"Detection error in websocket: {e}")
                await ws.send_json({"error": str(e)})

    except WebSocketDisconnect:
        logger.info("Camera WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            await ws.close()
        except Exception:
            pass

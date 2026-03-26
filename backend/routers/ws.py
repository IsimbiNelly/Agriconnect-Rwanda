from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError

from backend.config.settings import settings
from backend.utils.ws_manager import ws_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str = Query(...)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        await ws.close(code=1008)
        return

    await ws_manager.connect(user_id, ws)
    try:
        while True:
            await ws.receive_text()   # keep-alive; client pings ignored
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, ws)

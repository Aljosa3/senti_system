from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import json
import asyncio

from senti_os.core.faza22.service_registry import ServiceRegistry
from senti_os.core.faza22.logs_manager import LogsManager

websocket_app = FastAPI()
logs_manager = LogsManager()

@websocket_app.websocket("/system")
async def websocket_system(ws: WebSocket):
    await ws.accept()
    manager = ServiceRegistry().get_boot_manager()

    try:
        while True:
            status = manager.get_status()
            await ws.send_text(json.dumps(status))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return

@websocket_app.websocket("/logs")
async def websocket_logs(ws: WebSocket):
    await ws.accept()
    last_count = 0

    try:
        while True:
            logs = logs_manager.get_logs(limit=50)
            if len(logs) != last_count:
                await ws.send_text(json.dumps(logs))
                last_count = len(logs)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return

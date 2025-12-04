from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from senti_os.core.faza24.api_routes import router as api_router
from senti_os.core.faza24.websocket_server import websocket_app

app = FastAPI(title="Senti OS Web Dashboard", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix="/api")

# WebSocket
app.mount("/ws", websocket_app)

# Static files
app.mount("/", StaticFiles(directory="/home/pisarna/senti_system/senti_os/core/faza24/static", html=True), name="static")


def start_web(host="0.0.0.0", port=8123):
    uvicorn.run("senti_os.core.faza24.web_server:app", host=host, port=port, reload=False)

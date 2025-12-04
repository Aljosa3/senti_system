from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os

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

# PATHS - Correctly point to static directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Verify static directory exists
if not os.path.exists(STATIC_DIR):
    raise RuntimeError(f"Static directory not found: {STATIC_DIR}")

# ROOT ROUTE (SERVE DASHBOARD UI) - Must be defined before static mount
@app.get("/")
async def serve_dashboard():
    dashboard_path = os.path.join(STATIC_DIR, "dashboard.html")
    if not os.path.exists(dashboard_path):
        raise RuntimeError(f"Dashboard HTML not found: {dashboard_path}")
    return FileResponse(dashboard_path)

# API ROUTES - Include before mounts
app.include_router(api_router, prefix="/api")

# STATIC FILES (CSS, JS) - Mount after routes, before websocket
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# WEBSOCKET - Mount last to avoid path conflicts
app.mount("/ws", websocket_app)


def start_web():
    """Start the FastAPI web server on port 8123"""
    uvicorn.run(app, host="0.0.0.0", port=8123)

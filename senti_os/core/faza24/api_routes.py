from fastapi import APIRouter
from senti_os.core.faza22.service_registry import ServiceRegistry
from senti_os.core.faza22.logs_manager import LogsManager

router = APIRouter()
logs_manager = LogsManager()

@router.get("/status")
def get_status():
    manager = ServiceRegistry().get_boot_manager()
    return manager.get_status()

@router.get("/logs")
def get_logs(limit: int = 100):
    return logs_manager.get_logs(limit=limit)

@router.get("/events")
def get_events():
    manager = ServiceRegistry().get_boot_manager()
    return manager.get_status().get("events", {})

@router.get("/stacks")
def get_stacks():
    manager = ServiceRegistry().get_boot_manager()
    return manager.get_status().get("stacks", {})

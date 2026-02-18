from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "chat-backend"
    }

@router.get("/ready")
def readiness_check():
    """Readiness check for container orchestration"""
    # In a real implementation, you might check database connectivity,
    # external service availability, etc.
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "chat-backend"
    }

@router.get("/live")
def liveness_check():
    """Liveness check for container orchestration"""
    # Simple liveness check - just return healthy if the service is responding
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "chat-backend"
    }
from pydantic import BaseModel
from typing import Dict, Any, Optional

class ErrorResponse(BaseModel):
    """
    Standardized error response format as specified in the requirements:
    { "error": "message", "code": "error_code", "details": {} }
    """
    error: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = {}

class HealthResponse(BaseModel):
    """
    Health check response
    """
    status: str
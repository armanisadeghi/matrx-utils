from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class HealthResponse(BaseModel):
    """Health check response model"""
    status: bool
    timestamp: float
    service: str
    version: str
    environment: str
    checks: Dict[str, Any]

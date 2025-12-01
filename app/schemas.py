# app/schemas.py
from pydantic import BaseModel
from typing import Dict, Optional, List, Any

class AnalyzeResponse(BaseModel):
    analysis_id: str
    topicsMap: Dict[str, int]
    summary: Optional[str] = None
    raw: Optional[Any] = None

class HealthResponse(BaseModel):
    status: str = "ok"

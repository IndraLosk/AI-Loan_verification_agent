# app/schemas.py
from pydantic import BaseModel, UUID4
from typing import List, Dict, Any, Optional
from datetime import datetime

class Issue(BaseModel):
    level: str   # "error" или "warning"
    message: str

class DocumentInfo(BaseModel):
    name: str
    detected_type: Optional[str]
    size_kb: float

class CheckResponse(BaseModel):
    check_id: UUID4
    status: str
    status_label: str
    reason: Optional[str] = None
    issues: List[Issue] = []
    documents: List[DocumentInfo] = []
    extracted: Dict[str, Any] = {}
    checked_at: datetime

class CheckListResponse(BaseModel):
    id: UUID4
    program: str
    status: str
    checked_at: datetime
    documents_count: int
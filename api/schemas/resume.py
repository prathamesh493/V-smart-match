from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from datetime import datetime

class ResumeUploadRequest(BaseModel):
    """Schema for resume upload request"""
    user_id: str = Field(..., description="User ID for storing the resume data")

class ResumeResponse(BaseModel):
    """Schema for parsed resume response"""
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    file_name: str
    extracted_content: str
    format: str = "markdown"
    doc_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
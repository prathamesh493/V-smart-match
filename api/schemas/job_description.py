from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from datetime import datetime

class JobDescriptionUploadRequest(BaseModel):
    """Schema for job description upload request"""
    user_id: str = Field(..., description="User ID for storing the job description data")
    job_title: Optional[str] = Field(None, description="Title of the job")
    company: Optional[str] = Field(None, description="Company offering the job")

class JobDescriptionResponse(BaseModel):
    """Schema for parsed job description response"""
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    file_name: str
    extracted_content: str
    format: str = "markdown"
    doc_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
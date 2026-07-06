"""
Schemas for dashboard-related functionality
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total_matches: int = 0
    accepted_matches: int = 0
    pending_matches: int = 0
    rejected_matches: int = 0
    average_score: float = 0.0
    highest_score: float = 0.0
    recent_activity_count: int = 0

class JobMatchSummary(BaseModel):
    """Schema for job match summary in dashboard"""
    job_title: str
    company_name: Optional[str] = None
    match_count: int = 0
    accepted_count: int = 0
    pending_count: int = 0
    rejected_count: int = 0
    average_score: float = 0.0

class RecruiterActivity(BaseModel):
    """Schema for recruiter activity in dashboard"""
    recruiter_id: str
    recruiter_name: Optional[str] = None
    total_matches_created: int = 0
    matches_accepted: int = 0
    matches_rejected: int = 0
    average_response_time_hours: Optional[float] = None
    last_activity: Optional[datetime] = None

class DashboardInsights(BaseModel):
    """Schema for dashboard insights and analytics"""
    stats: DashboardStats
    top_job_matches: List[JobMatchSummary] = []
    recruiter_activities: List[RecruiterActivity] = []
    skill_demand: Dict[str, int] = Field(default_factory=dict)
    monthly_trends: Dict[str, int] = Field(default_factory=dict)

class NextStepAction(BaseModel):
    """Schema for next step actions available to candidate"""
    action_type: str = Field(..., description="Type of action: interview, assessment, document_upload, etc.")
    title: str = Field(..., description="Display title for the action")
    description: Optional[str] = Field(None, description="Detailed description")
    due_date: Optional[datetime] = Field(None, description="Deadline for the action")
    priority: str = Field(default="medium", description="Priority level: low, medium, high")
    action_url: Optional[str] = Field(None, description="URL for the action if applicable")
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
        return v

class CandidateMatchDetailed(BaseModel):
    """Schema for detailed candidate match information"""
    match_id: str
    job_title: str
    company_name: Optional[str] = None
    job_description_id: str
    recruiter_id: str
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    overall_score: float = Field(..., ge=0, le=100)
    category_scores: Optional[Dict[str, Any]] = None
    status: str = Field(default="pending")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    next_steps: List[NextStepAction] = []
    recruiter_notes: Optional[str] = None
    job_summary: Optional[str] = None
    required_skills: List[str] = []
    matched_skills: List[str] = []
    missing_skills: List[str] = []
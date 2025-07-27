from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

class ResumeProfile(BaseModel):
    """Schema for resume data in unified profile"""
    id: str
    extracted_content: Optional[str] = None
    timestamp: Optional[datetime] = None
    # Additional fields could be added for specific resume data points
    file_name: Optional[str] = None

class GithubSummary(BaseModel):
    """Schema for GitHub data in unified profile"""
    id: Optional[str] = None
    username: str
    timestamp: Optional[datetime] = None
    top_languages: Optional[List[str]] = None
    activity: Optional[Dict[str, int]] = None

class LeetcodeSummary(BaseModel):
    """Schema for LeetCode data in unified profile"""
    username: str
    timestamp: Optional[datetime] = None
    problems_solved: Optional[Dict[str, int]] = None
    # Could include other LeetCode stats like ranking, streak, etc.

class ProfileLinkRequest(BaseModel):
    """Schema for linking candidate profile types"""
    user_id: Optional[str] = Field(None, description="User ID for the candidate (optional, defaults to authenticated user)")
    resume_id: Optional[str] = Field(None, description="ID of the candidate's resume document")
    github_profile_id: Optional[str] = Field(None, description="ID of the candidate's GitHub profile document")
    github_username: Optional[str] = Field(None, description="Candidate's GitHub username")
    leetcode_username: Optional[str] = Field(None, description="Candidate's LeetCode username")

class UnifiedCandidateProfile(BaseModel):
    """Schema for the unified candidate profile"""
    user_id: str
    last_updated: datetime = Field(default_factory=datetime.now)
    resume: Optional[ResumeProfile] = None
    github: Optional[GithubSummary] = None
    leetcode: Optional[LeetcodeSummary] = None
    
    class Config:
        # Allow arbitrary types for flexibility
        arbitrary_types_allowed = True
        # Convert datetime to string in json representation
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class ProfileLinkResponse(BaseModel):
    """Schema for the response when profiles are linked"""
    message: str
    user_id: str
    linked_profiles: Dict[str, str]

class CandidateSearchParams(BaseModel):
    """Schema for candidate search parameters"""
    github_language: Optional[str] = None
    leetcode_problems_min: Optional[int] = None
    has_resume: Optional[bool] = None
    skills: Optional[List[str]] = None
    limit: int = 10

class Education(BaseModel):
    """Schema for candidate education"""
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    
class Experience(BaseModel):
    """Schema for candidate experience"""
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class CandidateReport(BaseModel):
    """Schema for comprehensive candidate report"""
    user_id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    skills: Optional[List[str]] = None
    education: Optional[List[Education]] = None
    experience: Optional[List[Experience]] = None
    
    # Resume data
    has_resume: Optional[bool] = None
    resume_id: Optional[str] = None
    resume_timestamp: Optional[datetime] = None
    resume_content: Optional[str] = None
    
    # GitHub profile data
    has_github_profile: Optional[bool] = None
    github_username: Optional[str] = None
    github_profile_id: Optional[str] = None
    github_profile_timestamp: Optional[datetime] = None
    github_top_languages: Optional[List[str]] = None
    github_activity: Optional[Dict[str, int]] = None
    
    # LeetCode profile data
    has_leetcode_profile: Optional[bool] = None
    leetcode_username: Optional[str] = None
    leetcode_profile_timestamp: Optional[datetime] = None
    leetcode_problems_solved: Optional[Dict[str, int]] = None
    
    # Report metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        # Allow arbitrary types for flexibility
        arbitrary_types_allowed = True
        # Convert datetime to string in json representation
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        }

class CandidateDashboardRequest(BaseModel):
    """Schema for candidate dashboard request parameters"""
    include_rejected: bool = Field(default=False, description="Whether to include rejected matches")
    limit: Optional[int] = Field(default=50, description="Maximum number of matches to return")
    sort_by: str = Field(default="overall_score", description="Field to sort by")
    sort_order: str = Field(default="desc", description="Sort order: asc or desc")
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = ["overall_score", "created_at", "updated_at", "job_title"]
        if v not in allowed_fields:
            raise ValueError(f"sort_by must be one of: {', '.join(allowed_fields)}")
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v

class MatchFilters(BaseModel):
    """Schema for filtering matches in candidate dashboard"""
    status: Optional[List[str]] = Field(None, description="Filter by status: accepted, pending, rejected")
    job_title: Optional[str] = Field(None, description="Filter by job title (partial match)")
    min_score: Optional[float] = Field(None, description="Minimum overall score", ge=0, le=100)
    max_score: Optional[float] = Field(None, description="Maximum overall score", ge=0, le=100)
    recruiter_id: Optional[str] = Field(None, description="Filter by specific recruiter")
    date_from: Optional[datetime] = Field(None, description="Filter matches from this date")
    date_to: Optional[datetime] = Field(None, description="Filter matches until this date")
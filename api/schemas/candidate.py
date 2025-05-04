from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

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
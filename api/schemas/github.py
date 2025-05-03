from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Basic model components
class GitHubBasicInfo(BaseModel):
    """Basic user information from GitHub profile"""
    username: str
    name: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int = 0

class RepoItem(BaseModel):
    """Repository item details"""
    name: str
    description: Optional[str] = None
    url: str
    language: Optional[str] = None
    stars: int = 0
    forks: Optional[int] = None
    updated_at: Optional[str] = None

class RepoTopic(BaseModel):
    """Repository topic with count"""
    topic: str
    count: int

class Contribution(BaseModel):
    """Open source contribution details"""
    title: str
    url: str
    repo: str
    state: str

class OpenSourceContributions(BaseModel):
    """Container for all open source contributions"""
    pull_requests: List[Contribution] = []
    issues: List[Contribution] = []

class ContributionActivity(BaseModel):
    """Recent activity metrics"""
    last_90_days: int
    last_30_days: int

class TechPreference(BaseModel):
    """Technology preference with count"""
    language: Optional[str] = None
    topic: Optional[str] = None
    count: int

class TechPreferences(BaseModel):
    """Container for technology preferences"""
    from_readme: List[str] = []
    from_starred: List[TechPreference] = []

class Metadata(BaseModel):
    """Metadata about the GitHub profile insights"""
    generated_at: str
    with_token: bool

# Main request/response models
class GitHubProfileResponse(BaseModel):
    """Complete GitHub profile response structure"""
    basic_info: GitHubBasicInfo
    top_languages: Dict[str, int] = Field(default_factory=dict)
    personal_projects: List[RepoItem] = []
    forked_repos: List[RepoItem] = []
    most_active_repos: List[RepoItem] = []
    repo_topics: List[RepoTopic] = []
    open_source_contributions: OpenSourceContributions
    contribution_activity: ContributionActivity
    tech_preferences: TechPreferences
    metadata: Metadata

class GitHubProfileRequest(BaseModel):
    """Request model for fetching GitHub profile"""
    username: str
    force_refresh: bool = False

# Database models
class GitHubProfileDocument(BaseModel):
    """Firestore document structure for GitHub profiles"""
    user_id: str
    github_username: str
    timestamp: datetime = Field(default_factory=datetime.now)
    insights_data: GitHubProfileResponse
    markdown_content: Optional[str] = None
    processed: bool = True
    
    class Config:
        arbitrary_types_allowed = True

# Error response model
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
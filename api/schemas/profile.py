# api/schemas/profile.py

from pydantic import BaseModel
from typing import Dict, Any, Optional

# Model for LeetCode API responses
class LeetCodeProfileResponse(BaseModel):
    """Full LeetCode profile data structure as returned by the API"""
    userPublicProfile: Optional[Dict[str, Any]] = None
    languageStats: Optional[Dict[str, Any]] = None
    skillStats: Optional[Dict[str, Any]] = None
    userProblemsSolved: Optional[Dict[str, Any]] = None
    userProfileCalendar: Optional[Dict[str, Any]] = None
    getStreakCounter: Optional[Dict[str, Any]] = None
    currentTimestamp: Optional[Dict[str, Any]] = None
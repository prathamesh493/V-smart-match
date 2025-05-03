from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from api.schemas.github import GitHubProfileResponse, ErrorResponse
from services.profile_aggregator import get_github_data

router = APIRouter()

class UserDependency(BaseModel):
    user_id: str

# For demo purposes, this is a simple dependency function 
# In a real application, this would validate authentication tokens
async def get_current_user():
    # In a real app, this would extract the user ID from the token
    # For testing, you can update this to return a hardcoded user ID
    return UserDependency(user_id="test-user-123")

@router.get(
    "/github/{username}",
    response_model=Dict[str, Any],
    responses={404: {"model": ErrorResponse}},
    summary="Get GitHub profile data",
    description="Retrieves GitHub profile data for a given username. Checks Firestore cache first, falls back to live API if not cached."
)
async def get_github_profile(
    username: str,
    force_refresh: bool = Query(False, description="Force refresh data from GitHub API instead of using cached data"),
    current_user: UserDependency = Depends(get_current_user)
):
    """
    Retrieves GitHub profile data for a given username.
    
    - **username**: GitHub username to fetch data for
    - **force_refresh**: Set to true to force a refresh from the GitHub API instead of using cached data
    
    Returns the GitHub profile insights data.
    """
    try:
        # Get GitHub data with caching through the profile aggregator
        data = await get_github_data(
            username=username,
            user_id=current_user.user_id,
            force_refresh=force_refresh
        )
        return data
    except Exception as e:
        # Handle exceptions, like user not found
        raise HTTPException(status_code=404, detail=str(e))

@router.get(
    "/github-profiles",
    response_model=List[Dict[str, Any]],
    summary="Get all GitHub profiles for the current user",
    description="Lists all GitHub profiles that have been stored for the current authenticated user."
)
async def get_user_github_profiles(
    current_user: UserDependency = Depends(get_current_user)
):
    """
    Lists all GitHub profiles stored for the current user.
    
    Returns a list of GitHub profile documents from Firestore.
    """
    try:
        # This function is expected to be implemented in services/firebase.py
        from services.firebase import query_documents
        
        profiles = await query_documents(
            collection_name="github_profiles",
            field="user_id", 
            operator="==", 
            value=current_user.user_id,
            order_by="timestamp",
            direction="DESCENDING"
        )
        
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve GitHub profiles: {str(e)}")
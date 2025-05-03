# api/routes/profile.py

from fastapi import APIRouter, HTTPException, Query, Depends, Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from services.profile_aggregator import get_leetcode_data, get_github_data
from api.schemas.profile import LeetCodeProfileResponse
from api.schemas.github import GitHubProfileResponse, ErrorResponse

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
    "/leetcode/{username}", 
    response_model=Dict[str, Any], 
    responses={404: {"model": ErrorResponse}},
    summary="Get LeetCode profile data",
    description="Retrieves raw LeetCode profile data for a given username. Checks Firestore cache first, falls back to live API if not cached."
)
async def get_leetcode_profile(
    username: str, 
    force_refresh: bool = Query(False, description="Force refresh data from LeetCode API instead of using cached data")
):
    """
    Retrieves LeetCode profile data for a given username.
    
    - **username**: LeetCode username to fetch data for
    - **force_refresh**: Set to true to force a refresh from the LeetCode API instead of using cached data
    
    Returns the raw LeetCode profile data as returned by their GraphQL API.
    """
    try:
        # Get LeetCode data with caching
        data = await get_leetcode_data(username, force_refresh)
        return data
    except Exception as e:
        # Handle exceptions, like user not found
        raise HTTPException(status_code=404, detail=str(e))

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
    "/profiles/{user_id}",
    response_model=Dict[str, Any],
    summary="Get all developer profiles for a user",
    description="Retrieves all developer profiles (GitHub, LeetCode) associated with a specific user."
)
async def get_user_profiles(
    user_id: str = Path(..., description="User ID to fetch profiles for"),
    current_user: UserDependency = Depends(get_current_user)
):
    """
    Retrieves all developer profiles for a specific user.
    
    - **user_id**: User ID to fetch profiles for
    
    Returns a dictionary with GitHub and LeetCode profiles if they exist.
    """
    # For security, only allow users to access their own profiles
    if current_user.user_id != user_id and current_user.user_id != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access these profiles")
    
    try:
        from services.firebase import get_document
        
        # Get the user document which contains profile references
        user_doc = await get_document("users", user_id)
        if not user_doc:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        result = {"github": None, "leetcode": None}
        
        # Get GitHub profile if it exists
        if user_doc.get("github_profile_id"):
            github_profile = await get_document("github_profiles", user_doc["github_profile_id"])
            if github_profile:
                result["github"] = github_profile.get("insights_data")
        
        # Get LeetCode profile if it exists
        if user_doc.get("leetcode_username"):
            leetcode_username = user_doc["leetcode_username"]
            leetcode_profile = await get_document("leetcode_profiles", leetcode_username)
            if leetcode_profile:
                result["leetcode"] = leetcode_profile.get("profile_data")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profiles: {str(e)}")
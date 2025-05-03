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
    description="Retrieves all developer profiles (GitHub, LeetCode, Resume) associated with a specific user."
)
async def get_user_profiles(
    user_id: str = Path(..., description="User ID to fetch profiles for"),
    current_user: UserDependency = Depends(get_current_user)
):
    """
    Retrieves all developer profiles for a specific user.
    
    - **user_id**: User ID to fetch profiles for
    
    Returns a dictionary with GitHub, LeetCode, and Resume data if they exist.
    """
    # For security, only allow users to access their own profiles
    # Allow access to "string" user ID for testing purposes
    if current_user.user_id != user_id and current_user.user_id != "admin" and user_id != "string":
        raise HTTPException(status_code=403, detail="Not authorized to access these profiles")
    
    try:
        from services.firebase import get_document, query_documents
        
        # Initialize the result dictionary with all profile types
        result = {"github": None, "leetcode": None, "resume": None}
        
        # First check the candidates collection (new structure)
        candidate_doc = await get_document("candidates", user_id)
        
        # If not found in candidates, check the users collection (old structure)
        if not candidate_doc:
            user_doc = await get_document("users", user_id)
            if not user_doc:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            profile_doc = user_doc
        else:
            profile_doc = candidate_doc
        
        # Get GitHub profile if it exists
        if profile_doc.get("github_profile_id"):
            github_profile = await get_document("github_profiles", profile_doc["github_profile_id"])
            if github_profile:
                result["github"] = github_profile.get("insights_data")
        
        # Get LeetCode profile if it exists
        if profile_doc.get("leetcode_username"):
            leetcode_username = profile_doc["leetcode_username"]
            leetcode_profile = await get_document("leetcode_profiles", leetcode_username)
            if leetcode_profile:
                result["leetcode"] = leetcode_profile.get("profile_data")
        
        # Get Resume data if it exists
        resume_id = profile_doc.get("latest_resume_id")
        if resume_id:
            resume_data = await get_document("resumes", resume_id)
            if resume_data:
                result["resume"] = {
                    "id": resume_id,
                    "extracted_content": resume_data.get("extracted_content"),
                    "timestamp": resume_data.get("timestamp"),
                    "metadata": resume_data.get("metadata", {})
                }
        else:
            # If no specific resume ID is linked, try to find the most recent resume for this user
            resumes = await query_documents(
                collection_name="resumes",
                field="user_id", 
                operator="==", 
                value=user_id,
                order_by="timestamp",
                direction="DESCENDING",
                limit=1
            )
            
            if resumes and len(resumes) > 0:
                resume_data = resumes[0]
                result["resume"] = {
                    "id": resume_data.get("id"),
                    "extracted_content": resume_data.get("extracted_content"),
                    "timestamp": resume_data.get("timestamp"),
                    "metadata": resume_data.get("metadata", {})
                }
        
        # Additionally, look for a unified profile if it exists
        unified_profile = await get_document("unified_profiles", user_id)
        if unified_profile:
            result["unified"] = unified_profile
                
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profiles: {str(e)}")
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, Optional, List

from api.schemas.candidate import (
    ProfileLinkRequest, 
    UnifiedCandidateProfile, 
    ProfileLinkResponse, 
    CandidateSearchParams
)
from services.firebase import (
    link_candidate_profiles, 
    get_unified_candidate_profile,
    get_document
)

router = APIRouter(prefix="/candidate", tags=["candidate"])

@router.post("/link-profiles", status_code=status.HTTP_200_OK, response_model=ProfileLinkResponse)
async def link_profiles(profile_link: ProfileLinkRequest):
    """
    Link multiple profile types for a candidate (resume, GitHub, LeetCode).
    
    This endpoint establishes relationships between different profile data sources
    for a single candidate, creating a unified profile that can be retrieved later.
    
    - Links resume document with GitHub and LeetCode profiles
    - Creates a unified profile document for easier retrieval 
    - Updates the user document with references to all linked profiles
    
    The endpoint accepts at least one profile ID to link (resume_id, github_profile_id,
    or leetcode_username). IDs provided must reference existing documents in the system.
    """
    # Verify that at least one profile reference is provided
    if not (profile_link.resume_id or profile_link.github_profile_id or 
            profile_link.github_username or profile_link.leetcode_username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one profile reference must be provided"
        )
    
    # Verify that the resume exists if provided
    if profile_link.resume_id:
        resume_doc = await get_document("resumes", profile_link.resume_id)
        if not resume_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {profile_link.resume_id} not found"
            )
    
    # Verify that the GitHub profile exists if ID is provided
    if profile_link.github_profile_id:
        github_doc = await get_document("github_profiles", profile_link.github_profile_id)
        if not github_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GitHub profile with ID {profile_link.github_profile_id} not found"
            )
    
    # Create a dictionary of profile links to update
    profile_links = {
        "resume_id": profile_link.resume_id,
        "github_profile_id": profile_link.github_profile_id,
        "github_username": profile_link.github_username,
        "leetcode_username": profile_link.leetcode_username
    }
    
    # Filter out None values
    profile_links = {k: v for k, v in profile_links.items() if v is not None}
    
    # Link the profiles
    success = await link_candidate_profiles(profile_link.user_id, profile_links)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link profiles"
        )
    
    return ProfileLinkResponse(
        message="Profiles linked successfully",
        user_id=profile_link.user_id,
        linked_profiles=profile_links
    )

@router.get("/profile/{user_id}", response_model=UnifiedCandidateProfile)
async def get_candidate_profile(user_id: str):
    """
    Get the unified candidate profile with combined data from resume, GitHub, and LeetCode.
    
    This endpoint retrieves a unified view of a candidate by combining data from different
    profile sources that have been linked together. It provides a comprehensive view of:
    
    - Resume data and key skills
    - GitHub activity and top programming languages
    - LeetCode problem solving stats
    
    If the unified profile doesn't exist but individual profiles are linked to the user,
    this endpoint will create the unified profile on-demand.
    """
    profile = await get_unified_candidate_profile(user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No profile found for user ID {user_id}"
        )
    
    return profile

@router.get("/search", response_model=List[UnifiedCandidateProfile])
async def search_candidates(
    github_language: Optional[str] = None,
    leetcode_problems_min: Optional[int] = None,
    has_resume: Optional[bool] = None,
    limit: int = 10
):
    """
    Search for candidates based on criteria from GitHub and LeetCode profiles.
    
    This endpoint allows searching for candidates based on:
    
    - GitHub primary language
    - Minimum number of LeetCode problems solved
    - Whether the candidate has a resume
    - (Additional filters can be added as needed)
    
    Returns a list of unified candidate profiles matching the search criteria.
    """
    # This is a placeholder implementation that will need to be expanded
    # based on your specific search requirements and filtering logic
    
    # For now, we'll just return an empty list to be implemented later
    return []
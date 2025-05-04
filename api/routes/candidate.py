from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, Optional, List

from api.schemas.candidate import (
    ProfileLinkRequest, 
    UnifiedCandidateProfile, 
    ProfileLinkResponse, 
    CandidateSearchParams,
    CandidateReport
)
from services.firebase import (
    link_candidate_profiles, 
    get_unified_candidate_profile,
    get_document
)
from api.auth import get_current_user, UserData

router = APIRouter(prefix="/candidate", tags=["candidate"])

@router.post("/link-profiles", status_code=status.HTTP_200_OK, response_model=ProfileLinkResponse)
async def link_profiles(
    profile_link: ProfileLinkRequest,
    current_user: UserData = Depends(get_current_user)
):
    """
    Link multiple profile types for a candidate (resume, GitHub, LeetCode).
    
    This endpoint establishes relationships between different profile data sources
    for a single candidate, creating a unified profile that can be retrieved later.
    
    - Links resume document with GitHub and LeetCode profiles
    - Updates the user document with references to all linked profiles
    
    The endpoint accepts at least one profile ID to link (resume_id, github_profile_id,
    or leetcode_username). IDs provided must reference existing documents in the system.
    """
    # Use the authenticated user's ID or the one provided in the request (if any)
    user_id = current_user.user_id
    # If user_id is provided in the request and it's not the same as the authenticated user,
    # check if the current user has permission to modify another user's profile (admin check)
    if profile_link.user_id and profile_link.user_id != user_id:
        # For now, only allow admins to modify other users' profiles
        if current_user.user_id != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this profile"
            )
        user_id = profile_link.user_id
        
    # Use the appropriate candidate ID
    candidate_id = current_user.candidate_id if current_user.candidate_id else user_id
    
    # Log the authentication and candidate info for debugging
    print(f"Auth: Using user_id={user_id}, candidate_id={candidate_id}")
    
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
    
    # Use the candidate_id from the authenticated user for linking profiles
    success = await link_candidate_profiles(candidate_id, profile_links)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link profiles"
        )
    
    # If GitHub username is provided, trigger GitHub API fetch
    if profile_link.github_username:
        try:
            from services.profile_aggregator import get_github_data
            print(f"Fetching GitHub data for username={profile_link.github_username}, user_id={candidate_id}")
            
            # Fetch GitHub data - use the candidate_id for storing
            await get_github_data(
                username=profile_link.github_username,
                user_id=candidate_id,
                force_refresh=True
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Warning: Failed to fetch GitHub data: {str(e)}")
    
    # If LeetCode username is provided, trigger LeetCode API fetch
    if profile_link.leetcode_username:
        try:
            from services.profile_aggregator import get_leetcode_data
            print(f"Fetching LeetCode data for username={profile_link.leetcode_username}, user_id={candidate_id}")
            
            # Fetch LeetCode data - use the candidate_id for storing
            await get_leetcode_data(
                username=profile_link.leetcode_username,
                force_refresh=True,
                user_id=candidate_id
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Warning: Failed to fetch LeetCode data: {str(e)}")
    
    return ProfileLinkResponse(
        message="Profiles linked successfully",
        user_id=user_id,
        linked_profiles=profile_links
    )

@router.get("/profile/{user_id}", response_model=UnifiedCandidateProfile)
async def get_candidate_profile(
    user_id: str,
    current_user: UserData = Depends(get_current_user)
):
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
    # For security, users can only access their own profile unless they're an admin
    if current_user.user_id != user_id and current_user.user_id != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    
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
    limit: int = 10,
    current_user: UserData = Depends(get_current_user)
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

@router.get("/report/{candidate_id}", response_model=CandidateReport)
async def get_candidate_report(
    candidate_id: str,
    current_user: UserData = Depends(get_current_user)
):
    """
    Generate a comprehensive report for a candidate including all profile data.
    
    This endpoint aggregates information from:
    - Candidate's basic profile (personal info, skills, education, experience)
    - Resume data
    - GitHub profile statistics
    - LeetCode profile statistics
    
    Returns a unified report with candidate's complete profile information.
    """
    # Check if current user is requesting their own report or has permission
    if current_user.user_id != candidate_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this candidate's report"
        )
    
    # Get candidate document
    candidate_doc = await get_document("candidates", candidate_id)
    if not candidate_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found"
        )
    
    # Start building the candidate report
    report = CandidateReport(
        user_id=candidate_id,
        full_name=candidate_doc.get("fullName"),
        email=candidate_doc.get("email"),
        skills=candidate_doc.get("skills", []),
        education=candidate_doc.get("education", []),
        experience=candidate_doc.get("experience", []),
        has_resume=candidate_doc.get("has_resume", False),
        has_github_profile=candidate_doc.get("has_github_profile", False),
        has_leetcode_profile=candidate_doc.get("has_leetcode_profile", False),
        github_username=candidate_doc.get("github_username"),
        leetcode_username=candidate_doc.get("leetcode_username"),
        resume_id=candidate_doc.get("latest_resume_id"),
        resume_timestamp=candidate_doc.get("latest_resume_timestamp"),
        github_profile_id=candidate_doc.get("github_profile_id"),
        github_profile_timestamp=candidate_doc.get("github_profile_timestamp"),
        leetcode_profile_timestamp=candidate_doc.get("leetcode_profile_timestamp"),
    )
    
    # Get resume data if available
    if report.has_resume and report.resume_id:
        resume_doc = await get_document("resumes", report.resume_id)
        if resume_doc:
            report.resume_content = resume_doc.get("extracted_content")
    
    # Get GitHub profile data if available
    if report.has_github_profile and report.github_profile_id:
        github_doc = await get_document("github_profiles", report.github_profile_id)
        if github_doc:
            report.github_top_languages = github_doc.get("top_languages", [])
            report.github_activity = github_doc.get("activity", {})
    
    # Get LeetCode profile data if available
    if report.has_leetcode_profile and report.leetcode_username:
        # Query LeetCode profiles by username
        from services.firestore import db
        import asyncio
        
        leetcode_ref = db.collection("leetcode_profiles").where(
            "username", "==", report.leetcode_username
        ).limit(1)
        
        leetcode_docs = await asyncio.to_thread(lambda: leetcode_ref.get())
        if leetcode_docs and len(leetcode_docs) > 0:
            leetcode_doc = leetcode_docs[0].to_dict()
            report.leetcode_problems_solved = leetcode_doc.get("problems_solved", {})
    
    return report
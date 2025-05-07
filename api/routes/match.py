from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel

# Import Firebase utilities
from services.firebase import get_document, update_document, add_document, query_documents
from services.matcher import get_match, get_matches_for_resume, get_matches_for_job

router = APIRouter(prefix="/match", tags=["match"])

# Request and response models
class MatchRequest(BaseModel):
    candidate_id: str
    job_description_id: str

class MatchBulkRequest(BaseModel):
    candidate_ids: List[str] = []
    job_description_ids: List[str] = []

class MatchResult(BaseModel):
    match_id: str
    candidate_id: str
    job_description_id: str
    overall_score: float
    category_scores: Dict[str, Any]
    analysis: Dict[str, Any]
    metadata: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "match_id": "match_abc123",
                "candidate_id": "candidate_123",
                "job_description_id": "jd_456",
                "overall_score": 82.5,
                "category_scores": {
                    "skillsMatch": {
                        "score": 85,
                        "confidence": 90,
                        "keyMatches": [
                            {"skill": "Python", "relevance": 95},
                            {"skill": "React", "relevance": 80}
                        ],
                        "missingCriticalSkills": [
                            {"skill": "AWS", "importance": 75}
                        ]
                    },
                    # Other categories would be included here
                }
            }
        }

@router.post("/", response_model=Dict[str, Any])
async def create_match(match_req: MatchRequest):
    """
    Create a new match analysis between a candidate resume and job description.
    
    This endpoint:
    1. Retrieves the resume and job description documents
    2. Extracts their content
    3. Runs the matching algorithm
    4. Stores and returns the match results
    """
    try:
        # Retrieve the resume document
        resume_doc = await get_document("resumes", match_req.candidate_id)
        if not resume_doc:
            raise HTTPException(status_code=404, detail=f"Resume with ID {match_req.candidate_id} not found")
        
        # Retrieve the job description document
        job_doc = await get_document("job_descriptions", match_req.job_description_id)
        if not job_doc:
            raise HTTPException(status_code=404, detail=f"Job description with ID {match_req.job_description_id} not found")
        
        # Extract content from documents
        resume_content = resume_doc.get("extracted_content", "")
        job_content = job_doc.get("extracted_content", "")
        
        if not resume_content or not job_content:
            raise HTTPException(status_code=400, detail="Missing content in resume or job description")
        
        # Get GitHub data if available
        github_data = None
        github_profile = await get_document("github_profiles", match_req.candidate_id)
        if github_profile:
            github_data = github_profile
        
        # Get LeetCode data if available
        leetcode_data = None
        leetcode_profile = await get_document("leetcode_profiles", match_req.candidate_id)
        if leetcode_profile:
            leetcode_data = leetcode_profile
        
        # Generate match analysis
        match_result = await get_match(
            match_req.candidate_id,
            match_req.job_description_id,
            resume_content,
            job_content,
            github_data,
            leetcode_data
        )
        
        # Store the match result in Firebase
        await add_document("matches", match_result["matchId"], match_result)
        
        # Return the raw dictionary to avoid validation issues
        return match_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing match: {str(e)}")

@router.get("/{match_id}", response_model=Dict[str, Any])
async def get_match_by_id(match_id: str):
    """
    Retrieve a previously generated match by its ID.
    """
    match_doc = await get_document("matches", match_id)
    if not match_doc:
        raise HTTPException(status_code=404, detail=f"Match with ID {match_id} not found")
    
    return match_doc

@router.get("/candidate/{candidate_id}", response_model=List[Dict[str, Any]])
async def get_matches_by_candidate(
    candidate_id: str,
    limit: int = Query(10, description="Maximum number of matches to return")
):
    """
    Get all matches for a specific candidate.
    """
    matches = await query_documents("matches", "candidateId", "==", candidate_id, limit=limit)
    return matches

@router.get("/job/{job_description_id}", response_model=List[Dict[str, Any]])
async def get_matches_by_job(
    job_description_id: str,
    limit: int = Query(10, description="Maximum number of matches to return"),
    min_score: Optional[float] = Query(None, description="Minimum overall score filter")
):
    """
    Get all matches for a specific job description with optional score filtering.
    """
    matches = await query_documents("matches", "jobDescriptionId", "==", job_description_id, limit=limit)
    
    # Apply score filter if specified
    if min_score is not None:
        matches = [match for match in matches if match.get("overallScore", 0) >= min_score]
        
    return matches

@router.post("/bulk", response_model=List[Dict[str, Any]])
async def create_bulk_matches(bulk_req: MatchBulkRequest, background_tasks: BackgroundTasks):
    """
    Create multiple matches between candidates and job descriptions.
    
    This is useful for:
    - Matching one candidate against multiple job descriptions
    - Matching one job description against multiple candidates
    - Creating a matching matrix between multiple candidates and job descriptions
    """
    # Start the bulk matching process in the background
    background_tasks.add_task(process_bulk_matches, bulk_req.candidate_ids, bulk_req.job_description_ids)
    
    return {"message": f"Bulk matching started for {len(bulk_req.candidate_ids)} candidates and {len(bulk_req.job_description_ids)} job descriptions"}

async def process_bulk_matches(candidate_ids: List[str], job_description_ids: List[str]):
    """
    Background task to process bulk matches.
    """
    try:
        # Retrieve all candidates
        candidates = []
        for candidate_id in candidate_ids:
            resume_doc = await get_document("resumes", candidate_id)
            if resume_doc and "extracted_content" in resume_doc:
                # Get GitHub data if available
                github_data = None
                github_profile = await get_document("github_profiles", candidate_id)
                if github_profile:
                    github_data = github_profile
                
                # Get LeetCode data if available
                leetcode_data = None
                leetcode_profile = await get_document("leetcode_profiles", candidate_id)
                if leetcode_profile:
                    leetcode_data = leetcode_profile
                
                candidates.append({
                    "id": candidate_id,
                    "content": resume_doc["extracted_content"],
                    "github_data": github_data,
                    "leetcode_data": leetcode_data
                })
        
        # Retrieve all job descriptions
        job_descriptions = []
        for jd_id in job_description_ids:
            job_doc = await get_document("job_descriptions", jd_id)
            if job_doc and "extracted_content" in job_doc:
                job_descriptions.append({
                    "id": jd_id,
                    "content": job_doc["extracted_content"]
                })
        
        # Create a matrix of matches
        for candidate in candidates:
            for job in job_descriptions:
                try:
                    # Generate match analysis
                    match_result = await get_match(
                        candidate["id"],
                        job["id"],
                        candidate["content"],
                        job["content"],
                        candidate.get("github_data"),
                        candidate.get("leetcode_data")
                    )
                    
                    # Store match in database
                    await add_document("matches", match_result["matchId"], match_result)
                    print(f"Created match {match_result['matchId']} between candidate {candidate['id']} and job {job['id']}")
                except Exception as e:
                    print(f"Error creating match between candidate {candidate['id']} and job {job['id']}: {str(e)}")
                    continue
        
    except Exception as e:
        print(f"Error processing bulk matches: {str(e)}")

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_matches(
    min_score: float = Query(70, description="Minimum overall score"),
    skill: Optional[str] = Query(None, description="Required skill to filter by"),
    limit: int = Query(20, description="Maximum number of matches to return")
):
    """
    Search for matches with filtering options.
    """
    # Note: This is a simplified implementation. In a real-world scenario,
    # you would likely need more sophisticated querying capabilities.
    
    # Get all matches (in a production app, you'd use proper pagination and filtering)
    matches = await query_documents("matches", limit=limit)
    
    # Filter by minimum score
    filtered_matches = [match for match in matches if match.get("overallScore", 0) >= min_score]
    
    # Filter by skill if specified
    if skill:
        skill_filtered = []
        for match in filtered_matches:
            # Check if the skill exists in keyMatches
            key_matches = match.get("categoryScores", {}).get("skillsMatch", {}).get("keyMatches", [])
            skill_names = [item["skill"].lower() for item in key_matches]
            
            if skill.lower() in skill_names:
                skill_filtered.append(match)
        
        filtered_matches = skill_filtered
    
    return filtered_matches

@router.delete("/{match_id}")
async def delete_match(match_id: str):
    """
    Delete a match by ID.
    """
    # Check if match exists
    match_doc = await get_document("matches", match_id)
    if not match_doc:
        raise HTTPException(status_code=404, detail=f"Match with ID {match_id} not found")
    
    # Delete from Firebase
    # Implement your delete function in Firebase service
    # await delete_document("matches", match_id)
    
    return {"message": f"Match {match_id} deleted successfully"}
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import tempfile
from typing import Optional, List, Dict, Any
from ..schemas.job_description import JobDescriptionResponse, JobDescriptionUploadRequest
from ..schemas.resume import ErrorResponse
from services.job_description import extract_job_description_data
from services.job_firestore import store_job_description_data, get_job_description_data, get_user_job_descriptions, delete_job_description
from services.firebase import query_documents, get_document
from services.matcher import get_match

router = APIRouter(prefix="/job-description", tags=["job_description"])

async def generate_matches_for_job(job_id: str, job_content: str):
    """
    Background task to generate matches for all candidates against a new job description.
    
    Args:
        job_id: The ID of the job description
        job_content: The content of the job description
    """
    try:
        print(f"Starting background matching for job ID: {job_id}")
        
        # Get all candidates from the candidates collection instead of resumes
        candidates = await query_documents("candidates", limit=100)
        
        # Prepare candidate data for matching
        candidate_data = []
        for candidate in candidates:
            candidate_id = candidate.get("userId")  # Using userId from candidates collection
            
            if not candidate_id:
                continue
                
            # Check if candidate has a resume
            has_resume = candidate.get("has_resume", False)
            if not has_resume:
                print(f"Skipping candidate {candidate_id} with no resume")
                continue
                
            # Get resume content using latest_resume_id
            resume_id = candidate.get("latest_resume_id")
            if not resume_id:
                print(f"Skipping candidate {candidate_id} with no resume ID")
                continue
                
            # Fetch resume content from resumes collection
            resume_doc = await get_document("resumes", resume_id)
            if not resume_doc or "extracted_content" not in resume_doc:
                print(f"Could not find resume content for candidate {candidate_id}")
                continue
                
            resume_content = resume_doc.get("extracted_content", "")
            
            # Check GitHub profile status
            has_github_profile = candidate.get("has_github_profile", False)
            github_data = None
            if has_github_profile:
                github_username = candidate.get("github_username")
                if github_username:
                    github_profile = await get_document("github_profiles", candidate_id)
                    if github_profile:
                        github_data = github_profile
            
            # Check LeetCode profile status
            has_leetcode_profile = candidate.get("has_leetcode_profile", False)
            leetcode_data = None
            if has_leetcode_profile:
                leetcode_username = candidate.get("leetcode_username")
                if leetcode_username:
                    leetcode_profile = await get_document("leetcode_profiles", candidate_id)
                    if leetcode_profile:
                        leetcode_data = leetcode_profile
            
            candidate_data.append({
                "id": candidate_id,
                "content": resume_content,
                "github_data": github_data,
                "leetcode_data": leetcode_data,
                "full_name": candidate.get("fullName"),
                "email": candidate.get("email")
            })
        
        print(f"Found {len(candidate_data)} candidates for matching")
        
        # Generate matches for each candidate
        for candidate in candidate_data:
            try:
                match_result = await get_match(
                    candidate["id"],
                    job_id,
                    candidate["content"],
                    job_content,
                    candidate.get("github_data"),
                    candidate.get("leetcode_data")
                )
                
                # Add additional candidate info to match result
                match_result["candidate_name"] = candidate.get("full_name", "")
                match_result["candidate_email"] = candidate.get("email", "")
                
                # Store the match in Firestore
                from services.firebase import add_document
                await add_document("matches", match_result["matchId"], match_result)
                print(f"Created match {match_result['matchId']} between candidate {candidate['id']} and job {job_id}")
                
            except Exception as e:
                print(f"Error generating match for candidate {candidate['id']}: {str(e)}")
                continue
                
        print(f"Completed background matching for job ID: {job_id}")
        
    except Exception as e:
        print(f"Error in background matching task: {str(e)}")
@router.post(
    "/upload",
    response_model=JobDescriptionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def upload_job_description(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    job_title: Optional[str] = Form(None),
    company: Optional[str] = Form(None)
):
    """
    Upload and process a job description PDF file
    - Saves the uploaded PDF temporarily
    - Extracts text using zerox
    - Processes the text with Gemini AI
    - Stores structured data in Firestore under the provided user_id
    - Generates matches for all candidates in the system
    """
    # Validate file is PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"job_{user_id}_{timestamp}_{unique_id}.pdf"

    # Create data/job_descriptions directory if it doesn't exist
    os.makedirs("data/job_descriptions", exist_ok=True)
    file_path = os.path.join("data/job_descriptions", filename)

    try:
        # Save file
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Process file using zerox and extract markdown content
        parsed_data, markdown_content = await extract_job_description_data(
            file_path, 
            job_title=job_title, 
            company=company
        )
        
        # Validate markdown content
        if not isinstance(markdown_content, str):
            raise ValueError(f"Expected string markdown content but got {type(markdown_content)}")
            
        # Store data in Firestore
        doc_id = await store_job_description_data(user_id, filename, parsed_data)

        # Schedule file cleanup in background after processing
        background_tasks.add_task(cleanup_file, file_path)
        
        # Schedule background task to generate matches for all candidates
        background_tasks.add_task(generate_matches_for_job, doc_id, markdown_content)

        # Get metadata for response if available
        metadata = parsed_data.get("metadata", {})
        
        # Return response
        return JobDescriptionResponse(
            user_id=user_id,
            timestamp=datetime.now(),
            file_name=filename,
            extracted_content=markdown_content,
            format="markdown",
            doc_id=doc_id,
            metadata=metadata,
            job_title=parsed_data.get("job_title"),
            company=parsed_data.get("company")
        )
    except Exception as e:
        # Ensure file is cleaned up in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Job description processing failed: {str(e)}")

@router.get(
    "/{job_id}",
    response_model=JobDescriptionResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_job_description(job_id: str):
    """
    Get a job description by ID
    """
    try:
        job_data = await get_job_description_data(job_id)
        
        return JobDescriptionResponse(
            user_id=job_data.get("user_id"),
            timestamp=job_data.get("timestamp"),
            file_name=job_data.get("file_name"),
            extracted_content=job_data.get("extracted_content"),
            format=job_data.get("format", "markdown"),
            doc_id=job_id,
            metadata=job_data.get("metadata"),
            job_title=job_data.get("job_title"),
            company=job_data.get("company")
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get(
    "/user/{user_id}",
    response_model=List[JobDescriptionResponse],
    responses={500: {"model": ErrorResponse}}
)
async def get_user_jobs(user_id: str):
    """
    Get all job descriptions for a user
    """
    try:
        jobs = await get_user_job_descriptions(user_id)
        
        return [
            JobDescriptionResponse(
                user_id=job.get("user_id"),
                timestamp=job.get("timestamp"),
                file_name=job.get("file_name"),
                extracted_content=job.get("extracted_content"),
                format=job.get("format", "markdown"),
                doc_id=job.get("id"),
                metadata=job.get("metadata"),
                job_title=job.get("job_title"),
                company=job.get("company")
            )
            for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user job descriptions: {str(e)}")

@router.delete(
    "/{job_id}",
    responses={404: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def remove_job_description(job_id: str, user_id: str):
    """
    Delete a job description
    """
    try:
        success = await delete_job_description(user_id, job_id)
        return {"message": "Job description deleted successfully"}
    except Exception as e:
        if "Not authorized" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        elif "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete job description: {str(e)}")

def cleanup_file(file_path: str):
    """Remove temporary file after processing"""
    if os.path.exists(file_path):
        os.remove(file_path)
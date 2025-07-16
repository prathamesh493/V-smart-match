# routes/job_description.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import tempfile
from typing import Optional, List, Dict, Any

# --- MODIFIED IMPORTS ---
from ..schemas.job_description import JobDescriptionResponse # JobDescriptionUploadRequest is no longer needed here
from ..schemas.resume import ErrorResponse
from services.job_description import extract_job_description_data
from services.job_firestore import store_job_description_data, get_job_description_data, get_user_job_descriptions, delete_job_description
from services.firebase import get_document, add_document
from services.matcher import get_match
from services.embedding import get_embedding
from services.pinecone_service import query_embedding

router = APIRouter(prefix="/job-description", tags=["job_description"])


# This is our efficient background task function
async def find_and_generate_matches(job_id: str, job_content: str, num_matches_to_generate: int, recruiter_id: str, job_title: str):
    """
    Background task to find top candidates via vector search and generate detailed match reports.
    """
    try:
        print(f"Starting background matching for job ID: {job_id} for {num_matches_to_generate} candidates.")
        
        # 1. Generate an embedding for the job description
        job_embedding = get_embedding(job_content)

        print(f"Job embedding is: {job_embedding}")

        # 2. Query Pinecone: fetch the desired number of candidate resumes
        query_results = query_embedding(embedding=job_embedding, top_k=num_matches_to_generate)

        print(f"Query results from Pinecone: {query_results}")
        
        pinecone_matches = query_results.get('matches', [])
        if not pinecone_matches:
            print(f"No potential candidates found in Pinecone for job {job_id}")
            return

        # 3. Process each potential candidate and generate a full match report
        for pinecone_match in pinecone_matches:
            try:
                resume_id = pinecone_match['id']
                score = pinecone_match.get('score')
                # Fetch resume and associated candidate details
                resume_doc = await get_document("resumes", resume_id)
                if not resume_doc or "user_id" not in resume_doc:
                    print(f"Skipping resume {resume_id}, missing content or user_id.")
                    continue
                
                candidate_id = resume_doc["user_id"]
                candidate_doc = await get_document("candidates", candidate_id)
                if not candidate_doc:
                    print(f"Could not find candidate profile for ID {candidate_id}")
                    continue
                
                # Fetch optional profile data
                github_data = await get_document("github_profiles", candidate_id) if candidate_doc.get("has_github_profile") else None
                leetcode_data = await get_document("leetcode_profiles", candidate_id) if candidate_doc.get("has_leetcode_profile") else None

                # Generate the detailed match report
                match_result = await get_match(
                    candidate_id=candidate_id,
                    job_description_id=job_id,
                    resume_content=resume_doc["extracted_content"],
                    job_description_content=job_content,
                    github_data=github_data,
                    leetcode_data=leetcode_data
                )
                
                match_result["candidate_name"] = candidate_doc.get("fullName", "")
                match_result["candidate_email"] = candidate_doc.get("email", "")
                match_result["embedding_score"] = score
                match_result["recruiterId"] = recruiter_id
                match_result["jobTitle"] = job_title
                
                await add_document("matches", match_result["matchId"], match_result)
                print(f"Created match {match_result['matchId']} for candidate {candidate_id} (embedding_score={score})")

            except Exception as e:
                print(f"Error generating match for resume {resume_id}: {str(e)}")
                continue
                
        print(f"Completed background matching for job ID: {job_id}")

    except Exception as e:
        print(f"FATAL Error in background matching task for job {job_id}: {str(e)}")

@router.post(
    "/upload",
    response_model=JobDescriptionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def upload_job_description_and_match(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    num_matches: int = Form(..., description="The number of top candidate matches to generate."),
    job_title: Optional[str] = Form(None),
    company: Optional[str] = Form(None)
):
    """
    Upload a job description, process it, and trigger the matching process
    for the specified number of top candidates in a single action.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"job_{user_id}_{timestamp}_{unique_id}.pdf"

    os.makedirs("data/job_descriptions", exist_ok=True)
    file_path = os.path.join("data/job_descriptions", filename)

    try:
        # Step 1: Save and process the uploaded Job Description
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        parsed_data, markdown_content = await extract_job_description_data(
            file_path, job_title=job_title, company=company
        )
        print(f"Extracted job description content: {markdown_content[:30]}...")  # Log first 30 chars for debugging
        if not isinstance(markdown_content, str) or not markdown_content:
            raise ValueError("Extracted job description content is invalid.")
            
        # Step 2: Store the processed JD in Firestore to get a doc_id
        doc_id = await store_job_description_data(user_id, filename, parsed_data)

        # Step 3: Schedule background tasks for matching and cleanup
        background_tasks.add_task(
            find_and_generate_matches, 
            job_id=doc_id, 
            job_content=markdown_content,
            num_matches_to_generate=num_matches,
            recruiter_id=user_id,
            job_title=parsed_data.get("job_title", "Untitled Job")
        )
        background_tasks.add_task(cleanup_file, file_path)

        # Step 4: Return an immediate response to the user
        return JobDescriptionResponse(
            user_id=user_id,
            timestamp=datetime.now(),
            file_name=filename,
            extracted_content=markdown_content,
            format="markdown",
            doc_id=doc_id,
            metadata=parsed_data.get("metadata", {}),
            job_title=parsed_data.get("job_title"),
            company=parsed_data.get("company"),
            detail=f"Successfully uploaded. Matching process for top {num_matches} candidates has started in the background."
        )
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Job description processing failed: {str(e)}")

# The rest of the file (GET, DELETE endpoints) remains the same
# ... (get_job_description, get_user_jobs, remove_job_description, cleanup_file) ...

@router.get(
    "/{job_id}",
    response_model=JobDescriptionResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_job_description(job_id: str):
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
        
@router.get(
    "/{job_id}/embedding",
    response_model=Dict[str, Any],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_job_description_embedding(job_id: str):
    """
    Generate and return the embedding for the specified job description ID.
    """
    try:
        job_data = await get_job_description_data(job_id)
        jd_content = job_data.get("extracted_content")
        if not jd_content:
            raise HTTPException(status_code=404, detail="Job description content not found.")
        embedding = get_embedding(jd_content)
        return {"job_id": job_id, "embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")


def cleanup_file(file_path: str):
    """Remove temporary file after processing"""
    if os.path.exists(file_path):
        os.remove(file_path)
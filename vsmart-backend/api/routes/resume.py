# api/resume.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import tempfile
from typing import Optional
from services.pinecone_service import upsert_embedding, delete_by_metadata_filter
from services.embedding import get_embedding
from ..schemas.resume import ResumeResponse, ErrorResponse
from services.gemini import extract_resume_data
from services.firestore import store_resume_data
import logging
from api.auth import get_current_user, UserData


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/resume", tags=["resume"])


@router.post(
    "/upload",
    response_model=ResumeResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: UserData = Depends(get_current_user),
):
    """
    Upload and process a resume PDF file:
    - Saves the uploaded PDF temporarily.
    - Extracts structured JSON data using Gemini.
    - Creates rich metadata for the vector database.
    - Converts the JSON to markdown for storage in Firestore.
    - Upserts an embedding with the rich metadata to Pinecone.
    """
    user_id = current_user.user_id
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{user_id}_{timestamp}_{unique_id}.pdf"

    os.makedirs("data/resumes", exist_ok=True)
    file_path = os.path.join("data/resumes", filename)

    try:
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        logger.info(f"File saved to {file_path}")

        try:
            logger.info("Starting resume extraction...")
            pinecone_metadata, markdown_content, firestore_data = await extract_resume_data(file_path)
            
            # --- MODIFICATION: Add user_id to the Firestore document data ---
            firestore_data['user_id'] = user_id
            # --- END MODIFICATION ---

            logger.info("Resume extraction and processing completed successfully.")

            if not isinstance(markdown_content, str) or not markdown_content:
                raise ValueError("Generated markdown content is invalid or empty.")
            
            # Store the markdown and other data in Firestore
            doc_id = await store_resume_data(user_id, filename, firestore_data)
    
            background_tasks.add_task(cleanup_file, file_path)
    
            # Generate embedding from the clean markdown content
            embedding = get_embedding(markdown_content)

            # Check for and delete existing documents using the email from the resume
            resume_email = pinecone_metadata.get('email')
            if resume_email:
                logger.info(f"Checking for existing documents for email: {resume_email}")
                try:
                    deleted_result = delete_by_metadata_filter({"email": resume_email})
                    if deleted_result == "deleted":
                        logger.info(f"Deleted existing documents for email {resume_email} using filter")
                    elif isinstance(deleted_result, int) and deleted_result > 0:
                        logger.info(f"Deleted {deleted_result} existing documents for email {resume_email}")
                    else:
                        logger.info("No existing documents found for this email")
                except Exception as delete_error:
                    logger.warning(f"Error deleting existing documents: {str(delete_error)}")
                    # Continue with the upload even if deletion fails
            else:
                logger.warning("No email found in resume metadata for checking existing documents")

            # Upsert the embedding to Pinecone with the rich metadata
            logger.info(f"Upserting to Pinecone with metadata: {pinecone_metadata}")
            upsert_embedding(doc_id, embedding, pinecone_metadata)
            
            return ResumeResponse(
                user_id=user_id,
                timestamp=datetime.now(),
                file_name=filename,
                extracted_content=markdown_content,
                format="markdown",
                doc_id=doc_id,
                metadata=firestore_data.get("metadata", {})
            )
        except Exception as processing_error:
            logger.error(f"Error processing PDF: {str(processing_error)}")
            if "poppler" in str(processing_error).lower():
                raise HTTPException(
                    status_code=500, 
                    detail="PDF processing failed: Poppler is not installed. Please install poppler-utils and add it to your PATH."
                )
            else:
                raise HTTPException(status_code=500, detail=f"Resume processing failed: {str(processing_error)}")
    except Exception as e:
        logger.error(f"Error in upload process: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Resume processing failed: {str(e)}")


# No changes needed for the GET endpoint or cleanup_file function
@router.get(
    "/{user_id}",
    response_model=ResumeResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_resume_by_user_id_endpoint(
    user_id: str,
):
    try:
        from services.firestore import get_resume_by_user_id
        resume_data = await get_resume_by_user_id(user_id)
        if not resume_data:
            raise HTTPException(status_code=404, detail=f"No resume found for user ID: {user_id}")
        return resume_data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving resume data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resume data: {str(e)}")


def cleanup_file(file_path: str):
    """Remove temporary file after processing"""
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"Cleaned up file: {file_path}")
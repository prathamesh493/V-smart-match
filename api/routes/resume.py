from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import tempfile
from typing import Optional
from ..schemas.resume import ResumeResponse, ErrorResponse
from services.gemini import extract_resume_data
from services.firestore import store_resume_data
import logging

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
    user_id: str = Form(...),
):
    """
    Upload and process a resume PDF file
    - Saves the uploaded PDF temporarily
    - Extracts text using zerox
    - Processes the text with Gemini AI
    - Stores structured data in Firestore under the provided user_id
    """
    # Validate file is PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{user_id}_{timestamp}_{unique_id}.pdf"

    # Create data/resumes directory if it doesn't exist
    os.makedirs("data/resumes", exist_ok=True)
    file_path = os.path.join("data/resumes", filename)

    try:
        # Save file
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
            
        logger.info(f"File saved to {file_path}")

        try:
            # Process file using zerox and extract markdown content
            logger.info("Starting resume extraction...")
            parsed_data, markdown_content = await extract_resume_data(file_path)
            logger.info("Resume extraction completed successfully")
            
            # Validate markdown content
            if not isinstance(markdown_content, str):
                raise ValueError(f"Expected string markdown content but got {type(markdown_content)}")
                
            # Store data in Firestore
            doc_id = await store_resume_data(user_id, filename, parsed_data)
    
            # Schedule file cleanup in background after processing
            background_tasks.add_task(cleanup_file, file_path)
    
            # Get metadata for response if available
            metadata = parsed_data.get("metadata", {})
            
            # Return response
            return ResumeResponse(
                user_id=user_id,
                timestamp=datetime.now(),
                file_name=filename,
                extracted_content=markdown_content,
                format="markdown",
                doc_id=doc_id,  # Add document ID to response
                metadata=metadata  # Add metadata to response if schema supports it
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
        # Ensure file is cleaned up in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Resume processing failed: {str(e)}")

def cleanup_file(file_path: str):
    """Remove temporary file after processing"""
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"Cleaned up file: {file_path}")
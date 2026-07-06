import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import os
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import FIREBASE_CREDENTIALS_PATH

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK if not already initialized
try:
    # Use existing app if initialized
    firebase_admin.get_app()
except ValueError:
    try:
        # Only initialize if we have real credentials
        if os.path.exists(FIREBASE_CREDENTIALS_PATH) and FIREBASE_CREDENTIALS_PATH != "firebase-credentials.json":
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        else:
            logger.warning("Firebase credentials not found or using dummy credentials. Firebase services disabled.")
            firebase_admin = None
    except Exception as e:
        logger.warning(f"Failed to initialize Firebase: {e}. Firebase services disabled.")
        firebase_admin = None

# Initialize Firestore client
if firebase_admin:
    try:
        db = firestore.client()
    except Exception as e:
        logger.warning(f"Failed to initialize Firestore client: {e}")
        db = None
else:
    db = None

async def store_job_description_data(
    user_id: str,
    filename: str,
    parsed_data: Dict[str, Any]
) -> str:
    """
    Store job description data in Firestore
    
    Args:
        user_id: User ID to associate with this job description
        filename: Original filename of the uploaded job description
        parsed_data: Dictionary containing extracted markdown content and metadata
        
    Returns:
        Document ID of the stored job description data
    """
    try:
        # Ensure the extracted_content is a string
        extracted_content = parsed_data.get("extracted_content", "")
        if not isinstance(extracted_content, str):
            raise ValueError("Extracted content must be a string")
            
        # Create document for storage
        doc_data = {
            "user_id": user_id,
            "file_name": filename,
            "timestamp": datetime.now(),
            "extracted_content": extracted_content,
            "format": parsed_data.get("format", "markdown"),
            "processed": True,
            "job_title": parsed_data.get("job_title"),
            "company": parsed_data.get("company")
        }
        
        # Add metadata if available, ensuring all values are serializable
        if "metadata" in parsed_data and isinstance(parsed_data["metadata"], dict):
            # Convert any non-serializable values to strings
            safe_metadata = {}
            for key, value in parsed_data["metadata"].items():
                if isinstance(value, (str, int, float, bool, datetime, type(None))):
                    safe_metadata[key] = value
                else:
                    safe_metadata[key] = str(value)
            
            doc_data["metadata"] = safe_metadata
        
        # Store in Firestore
        job_ref = db.collection("job_descriptions").document()
        await asyncio.to_thread(lambda: job_ref.set(doc_data))
        
        # Update user document with reference to this job description
        user_ref = db.collection("users").document(user_id)
        user_doc = await asyncio.to_thread(lambda: user_ref.get())
        
        user_data = {
            "latest_job_description_id": job_ref.id,
            "latest_job_description_timestamp": datetime.now(),
            "has_job_descriptions": True
        }
        
        # Create or update user document
        if not user_doc.exists:
            user_data["created_at"] = datetime.now()
            
        await asyncio.to_thread(lambda: user_ref.set(user_data, merge=True))
        
        # Also add to user's job descriptions collection
        user_jobs_ref = user_ref.collection("job_descriptions").document(job_ref.id)
        await asyncio.to_thread(lambda: user_jobs_ref.set({
            "job_id": job_ref.id,
            "timestamp": datetime.now(),
            "job_title": parsed_data.get("job_title"),
            "company": parsed_data.get("company")
        }))
        
        return job_ref.id
    except Exception as e:
        raise Exception(f"Failed to store job description data in Firestore: {str(e)}")

async def get_job_description_data(job_id: str) -> Dict[str, Any]:
    """
    Retrieve job description data from Firestore
    
    Args:
        job_id: Document ID of the job description
        
    Returns:
        Job description data as dictionary
    """
    try:
        job_ref = db.collection("job_descriptions").document(job_id)
        job_doc = await asyncio.to_thread(lambda: job_ref.get())
        
        if not job_doc.exists:
            raise Exception(f"Job description with ID {job_id} not found")
            
        return job_doc.to_dict()
    except Exception as e:
        raise Exception(f"Failed to retrieve job description data: {str(e)}")

async def get_user_job_descriptions(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all job descriptions for a user
    
    Args:
        user_id: User ID to get job descriptions for
        
    Returns:
        List of job description data dictionaries with document IDs
    """
    try:
        jobs_ref = db.collection("job_descriptions").where("user_id", "==", user_id).order_by("timestamp", direction=firestore.Query.DESCENDING)
        jobs = await asyncio.to_thread(lambda: jobs_ref.get())
        
        return [{"id": doc.id, **doc.to_dict()} for doc in jobs]
    except Exception as e:
        raise Exception(f"Failed to retrieve user job descriptions: {str(e)}")

async def delete_job_description(user_id: str, job_id: str) -> bool:
    """
    Delete a job description
    
    Args:
        user_id: User ID who owns the job description
        job_id: Document ID of the job description to delete
        
    Returns:
        True if successful, raises exception otherwise
    """
    try:
        # First verify ownership
        job_ref = db.collection("job_descriptions").document(job_id)
        job_doc = await asyncio.to_thread(lambda: job_ref.get())
        
        if not job_doc.exists:
            raise Exception(f"Job description with ID {job_id} not found")
            
        job_data = job_doc.to_dict()
        if job_data.get("user_id") != user_id:
            raise Exception("Not authorized to delete this job description")
        
        # Delete the job description
        await asyncio.to_thread(lambda: job_ref.delete())
        
        # Also remove from user's job descriptions subcollection
        user_ref = db.collection("users").document(user_id)
        user_job_ref = user_ref.collection("job_descriptions").document(job_id)
        await asyncio.to_thread(lambda: user_job_ref.delete())
        
        return True
    except Exception as e:
        raise Exception(f"Failed to delete job description: {str(e)}")
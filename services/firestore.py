import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import FIREBASE_CREDENTIALS_PATH

# Initialize Firebase Admin SDK
try:
    # Use existing app if initialized
    firebase_admin.get_app()
except ValueError:
    # Initialize app if not already done
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

async def store_resume_data(
    user_id: str,
    filename: str,
    parsed_data: Dict[str, Any]
) -> str:
    """
    Store resume data in Firestore
    
    Args:
        user_id: User ID to associate with this resume
        filename: Original filename of the uploaded resume
        parsed_data: Dictionary containing extracted markdown content and metadata
        
    Returns:
        Document ID of the stored resume data
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
            "processed": True
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
        
        # Store in Firestore (use user_id as doc_id or generate one)
        # First check if user exists
        user_ref = db.collection("users").document(user_id)
        user_doc = await asyncio.to_thread(lambda: user_ref.get())
        
        # Store resume data
        resume_ref = db.collection("resumes").document()
        await asyncio.to_thread(lambda: resume_ref.set(doc_data))
        
        # Update user document with reference to this resume
        user_data = {
            "latest_resume_id": resume_ref.id,
            "latest_resume_timestamp": datetime.now(),
            "has_resume": True
        }
        
        if not user_doc.exists:
            # Create user if doesn't exist
            user_data["created_at"] = datetime.now()
            
        await asyncio.to_thread(lambda: user_ref.set(user_data, merge=True))
        
        return resume_ref.id
    except Exception as e:
        raise Exception(f"Failed to store resume data in Firestore: {str(e)}")

async def get_resume_data(resume_id: str) -> Dict[str, Any]:
    """
    Retrieve resume data from Firestore
    
    Args:
        resume_id: Document ID of the resume
        
    Returns:
        Resume data as dictionary
    """
    try:
        resume_ref = db.collection("resumes").document(resume_id)
        resume_doc = await asyncio.to_thread(lambda: resume_ref.get())
        
        if not resume_doc.exists:
            raise Exception(f"Resume with ID {resume_id} not found")
            
        return resume_doc.to_dict()
    except Exception as e:
        raise Exception(f"Failed to retrieve resume data: {str(e)}")

async def get_user_resumes(user_id: str) -> list:
    """
    Get all resumes for a user
    
    Args:
        user_id: User ID to get resumes for
        
    Returns:
        List of resume data dictionaries
    """
    try:
        resumes_ref = db.collection("resumes").where("user_id", "==", user_id).order_by("timestamp", direction=firestore.Query.DESCENDING)
        resumes = await asyncio.to_thread(lambda: resumes_ref.get())
        
        return [doc.to_dict() for doc in resumes]
    except Exception as e:
        raise Exception(f"Failed to retrieve user resumes: {str(e)}")
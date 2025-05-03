import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from services.firebase import get_db, convert_to_serializable, document_to_dict

async def store_github_insights(
    user_id: str,
    username: str,
    insights_data: Dict[str, Any],
    markdown_content: Optional[str] = None
) -> str:
    """
    Store GitHub insights data and markdown in Firestore
    
    Args:
        user_id: User ID to associate with this GitHub profile
        username: GitHub username 
        insights_data: Dictionary containing GitHub profile insights
        markdown_content: Optional GitHub profile markdown content
        
    Returns:
        Document ID of the stored GitHub insights
    """
    try:
        db = get_db()
        
        # Create document for storage
        timestamp = datetime.now()
        doc_data = {
            "user_id": user_id,
            "github_username": username,
            "timestamp": timestamp,
            "insights_data": convert_to_serializable(insights_data),
            "processed": True
        }
        
        # Add markdown content if available
        if markdown_content:
            doc_data["markdown_content"] = markdown_content
        
        # Store in Firestore
        github_ref = db.collection("github_profiles").document()
        github_ref.set(doc_data)
        
        # Update user document with reference to this GitHub profile
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        user_data = {
            "github_profile_id": github_ref.id,
            "github_username": username,
            "github_profile_timestamp": timestamp,
            "has_github_profile": True
        }
        
        # Create or update user document
        if not user_doc.exists:
            user_data["created_at"] = timestamp
            
        user_ref.set(user_data, merge=True)
        
        # Also add to user's profiles collection
        user_profiles_ref = user_ref.collection("profiles").document(github_ref.id)
        user_profiles_ref.set({
            "profile_id": github_ref.id,
            "profile_type": "github",
            "username": username,
            "timestamp": timestamp
        })
        
        return github_ref.id
    except Exception as e:
        raise Exception(f"Failed to store GitHub insights data in Firestore: {str(e)}")

async def get_github_insights(github_profile_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve GitHub insights data from Firestore
    
    Args:
        github_profile_id: Document ID of the GitHub profile
        
    Returns:
        GitHub profile data as dictionary
    """
    try:
        db = get_db()
        profile_ref = db.collection("github_profiles").document(github_profile_id)
        profile_doc = profile_ref.get()
        
        if not profile_doc.exists:
            return None
            
        return document_to_dict(profile_doc)
    except Exception as e:
        raise Exception(f"Failed to retrieve GitHub profile data: {str(e)}")

async def get_github_insights_by_username(user_id: str, github_username: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve GitHub insights data by username for a specific user
    
    Args:
        user_id: User ID who owns the GitHub profile
        github_username: GitHub username to retrieve
        
    Returns:
        GitHub profile data as dictionary or None if not found
    """
    try:
        db = get_db()
        profiles_ref = db.collection("github_profiles").where("user_id", "==", user_id).where("github_username", "==", github_username)
        profiles = profiles_ref.get()
        
        if not profiles or len(profiles) == 0:
            return None
            
        # Return the most recent profile if multiple exist
        profiles_dict = [document_to_dict(doc) for doc in profiles]
        profiles_sorted = sorted(profiles_dict, key=lambda x: x.get("timestamp"), reverse=True)
        return profiles_sorted[0] if profiles_sorted else None
    except Exception as e:
        raise Exception(f"Failed to retrieve GitHub profile data: {str(e)}")

async def list_user_github_profiles(user_id: str) -> List[Dict[str, Any]]:
    """
    List all GitHub profiles for a specific user
    
    Args:
        user_id: User ID to get GitHub profiles for
        
    Returns:
        List of GitHub profile data dictionaries
    """
    try:
        db = get_db()
        profiles_ref = db.collection("github_profiles").where("user_id", "==", user_id).order_by("timestamp", direction="DESCENDING")
        profiles = profiles_ref.get()
        
        return [document_to_dict(doc) for doc in profiles]
    except Exception as e:
        raise Exception(f"Failed to list GitHub profiles: {str(e)}")

async def delete_github_profile(github_profile_id: str, user_id: str) -> bool:
    """
    Delete a GitHub profile and its references
    
    Args:
        github_profile_id: Document ID of the GitHub profile to delete
        user_id: User ID who owns the GitHub profile
        
    Returns:
        True if delete was successful, False otherwise
    """
    try:
        db = get_db()
        
        # Delete the main profile document
        profile_ref = db.collection("github_profiles").document(github_profile_id)
        profile_doc = profile_ref.get()
        
        if not profile_doc.exists:
            return False
            
        # Check ownership
        if profile_doc.to_dict().get("user_id") != user_id:
            return False
            
        # Delete from user's profiles subcollection
        user_ref = db.collection("users").document(user_id)
        user_profile_ref = user_ref.collection("profiles").document(github_profile_id)
        
        # Use a batch write for atomicity
        batch = db.batch()
        batch.delete(profile_ref)
        batch.delete(user_profile_ref)
        
        # If this is the current active profile, update the user document
        user_doc = user_ref.get()
        if user_doc.exists and user_doc.to_dict().get("github_profile_id") == github_profile_id:
            # Find the next most recent profile
            next_profiles = db.collection("github_profiles").where("user_id", "==", user_id).order_by("timestamp", direction="DESCENDING").limit(1).get()
            
            if next_profiles and len(next_profiles) > 0:
                next_profile = next_profiles[0]
                batch.update(user_ref, {
                    "github_profile_id": next_profile.id,
                    "github_username": next_profile.to_dict().get("github_username"),
                    "github_profile_timestamp": next_profile.to_dict().get("timestamp")
                })
            else:
                # No profiles left
                batch.update(user_ref, {
                    "github_profile_id": None,
                    "github_username": None,
                    "github_profile_timestamp": None,
                    "has_github_profile": False
                })
        
        # Commit the batch
        batch.commit()
        
        return True
    except Exception as e:
        raise Exception(f"Failed to delete GitHub profile: {str(e)}")
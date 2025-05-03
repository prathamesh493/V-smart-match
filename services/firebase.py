import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Initialize Firebase Admin SDK
# This should be done only once in your application
def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Use the service account credentials file
        cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'path/to/serviceAccountKey.json')
        
        try:
            # Try to use the credentials file
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            # If that fails, try to use the default application credentials
            # This is useful for Google Cloud environment
            firebase_admin.initialize_app()
            
    return firestore.client()

# Get a reference to the Firestore database
def get_db():
    """Get a reference to the Firestore database."""
    try:
        return firestore.client()
    except ValueError:
        # If the app is not initialized, initialize it first
        initialize_firebase()
        return firestore.client()

# Helper function to convert Firestore document to a dictionary
def document_to_dict(doc):
    """Convert a Firestore document to a dictionary."""
    if not doc:
        return None
        
    doc_dict = doc.to_dict()
    # Add the document ID as a field
    if doc_dict:
        doc_dict['id'] = doc.id
    return doc_dict

# Helper function to convert Python objects to JSON serializable types
def convert_to_serializable(data):
    """Convert Python objects to JSON serializable types."""
    if isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        return {k: convert_to_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    else:
        return data

# CRUD operations for Firestore

async def get_document(collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a document from a collection by its ID.
    
    Args:
        collection_name: Name of the collection
        doc_id: ID of the document to retrieve
        
    Returns:
        Document data as a dictionary, or None if document doesn't exist
    """
    try:
        db = get_db()
        doc_ref = db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            data = document_to_dict(doc)
            return convert_to_serializable(data)
        else:
            return None
    except Exception as e:
        print(f"Error getting document: {e}")
        return None

async def add_document(collection_name: str, doc_id: str, data: Dict[str, Any]) -> str:
    """
    Add a new document to a collection with a specific ID.
    
    Args:
        collection_name: Name of the collection
        doc_id: ID for the new document
        data: Document data as a dictionary
        
    Returns:
        ID of the created document
    """
    try:
        db = get_db()
        doc_ref = db.collection(collection_name).document(doc_id)
        doc_ref.set(data)
        return doc_id
    except Exception as e:
        print(f"Error adding document: {e}")
        raise

async def update_document(collection_name: str, doc_id: str, data: Dict[str, Any]) -> bool:
    """
    Update an existing document.
    
    Args:
        collection_name: Name of the collection
        doc_id: ID of the document to update
        data: Updated document data as a dictionary
        
    Returns:
        True if update was successful, False otherwise
    """
    try:
        db = get_db()
        doc_ref = db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.update(data)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error updating document: {e}")
        return False

async def delete_document(collection_name: str, doc_id: str) -> bool:
    """
    Delete a document from a collection.
    
    Args:
        collection_name: Name of the collection
        doc_id: ID of the document to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        db = get_db()
        doc_ref = db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.delete()
            return True
        else:
            return False
    except Exception as e:
        print(f"Error deleting document: {e}")
        return False

async def query_documents(
    collection_name: str, 
    field: str = None, 
    operator: str = None, 
    value: Any = None,
    order_by: str = None,
    direction: str = "ASCENDING",
    limit: int = 50,
    start_after: Any = None
) -> List[Dict[str, Any]]:
    """
    Query documents in a collection with filtering, ordering, and pagination.
    
    Args:
        collection_name: Name of the collection
        field: Field to filter on (optional)
        operator: Comparison operator (==, >, <, >=, <=, array_contains, in)
        value: Value to compare against
        order_by: Field to order results by
        direction: Direction to order (ASCENDING or DESCENDING)
        limit: Maximum number of documents to return
        start_after: Document to start after for pagination
        
    Returns:
        List of documents matching the query
    """
    try:
        db = get_db()
        query = db.collection(collection_name)
        
        # Apply filter if specified
        if field and operator and value is not None:
            query = query.where(field, operator, value)
        
        # Apply ordering if specified
        if order_by:
            direction_obj = firestore.Query.ASCENDING if direction == "ASCENDING" else firestore.Query.DESCENDING
            query = query.order_by(order_by, direction=direction_obj)
        
        # Apply pagination if specified
        if start_after:
            query = query.start_after(start_after)
            
        # Apply limit
        query = query.limit(limit)
        
        # Execute query
        docs = query.stream()
        
        # Convert to list of dictionaries
        results = []
        for doc in docs:
            doc_dict = document_to_dict(doc)
            if doc_dict:
                results.append(convert_to_serializable(doc_dict))
                
        return results
    except Exception as e:
        print(f"Error querying documents: {e}")
        return []

async def batch_get_documents(collection_name: str, doc_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Get multiple documents by their IDs.
    
    Args:
        collection_name: Name of the collection
        doc_ids: List of document IDs to retrieve
        
    Returns:
        List of documents
    """
    try:
        db = get_db()
        docs = []
        
        # Firestore doesn't have a native batch get, so we do multiple gets
        for doc_id in doc_ids:
            doc = await get_document(collection_name, doc_id)
            if doc:
                docs.append(doc)
                
        return docs
    except Exception as e:
        print(f"Error batch getting documents: {e}")
        return []

async def batch_add_documents(collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
    """
    Add multiple documents in a batch operation.
    
    Args:
        collection_name: Name of the collection
        documents: List of documents to add, each with an 'id' field
        
    Returns:
        List of document IDs that were added
    """
    try:
        db = get_db()
        batch = db.batch()
        doc_ids = []
        
        for doc in documents:
            doc_id = doc.get('id')
            if not doc_id:
                # Generate a new ID if not provided
                doc_ref = db.collection(collection_name).document()
                doc_id = doc_ref.id
            else:
                doc_ref = db.collection(collection_name).document(doc_id)
                
            # Remove id from the data to avoid duplication
            if 'id' in doc:
                data = doc.copy()
                data.pop('id')
            else:
                data = doc
                
            batch.set(doc_ref, data)
            doc_ids.append(doc_id)
            
        # Commit the batch
        batch.commit()
        return doc_ids
    except Exception as e:
        print(f"Error batch adding documents: {e}")
        raise

async def link_candidate_profiles(user_id: str, profile_links: Dict[str, str]) -> bool:
    """
    Link multiple profile types for a candidate (resume, GitHub, LeetCode).
    
    Args:
        user_id: The user ID of the candidate
        profile_links: Dictionary containing profile IDs to link, with keys like
                      'resume_id', 'github_profile_id', 'leetcode_username'
        
    Returns:
        True if linking was successful, False otherwise
    """
    try:
        db = get_db()
        
        # Create or update candidate profile in a dedicated collection
        candidate_ref = db.collection("candidates").document(user_id)
        candidate_doc = candidate_ref.get()
        
        # Prepare data for candidate document
        candidate_data = {
            "updated_at": datetime.now(),
        }
        
        # Add links to different profile types
        if 'resume_id' in profile_links and profile_links['resume_id']:
            candidate_data['latest_resume_id'] = profile_links['resume_id']
            candidate_data['has_resume'] = True
            
        if 'github_profile_id' in profile_links and profile_links['github_profile_id']:
            candidate_data['github_profile_id'] = profile_links['github_profile_id']
            candidate_data['has_github_profile'] = True
            
        if 'github_username' in profile_links and profile_links['github_username']:
            candidate_data['github_username'] = profile_links['github_username']
            
        if 'leetcode_username' in profile_links and profile_links['leetcode_username']:
            candidate_data['leetcode_username'] = profile_links['leetcode_username']
            candidate_data['has_leetcode_profile'] = True
        
        # Add a combined profiles field for easy retrieval
        linked_profiles = {}
        if 'resume_id' in profile_links and profile_links['resume_id']:
            linked_profiles['resume'] = profile_links['resume_id']
        if 'github_profile_id' in profile_links and profile_links['github_profile_id']:
            linked_profiles['github'] = profile_links['github_profile_id']
        if 'leetcode_username' in profile_links and profile_links['leetcode_username']:
            linked_profiles['leetcode'] = profile_links['leetcode_username']
            
        if linked_profiles:
            candidate_data['linked_profiles'] = linked_profiles
            candidate_data['profiles_last_updated'] = datetime.now()
        
        # Create or update the candidate document
        if candidate_doc.exists:
            # Merge with existing data instead of overwriting
            candidate_ref.update(candidate_data)
        else:
            candidate_data['created_at'] = datetime.now()
            candidate_data['user_id'] = user_id  # Store reference to the user
            candidate_ref.set(candidate_data)
            
        # Add a reference to the candidate profile in the user document
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_ref.update({
                "candidate_profile_id": user_id,
                "has_candidate_profile": True,
                "profiles_last_updated": datetime.now()
            })
        else:
            # Create minimal user document if it doesn't exist
            user_ref.set({
                "created_at": datetime.now(),
                "candidate_profile_id": user_id,
                "has_candidate_profile": True
            })
            
        # Create the unified candidate profile document
        await create_unified_candidate_profile(user_id)
        
        return True
    except Exception as e:
        print(f"Error linking candidate profiles: {e}")
        return False

async def create_unified_candidate_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Create a unified candidate profile combining data from resume, GitHub, and LeetCode.
    
    Args:
        user_id: The user ID of the candidate
        
    Returns:
        Unified candidate profile data, or None if creation failed
    """
    try:
        db = get_db()
        candidate_ref = db.collection("candidates").document(user_id)
        candidate_doc = candidate_ref.get()
        
        if not candidate_doc.exists:
            # Fallback to user document if candidate doesn't exist
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            if not user_doc.exists:
                return None
            candidate_data = user_doc.to_dict()
        else:
            candidate_data = candidate_doc.to_dict()
            
        unified_profile = {
            "user_id": user_id,
            "last_updated": datetime.now()
        }
        
        # Get resume data if available
        resume_id = candidate_data.get('latest_resume_id')
        if resume_id:
            resume_doc = await get_document("resumes", resume_id)
            if resume_doc:
                unified_profile["resume"] = {
                    "id": resume_id,
                    "extracted_content": resume_doc.get("extracted_content"),
                    "timestamp": resume_doc.get("timestamp")
                }
        
        # Get GitHub profile data if available
        github_profile_id = candidate_data.get('github_profile_id')
        if github_profile_id:
            github_doc = await get_document("github_profiles", github_profile_id)
            if github_doc:
                # Extract key skills and stats from GitHub
                github_username = github_doc.get("github_username")
                insights_data = github_doc.get("insights_data", {})
                
                github_summary = {
                    "id": github_profile_id,
                    "username": github_username,
                    "timestamp": github_doc.get("timestamp")
                }
                
                # Include top languages if available
                if insights_data and "top_languages" in insights_data:
                    github_summary["top_languages"] = list(insights_data.get("top_languages", {}).keys())[:5]
                    
                # Include contribution activity if available
                if insights_data and "contribution_activity" in insights_data:
                    github_summary["activity"] = insights_data.get("contribution_activity")
                    
                unified_profile["github"] = github_summary
        
        # Get LeetCode profile data if available
        leetcode_username = candidate_data.get('leetcode_username')
        if leetcode_username:
            leetcode_doc = await get_document("leetcode_profiles", leetcode_username)
            if leetcode_doc:
                # Extract key stats from LeetCode
                profile_data = leetcode_doc.get("profile_data", {})
                
                leetcode_summary = {
                    "username": leetcode_username,
                    "timestamp": leetcode_doc.get("timestamp")
                }
                
                # Extract solving stats if available
                user_problems = profile_data.get("userProblemsSolved", {})
                matched_user = user_problems.get("matchedUser", {})
                if matched_user and "submitStatsGlobal" in matched_user:
                    submit_stats = matched_user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
                    if submit_stats:
                        leetcode_summary["problems_solved"] = {
                            item.get("difficulty"): item.get("count") for item in submit_stats
                        }
                
                unified_profile["leetcode"] = leetcode_summary
        
        # Store the unified profile
        unified_ref = db.collection("unified_profiles").document(user_id)
        unified_ref.set(unified_profile)
        
        return unified_profile
    except Exception as e:
        print(f"Error creating unified candidate profile: {e}")
        return None

async def get_unified_candidate_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the unified candidate profile for a user.
    
    Args:
        user_id: The user ID of the candidate
        
    Returns:
        Unified candidate profile data, or None if not found
    """
    try:
        db = get_db()
        profile_ref = db.collection("unified_profiles").document(user_id)
        profile_doc = profile_ref.get()
        
        if profile_doc.exists:
            return document_to_dict(profile_doc)
        else:
            # Try to create it if it doesn't exist but we have profile data
            return await create_unified_candidate_profile(user_id)
    except Exception as e:
        print(f"Error getting unified candidate profile: {e}")
        return None
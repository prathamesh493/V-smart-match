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
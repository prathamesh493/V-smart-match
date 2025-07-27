# service/pinecone_service.py

import os
from dotenv import load_dotenv
from pinecone import Pinecone
from typing import List, Dict, Any

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize Pinecone only if API key is available
if PINECONE_API_KEY and PINECONE_API_KEY != "dummy_key_for_testing":
    pc = Pinecone(api_key=PINECONE_API_KEY)
    INDEX_NAME = "vsmart-embeddings"
    index = pc.Index(INDEX_NAME)
else:
    pc = None
    index = None
    INDEX_NAME = "vsmart-embeddings"

def get_index():
    if pc is None:
        raise RuntimeError("Pinecone not initialized. Please set PINECONE_API_KEY environment variable.")
    return pc.Index(INDEX_NAME)

def upsert_embedding(id: str, embedding: List[float], metadata: Dict[str, Any]):
    if index is None:
        raise RuntimeError("Pinecone not initialized. Please set PINECONE_API_KEY environment variable.")
    index.upsert([(id, embedding, metadata)])

def query_embedding(embedding: List[float], top_k: int = 5):
    index = get_index()
    return index.query(vector=embedding, top_k=top_k, include_metadata=True)

def query_by_metadata(filter_dict: Dict[str, Any], top_k: int = 100):
    """Query documents by metadata filter"""
    if index is None:
        raise RuntimeError("Pinecone not initialized. Please set PINECONE_API_KEY environment variable.")
    # Use a zero vector with the correct dimension (768 for your index)
    return index.query(vector=[0.0] * 768, filter=filter_dict, top_k=top_k, include_metadata=True)

def delete_by_ids(ids: List[str]):
    """Delete documents by their IDs"""
    if index is None:
        raise RuntimeError("Pinecone not initialized. Please set PINECONE_API_KEY environment variable.")
    if ids:
        index.delete(ids=ids)

def delete_by_metadata_filter(filter_dict: Dict[str, Any]):
    """Delete documents by metadata filter"""
    if index is None:
        raise RuntimeError("Pinecone not initialized. Please set PINECONE_API_KEY environment variable.")
    
    # Use Pinecone's delete with filter directly (more efficient)
    try:
        # Try direct delete with filter first (if supported)
        index.delete(filter=filter_dict)
        return "deleted"  # We can't get exact count with direct filter delete
    except Exception as e:
        # Fallback to query then delete if direct filter delete is not supported
        results = query_by_metadata(filter_dict, top_k=100)
        
        if results.matches:
            ids_to_delete = [match.id for match in results.matches]
            delete_by_ids(ids_to_delete)
            return len(ids_to_delete)
        return 0
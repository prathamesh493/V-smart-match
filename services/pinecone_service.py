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
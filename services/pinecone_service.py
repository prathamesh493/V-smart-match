# service/pinecone_service.py

import os
from pinecone import Pinecone
from typing import List, Dict, Any

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key="pcsk_28MgEy_PotSsF19LHaX42NLpfeQQikpFFmEToxc5GZSXjBixGz1p6YAydL6h6yUKfoxbhF")

INDEX_NAME = "vsmart-embeddings"
index = pc.Index(INDEX_NAME)

def get_index():
    return pc.Index(INDEX_NAME)

def upsert_embedding(id: str, embedding: List[float], metadata: Dict[str, Any]):
    index = get_index()
    index.upsert([(id, embedding, metadata)])

def query_embedding(embedding: List[float], top_k: int = 5):
    index = get_index()
    return index.query(vector=embedding, top_k=top_k, include_metadata=True)
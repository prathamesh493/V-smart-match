# service/embedding.py

#Method 1
# from sentence_transformers import SentenceTransformer

# # You can choose a different model if you prefer
# model = SentenceTransformer("all-MiniLM-L6-v2")

# def get_embedding(text: str) -> list:
#     embedding = model.encode(text)
#     return embedding.tolist()

#Method 2
# from transformers import AutoModel
# model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-en', trust_remote_code=True)

# def get_embedding(text: str) -> list:
#     embedding = model.encode(text)
#     return embedding.tolist()

import requests

API_URL = "https://goofydog-vsmartmatchemeddingcreation.hf.space/embed"  # replace with your actual HF Space URL

def get_embedding(text: str) -> list:
    response = requests.post(API_URL, json={"text": text})
    response.raise_for_status()  # raise error if request failed
    data = response.json()
    return data["embedding"]

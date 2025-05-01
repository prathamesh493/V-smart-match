import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-04-17")

# Firebase/Firestore config
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")

# Application settings
MAX_UPLOAD_SIZE =  10 * 1024 * 1024 # 10MB by default
ALLOWED_FILE_TYPES = ["application/pdf"]
RESUME_STORAGE_PATH = os.getenv("RESUME_STORAGE_PATH", "data/resumes")

# Create storage directory if it doesn't exist
os.makedirs(RESUME_STORAGE_PATH, exist_ok=True)
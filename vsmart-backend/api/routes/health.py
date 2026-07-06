from fastapi import APIRouter, status
from datetime import datetime

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Simple health check endpoint to verify API is running
    """
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "service": "VSmart Backend API",
        "version": "0.1.0"
    }
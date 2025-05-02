# api/routes/profile.py

from fastapi import APIRouter, HTTPException, Query
from services.profile_aggregator import get_leetcode_data
from api.schemas.profile import LeetCodeProfileResponse
import asyncio

router = APIRouter()

@router.get(
    "/leetcode/{username}", 
    response_model=LeetCodeProfileResponse, 
    summary="Get LeetCode profile data",
    description="Retrieves raw LeetCode profile data for a given username. Checks Firestore cache first, falls back to live API if not cached."
)
async def get_leetcode_profile(
    username: str, 
    force_refresh: bool = Query(False, description="Force refresh data from LeetCode API instead of using cached data")
):
    """
    Retrieves LeetCode profile data for a given username.
    
    - **username**: LeetCode username to fetch data for
    - **force_refresh**: Set to true to force a refresh from the LeetCode API instead of using cached data
    
    Returns the raw LeetCode profile data as returned by their GraphQL API.
    """
    try:
        # Get LeetCode data with caching
        data = await get_leetcode_data(username, force_refresh)
        return data
    except Exception as e:
        # Handle exceptions, like user not found
        raise HTTPException(status_code=404, detail=str(e))
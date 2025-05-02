# services/profile_aggregator.py

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from services.leetcode import LeetcodeService
from services.firestore import get_user_data, store_user_data

# Initialize the LeetCode service
leetcode_service = LeetcodeService()

async def get_leetcode_data(username: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Get LeetCode profile data for a user
    
    Args:
        username: LeetCode username
        force_refresh: Force a refresh from LeetCode API instead of using cached data
        
    Returns:
        Dictionary containing LeetCode profile data
    """
    # Check if we have cached data in Firestore
    if not force_refresh:
        cached_data = await get_cached_leetcode_data(username)
        if cached_data:
            print("Data Already Present")
            return cached_data
    
    # If no cached data or force refresh, fetch from LeetCode API
    leetcode_data = leetcode_service.fetch_user_profile(username)
    
    # Check if data was successfully retrieved
    if not leetcode_data or not leetcode_data.get("userPublicProfile", {}).get("matchedUser"):
        # If not found, raise an exception
        raise Exception(f"LeetCode user '{username}' not found or API request failed")
    
    # Store the data in Firestore
    await store_leetcode_data(username, leetcode_data)
    
    return leetcode_data

async def get_cached_leetcode_data(username: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached LeetCode data from Firestore if it exists
    
    Args:
        username: LeetCode username
        
    Returns:
        Dictionary containing cached LeetCode data or None if not found
    """
    # Try to get the cached data from Firestore
    cached_data = await get_user_data("leetcode_profiles", username)
    
    # If no cached data, return None
    if not cached_data:
        return None
    
    # Return the cached profile data (permanently stored)
    return cached_data.get("profile_data", {})


async def store_leetcode_data(username: str, profile_data: Dict[str, Any]) -> None:
    """
    Store LeetCode profile data in Firestore
    
    Args:
        username: LeetCode username
        profile_data: Dictionary containing LeetCode profile data
    """
    # Create a document to store
    document = {
        "username": username,
        "timestamp": datetime.now(),
        "profile_data": profile_data
    }
    
    # Store in Firestore
    await store_user_data("leetcode_profiles", username, document)

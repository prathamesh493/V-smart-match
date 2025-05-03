# services/profile_aggregator.py

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from services.leetcode import LeetcodeService
from services.github import get_github_insights
from services.firebase import get_db, document_to_dict, convert_to_serializable
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

async def get_github_data(username: str, user_id: str = None, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Get GitHub profile data for a user
    
    Args:
        username: GitHub username
        user_id: Optional user ID to associate with this GitHub profile
        force_refresh: Force a refresh from GitHub API instead of using cached data
        
    Returns:
        Dictionary containing GitHub profile insights
    """
    # Use a default user ID if none provided
    user_id = user_id or "anonymous"
    
    # Check if we have cached data in Firestore
    if not force_refresh:
        cached_data = await get_cached_github_data(username, user_id)
        if cached_data and isinstance(cached_data, dict) and "insights_data" in cached_data:
            print("GitHub data already present")
            return cached_data.get("insights_data", {})
    
    # If no cached data or force refresh, fetch from GitHub API
    github_data = get_github_insights(username)
    
    # Check if data was successfully retrieved
    if not github_data or not github_data.get("basic_info", {}).get("username"):
        # If not found, raise an exception
        raise Exception(f"GitHub user '{username}' not found or API request failed")
    
    # Generate markdown from the data
    markdown_content = generate_markdown_from_insights(github_data)
    
    # Store the data in Firestore
    await store_github_data(username, github_data, markdown_content, user_id)
    
    return github_data

async def get_cached_github_data(username: str, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached GitHub data from Firestore if it exists
    
    Args:
        username: GitHub username
        user_id: User ID associated with this GitHub profile
        
    Returns:
        Dictionary containing cached GitHub data or None if not found
    """
    try:
        db = get_db()
        # Try to find the most recent GitHub profile for this user and username
        profiles_ref = db.collection("github_profiles").where("user_id", "==", user_id).where("github_username", "==", username)
        profiles = profiles_ref.get()
        
        if not profiles or len(profiles) == 0:
            return None
            
        # Return the most recent profile if multiple exist
        profiles_dict = [document_to_dict(doc) for doc in profiles]
        profiles_sorted = sorted(profiles_dict, key=lambda x: x.get("timestamp"), reverse=True)
        return profiles_sorted[0] if profiles_sorted else None
    except Exception as e:
        print(f"Error retrieving cached GitHub data: {str(e)}")
        return None

async def store_github_data(username: str, insights_data: Dict[str, Any], markdown_content: str, user_id: str) -> str:
    """
    Store GitHub profile data in Firestore
    
    Args:
        username: GitHub username
        insights_data: Dictionary containing GitHub profile insights
        markdown_content: Markdown representation of the profile
        user_id: User ID to associate with this profile
        
    Returns:
        Document ID of the stored profile
    """
    try:
        db = get_db()
        
        # Create document for storage
        timestamp = datetime.now()
        doc_data = {
            "user_id": user_id,
            "github_username": username,
            "timestamp": timestamp,
            "insights_data": convert_to_serializable(insights_data),
            "markdown_content": markdown_content,
            "processed": True
        }
        
        # Store in Firestore
        github_ref = db.collection("github_profiles").document()
        github_ref.set(doc_data)
        
        # Update user document with reference to this GitHub profile
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        user_data = {
            "github_profile_id": github_ref.id,
            "github_username": username,
            "github_profile_timestamp": timestamp,
            "has_github_profile": True
        }
        
        # Create or update user document
        if not user_doc.exists:
            user_data["created_at"] = timestamp
            
        user_ref.set(user_data, merge=True)
        
        # Also add to user's profiles collection
        user_profiles_ref = user_ref.collection("profiles").document(github_ref.id)
        user_profiles_ref.set({
            "profile_id": github_ref.id,
            "profile_type": "github",
            "username": username,
            "timestamp": timestamp
        })
        
        return github_ref.id
    except Exception as e:
        print(f"Error storing GitHub data: {str(e)}")
        raise Exception(f"Failed to store GitHub profile data: {str(e)}")

def generate_markdown_from_insights(insights_data: Dict[str, Any]) -> str:
    """
    Generate a markdown profile from GitHub insights data.
    """
    md = []
    
    # Header section
    basic_info = insights_data.get("basic_info", {})
    name = basic_info.get("name") or basic_info.get("username", "GitHub User")
    md.append(f"# GitHub Profile: {name}\n")

    # Basic information
    md.append("## Developer Profile\n")
    if basic_info.get("bio"):
        md.append(f"{basic_info.get('bio')}\n")
    if basic_info.get("company"):
        md.append(f"🏢 Works at: {basic_info.get('company')}\n")
    if basic_info.get("blog"):
        md.append(f"🔗 Website/Blog: {basic_info.get('blog')}\n")
    md.append(f"📂 Public repositories: {basic_info.get('public_repos', 0)}\n\n")

    # Technical skills section - Top languages
    md.append("## Technical Skills\n")
    md.append("### Top Programming Languages\n")
    top_languages = insights_data.get("top_languages", {})
    if top_languages:
        total_bytes = sum(top_languages.values())
        md.append("| Language | Usage |\n")
        md.append("|----------|-------|\n")
        for lang, bytes_count in list(top_languages.items())[:8]:
            percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
            md.append(f"| {lang} | {percentage:.1f}% |\n")
        md.append("\n")
    else:
        md.append("No language data available.\n\n")

    # Technical keywords from READMEs
    tech_prefs = insights_data.get("tech_preferences", {})
    readme_techs = tech_prefs.get("from_readme", [])
    md.append("### Technologies (from READMEs)\n")
    if readme_techs:
        md.append(", ".join(readme_techs) + "\n\n")
    else:
        md.append("No technology keywords detected in READMEs.\n\n")

    # Repository topics
    md.append("### Preferred Topics\n")
    repo_topics = insights_data.get("repo_topics", [])
    if repo_topics:
        topics = [f"`{topic.get('topic')}`" for topic in repo_topics[:10]]
        md.append(" ".join(topics) + "\n\n")
    else:
        md.append("No repository topics found.\n\n")

    # Personal projects section
    md.append("## Personal Projects\n")
    personal_projects = insights_data.get("personal_projects", [])
    if personal_projects:
        # Sort projects by stars (descending)
        projects = sorted(personal_projects, key=lambda x: x.get('stars', 0), reverse=True)[:5]
        for project in projects:
            md.append(f"### [{project.get('name')}]({project.get('url')})\n")
            if project.get('description'):
                md.append(f"{project.get('description')}\n\n")
            details = []
            if project.get('language'):
                details.append(f"**Language**: {project.get('language')}")
            if project.get('stars', 0) > 0:
                details.append(f"**Stars**: {project.get('stars')}")
            if details:
                md.append(" | ".join(details) + "\n\n")
    else:
        md.append("No personal projects found.\n\n")

    # Activity section
    md.append("## Recent Activity\n")
    md.append("### Most Active Repositories\n")
    active_repos = insights_data.get("most_active_repos", [])
    if active_repos:
        for repo in active_repos[:3]:
            md.append(f"- [{repo.get('name', '')}]({repo.get('url', '')}) - {repo.get('description', 'No description')}\n")
        md.append("\n")
    else:
        md.append("No active repositories found.\n\n")

    # Recent commits
    contribution_activity = insights_data.get("contribution_activity", {})
    md.append("### Contribution Activity\n")
    md.append(f"- **Last 30 days**: {contribution_activity.get('last_30_days', 0)} commits\n")
    md.append(f"- **Last 90 days**: {contribution_activity.get('last_90_days', 0)} commits\n\n")

    # Open source contributions
    open_source = insights_data.get("open_source_contributions", {})
    md.append("## Open Source Contributions\n")
    prs = open_source.get("pull_requests", [])
    issues = open_source.get("issues", [])
    
    if prs or issues:
        # Pull Requests
        if prs:
            md.append(f"### Pull Requests ({len(prs)})\n")
            for pr in prs[:5]:  # Show top 5 PRs
                md.append(f"- [{pr.get('title', '')}]({pr.get('url', '')}) in {pr.get('repo', '')} ({pr.get('state', '')})\n")
            md.append("\n")

        # Issues
        if issues:
            md.append(f"### Issues ({len(issues)})\n")
            for issue in issues[:5]:  # Show top 5 issues
                md.append(f"- [{issue.get('title', '')}]({issue.get('url', '')}) in {issue.get('repo', '')} ({issue.get('state', '')})\n")
            md.append("\n")
    else:
        md.append("No open source contributions found or token not provided.\n\n")

    # Add metadata footer with LLM-friendly analysis hints
    md.append("---\n\n")
    md.append("## Profile Analysis for LLMs\n\n")
    md.append("### Key Strengths:\n")

    # Language strengths
    top_langs = list(insights_data.get("top_languages", {}).keys())[:3]
    if top_langs:
        md.append(f"- Primarily works with: {', '.join(top_langs)}\n")

    # Project focus
    if repo_topics and len(repo_topics) > 0:
        top_topics = [topic.get('topic') for topic in repo_topics[:3]]
        md.append(f"- Focus areas: {', '.join(top_topics)}\n")

    # Activity level
    if contribution_activity.get('last_30_days', 0) > 10:
        md.append("- Very active developer with consistent contributions\n")
    elif contribution_activity.get('last_90_days', 0) > 20:
        md.append("- Moderately active developer\n")

    # Open source involvement
    if prs:
        if len(prs) > 5:
            md.append("- Strong open source contributor\n")
        else:
            md.append("- Has open source contribution experience\n")

    md.append(f"\nProfile generated on {datetime.now().strftime('%Y-%m-%d')}\n")
    
    return "".join(md)

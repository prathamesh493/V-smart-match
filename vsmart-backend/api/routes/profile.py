# api/routes/profile.py

from fastapi import APIRouter, HTTPException, Query, Depends, Path
from typing import Dict, Any, List, Optional

from services.profile_aggregator import get_leetcode_data
from api.schemas.profile import LeetCodeProfileResponse
from api.schemas.github import ErrorResponse
from api.auth import get_current_user, UserData, get_optional_user

router = APIRouter()

@router.get(
    "/leetcode/{username}", 
    response_model=Dict[str, Any], 
    responses={404: {"model": ErrorResponse}},
    summary="Get LeetCode profile data",
    description="Retrieves raw LeetCode profile data for a given username. Checks Firestore cache first, falls back to live API if not cached."
)
async def get_leetcode_profile(
    username: str, 
    force_refresh: bool = Query(False, description="Force refresh data from LeetCode API instead of using cached data"),
    current_user: UserData = Depends(get_optional_user)
):
    """
    Retrieves LeetCode profile data for a given username.
    
    - **username**: LeetCode username to fetch data for
    - **force_refresh**: Set to true to force a refresh from the LeetCode API instead of using cached data
    
    Returns the raw LeetCode profile data as returned by their GraphQL API.
    """
    try:
        # Get LeetCode data with caching, passing the authenticated user ID
        data = await get_leetcode_data(username, force_refresh, user_id=current_user.user_id)
        return data
    except Exception as e:
        # Handle exceptions, like user not found
        raise HTTPException(status_code=404, detail=str(e))

@router.get(
    "/profiles/{user_id}",
    response_model=Dict[str, Any],
    summary="Get all developer profiles for a user",
    description="Retrieves all developer profiles (GitHub, LeetCode, Resume) associated with a specific user."
)
async def get_user_profiles(
    user_id: str = Path(..., description="User ID to fetch profiles for"),
    current_user: UserData = Depends(get_current_user)
):
    """
    Retrieves all developer profiles for a specific user.
    
    - **user_id**: User ID to fetch profiles for
    
    Returns a dictionary with GitHub, LeetCode, and Resume data if they exist.
    """
    # For security, only allow users to access their own profiles
    # Allow access to "string" user ID for testing purposes and "admin" for administrative access
    if current_user.user_id != user_id and current_user.user_id != "admin" and user_id != "string":
        raise HTTPException(status_code=403, detail="Not authorized to access these profiles")
    
    try:
        from services.firebase import get_document, query_documents
        
        # Initialize the result dictionary with all profile types
        result = {"github": None, "leetcode": None, "resume": None}
        
        # First check the candidates collection (new structure)
        candidate_doc = await get_document("candidates", user_id)
        
        # If not found in candidates, check the users collection (old structure)
        if not candidate_doc:
            user_doc = await get_document("users", user_id)
            if not user_doc:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            profile_doc = user_doc
        else:
            profile_doc = candidate_doc
        
        # Get GitHub profile if it exists
        if profile_doc.get("github_profile_id"):
            github_profile = await get_document("github_profiles", profile_doc["github_profile_id"])
            if github_profile:
                result["github"] = github_profile.get("insights_data")
        elif profile_doc.get("github_username"):
            # If we only have the username but no profile ID
            result["github"] = {"username": profile_doc.get("github_username")}
        
        # Get LeetCode profile if it exists
        if profile_doc.get("leetcode_username"):
            leetcode_username = profile_doc["leetcode_username"]
            leetcode_profile = await get_document("leetcode_profiles", leetcode_username)
            if leetcode_profile:
                result["leetcode"] = leetcode_profile.get("profile_data")
            else:
                # Include at least the username if we can't find the full profile
                result["leetcode"] = {"username": leetcode_username}
        
        # Get Resume data if it exists
        resume_id = profile_doc.get("latest_resume_id")
        if resume_id:
            resume_data = await get_document("resumes", resume_id)
            if resume_data:
                result["resume"] = {
                    "id": resume_id,
                    "extracted_content": resume_data.get("extracted_content"),
                    "timestamp": resume_data.get("timestamp"),
                    "metadata": resume_data.get("metadata", {})
                }
        else:
            # If no specific resume ID is linked, try to find the most recent resume for this user
            resumes = await query_documents(
                collection_name="resumes",
                field="user_id", 
                operator="==", 
                value=user_id,
                order_by="timestamp",
                direction="DESCENDING",
                limit=1
            )
            
            if resumes and len(resumes) > 0:
                resume_data = resumes[0]
                result["resume"] = {
                    "id": resume_data.get("id"),
                    "extracted_content": resume_data.get("extracted_content"),
                    "timestamp": resume_data.get("timestamp"),
                    "metadata": resume_data.get("metadata", {})
                }
                
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profiles: {str(e)}")

@router.get(
    "/profiles/{user_id}/report",
    response_model=Dict[str, Any],
    summary="Get comprehensive report data for a user",
    description="Retrieves aggregated report data including GitHub stats, LeetCode progress, and resume insights."
)
async def get_user_report(
    user_id: str = Path(..., description="User ID to fetch report data for"),
    current_user: UserData = Depends(get_current_user)
):
    """
    Retrieves comprehensive report data for a specific user.
    
    - **user_id**: User ID to fetch report data for
    
    Returns a dictionary with aggregated metrics and insights from all user profiles.
    """
    # For security, only allow users to access their own reports
    if current_user.user_id != user_id and current_user.user_id != "admin" and user_id != "string":
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    
    try:
        from services.firebase import get_document, query_documents
        
        # Get all profile data first
        profiles = await get_user_profiles(user_id=user_id, current_user=current_user)
        
        # Initialize report structure
        report = {
            "skills": {
                "technical": [],
                "soft": []
            },
            "githubStats": {
                "commits": 0,
                "repositories": 0,
                "stars": 0,
                "followers": 0,
                "contributions": 0,
                "topLanguages": []
            },
            "leetcodeStats": {
                "solved": 0,
                "easy": 0,
                "medium": 0,
                "hard": 0,
                "ranking": 0,
                "streak": 0
            },
            "matchingStats": {
                "averageMatchScore": 0,
                "totalApplications": 0,
                "topMatches": []
            },
            "skillGaps": [],
            "improvementAreas": [],
            "strengths": []
        }
        
        # Extract GitHub stats if available
        if profiles.get("github") and isinstance(profiles["github"], dict):
            github_data = profiles["github"]
            
            # Repositories data
            if "user" in github_data and "repositories" in github_data["user"]:
                repos = github_data["user"]["repositories"].get("nodes", [])
                report["githubStats"]["repositories"] = len(repos)
                
                # Calculate stars
                stars = sum(repo.get("stargazerCount", 0) for repo in repos)
                report["githubStats"]["stars"] = stars
            
            # Followers
            if "user" in github_data and "followers" in github_data["user"]:
                report["githubStats"]["followers"] = github_data["user"]["followers"].get("totalCount", 0)
            
            # Contributions
            if "user" in github_data and "contributionsCollection" in github_data["user"]:
                contribs = github_data["user"]["contributionsCollection"]
                report["githubStats"]["commits"] = contribs.get("totalCommitContributions", 0)
                report["githubStats"]["contributions"] = sum([
                    contribs.get("totalCommitContributions", 0),
                    contribs.get("totalIssueContributions", 0),
                    contribs.get("totalPullRequestContributions", 0),
                    contribs.get("totalPullRequestReviewContributions", 0)
                ])
            
            # Top languages
            if "user" in github_data and "repositories" in github_data["user"]:
                lang_count = {}
                for repo in github_data["user"]["repositories"].get("nodes", []):
                    if "languages" in repo and "edges" in repo["languages"]:
                        for lang_edge in repo["languages"]["edges"]:
                            lang = lang_edge.get("node", {}).get("name")
                            size = lang_edge.get("size", 0)
                            if lang:
                                lang_count[lang] = lang_count.get(lang, 0) + size
                
                # Sort languages by size and take top 5
                top_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:5]
                report["githubStats"]["topLanguages"] = [{"name": lang, "value": size} for lang, size in top_langs]
        
        # Extract LeetCode stats if available
        if profiles.get("leetcode") and isinstance(profiles["leetcode"], dict):
            leetcode_data = profiles["leetcode"]
            
            if "matchedUser" in leetcode_data:
                user_data = leetcode_data["matchedUser"]
                
                # Basic stats
                if "submitStats" in user_data:
                    stats = user_data["submitStats"]
                    report["leetcodeStats"]["solved"] = stats.get("acSubmissionNum", [{"count": 0}])[0].get("count", 0)
                
                # Difficulty breakdown
                if "submitStatsGlobal" in user_data:
                    global_stats = user_data["submitStatsGlobal"]
                    report["leetcodeStats"]["easy"] = global_stats.get("easySolved", 0)
                    report["leetcodeStats"]["medium"] = global_stats.get("mediumSolved", 0)
                    report["leetcodeStats"]["hard"] = global_stats.get("hardSolved", 0)
                
                # Ranking and streak
                report["leetcodeStats"]["ranking"] = user_data.get("profile", {}).get("ranking", 0)
                report["leetcodeStats"]["streak"] = user_data.get("userCalendar", {}).get("streak", 0)
        
        # Extract skills from resume
        if profiles.get("resume") and profiles["resume"].get("extracted_content"):
            resume_content = profiles["resume"]["extracted_content"]
            
            # Try to extract skills from resume content
            all_skills = []
            
            # Look for a skills section in the resume
            import re
            skills_section = re.search(r'(?i)skills?:(.+?)(?:\n\n|\n[A-Z]|\Z)', resume_content, re.DOTALL)
            
            if skills_section:
                skills_text = skills_section.group(1)
                # Split by common delimiters
                skill_items = re.split(r'[,|•|\n]', skills_text)
                all_skills = [skill.strip() for skill in skill_items if skill.strip()]
            
            # Technical vs soft skills categorization (simplified)
            tech_keywords = ['python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'node', 
                          'aws', 'docker', 'kubernetes', 'sql', 'nosql', 'mongodb', 'firebase', 'git', 
                          'html', 'css', 'c++', 'c#', 'rust', 'go', 'php', 'ruby', 'swift', 'kotlin', 
                          'django', 'flask', 'fastapi', 'spring', 'tensorflow', 'pytorch', 'ai', 'ml']
            
            soft_keywords = ['communication', 'leadership', 'teamwork', 'management', 'problem solving', 
                          'critical thinking', 'adaptability', 'time management', 'creativity', 
                          'collaboration', 'conflict resolution', 'negotiation', 'presentation', 
                          'verbal', 'written', 'interpersonal', 'organization', 'flexibility']
            
            for skill in all_skills:
                skill_lower = skill.lower()
                # Check if skill matches any technical keyword
                if any(tech.lower() in skill_lower for tech in tech_keywords):
                    report["skills"]["technical"].append(skill)
                # Check if skill matches any soft skill keyword
                elif any(soft.lower() in skill_lower for soft in soft_keywords):
                    report["skills"]["soft"].append(skill)
                # Default to technical skill if unclassified
                else:
                    report["skills"]["technical"].append(skill)
        
        # Get job application stats
        try:
            applications = await query_documents(
                collection_name="job_applications",
                field="candidate_id", 
                operator="==", 
                value=user_id
            )
            
            # Calculate matching stats
            if applications:
                report["matchingStats"]["totalApplications"] = len(applications)
                
                # Calculate average match score
                match_scores = [app.get("match_score", 0) for app in applications if "match_score" in app]
                if match_scores:
                    report["matchingStats"]["averageMatchScore"] = sum(match_scores) / len(match_scores)
                
                # Get top matches
                top_matches = sorted(applications, key=lambda x: x.get("match_score", 0), reverse=True)[:3]
                for match in top_matches:
                    job_id = match.get("job_id")
                    if job_id:
                        job_doc = await get_document("jobs", job_id)
                        if job_doc:
                            report["matchingStats"]["topMatches"].append({
                                "jobId": job_id,
                                "title": job_doc.get("title", "Unknown Position"),
                                "company": job_doc.get("company", "Unknown Company"),
                                "matchScore": match.get("match_score", 0)
                            })
        except Exception as e:
            # Don't fail the entire report if this part fails
            print(f"Error fetching job applications: {str(e)}")
        
        # Generate AI-based insights
        try:
            from services.gemini import get_analysis
            
            # Compile a summary of the user's profile for analysis
            profile_summary = f"""
            GitHub: {report['githubStats']['repositories']} repositories, {report['githubStats']['stars']} stars, 
            {report['githubStats']['contributions']} contributions.
            Top languages: {', '.join([lang['name'] for lang in report['githubStats']['topLanguages'][:3]])}
            
            LeetCode: {report['leetcodeStats']['solved']} problems solved 
            ({report['leetcodeStats']['easy']} easy, {report['leetcodeStats']['medium']} medium, {report['leetcodeStats']['hard']} hard)
            
            Skills: {', '.join(report['skills']['technical'][:10])}
            """
            
            # Get AI analysis for strengths and improvement areas
            analysis = await get_analysis(profile_summary, "Analyze this developer profile and provide 3 main strengths and 3 areas for improvement")
            
            if analysis:
                # Very simple parsing - in production you would want more robust parsing
                strengths_section = analysis.split("Strengths:")[1].split("Areas for Improvement:")[0] if "Strengths:" in analysis else ""
                improvement_section = analysis.split("Areas for Improvement:")[1] if "Areas for Improvement:" in analysis else ""
                
                # Extract bullet points
                import re
                strengths = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|\Z)', strengths_section)
                improvements = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|\Z)', improvement_section)
                
                report["strengths"] = [s.strip() for s in strengths if s.strip()]
                report["improvementAreas"] = [i.strip() for i in improvements if i.strip()]
                
                # Extract skill gaps based on job market trends
                skill_gaps_analysis = await get_analysis(
                    f"Developer skills: {', '.join(report['skills']['technical'])}",
                    "What 3 in-demand skills is this developer missing based on current job market trends?"
                )
                
                if skill_gaps_analysis:
                    skill_gaps = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|\Z|\n\n)', skill_gaps_analysis)
                    report["skillGaps"] = [s.strip() for s in skill_gaps if s.strip()]
        except Exception as e:
            # Don't fail if AI analysis fails
            print(f"Error generating AI insights: {str(e)}")
            
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
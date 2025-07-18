import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.config import GEMINI_API_KEY
import google.generativeai as genai
from prompts.matcher import JOB_MATCHING_ANALYSIS_PROMPT

# Initialize Gemini with your API key
genai.configure(api_key=GEMINI_API_KEY)

class ResumeJobMatcher:
    """
    Service for matching resumes to job descriptions using Gemini's AI capabilities.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        """
        Initialize the matcher with the specified model.
        
        Args:
            model_name: The Gemini model to use for matching analysis
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
    async def generate_match_analysis(
        self, 
        candidate_id: str, 
        job_description_id: str,
        resume_content: str,
        job_description_content: str,
        github_data: Optional[Dict[str, Any]] = None,
        leetcode_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive match analysis between a resume and job description.
        
        Args:
            candidate_id: The ID of the candidate document
            job_description_id: The ID of the job description document
            resume_content: The extracted content from the resume
            job_description_content: The extracted content from the job description
            github_data: Optional GitHub profile data for enhanced matching
            leetcode_data: Optional LeetCode profile data for enhanced matching
            
        Returns:
            A dictionary containing the complete match analysis
        """
        start_time = time.time()
        
        # Generate a unique ID for this match
        match_id = f"match_{uuid.uuid4().hex}"
        
        # Get the analysis from Gemini
        analysis_result = await self._analyze_match(resume_content, job_description_content, github_data, leetcode_data)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)  # Convert to ms
        
        # Build the complete match result
        match_result = {
            "matchId": match_id,
            "candidateId": candidate_id,
            "jobDescriptionId": job_description_id,
            "createdAt": datetime.now().isoformat(),
            "overallScore": analysis_result.get("overallScore", 0),
            "categoryScores": analysis_result.get("categoryScores", {}),
            "analysis": analysis_result.get("analysis", {
                "summary": "",
                "strengths": [],
                "weaknesses": [],
                "recommendations": []
            }),
            "metadata": {
                "modelVersion": self.model_name,
                "processingTime": processing_time,
                "promptTokens": analysis_result.get("promptTokens", 0),
                "completionTokens": analysis_result.get("completionTokens", 0),
                "usedGithubData": github_data is not None,
                "usedLeetcodeData": leetcode_data is not None
            }
        }
        
        return match_result
        
    async def _analyze_match(
        self, 
        resume_content: str, 
        job_description_content: str,
        github_data: Optional[Dict[str, Any]] = None,
        leetcode_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use Gemini to analyze the match between resume and job description.
        
        Args:
            resume_content: The text content of the resume
            job_description_content: The text content of the job description
            github_data: Optional GitHub profile data for enhanced matching
            leetcode_data: Optional LeetCode profile data for enhanced matching
            
        Returns:
            A dictionary containing the analysis results
        """
        # Construct the prompt for Gemini
        prompt = self._build_analysis_prompt(resume_content, job_description_content, github_data, leetcode_data)
        
        print("Prompt for Gemini:",prompt)
        
        # Send the prompt to Gemini
        try:
            response = await self.model.generate_content_async(prompt)
            
            print("Gemini response:", response)
            
            # Extract the JSON from the response
            analysis_text = response.text
            # Sometimes Gemini might wrap the JSON in markdown code blocks
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
            
            try:
                analysis_result = json.loads(analysis_text)
                
                # Add token usage if available
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    # Input tokens
                    analysis_result["promptTokens"] = response.usage_metadata.prompt_token_count
                    # Output tokens[]
                    analysis_result["completionTokens"] = response.usage_metadata.candidates_token_count
                    # Total billed tokens
                    analysis_result["totalTokens"] = response.usage_metadata.total_token_count
                
                # Ensure all required fields exist
                if "overallScore" not in analysis_result:
                    analysis_result["overallScore"] = 0
                
                if "categoryScores" not in analysis_result:
                    analysis_result["categoryScores"] = {}
                
                if "analysis" not in analysis_result:
                    analysis_result["analysis"] = {
                        "summary": "",
                        "strengths": [],
                        "weaknesses": [],
                        "recommendations": []
                    }
                    
                return analysis_result
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from Gemini response: {str(e)}")
                print(f"Response text: {analysis_text}")
                
                # Return a default structure
                return {
                    "overallScore": 50,
                    "categoryScores": {
                        "skillsMatch": {"score": 50, "confidence": 50, "keyMatches": [], "missingCriticalSkills": []},
                        "experienceMatch": {"score": 50, "confidence": 50, "yearsExperienceMatch": 50, "domainExperienceMatch": 50, "roleAlignmentMatch": 50},
                        "educationMatch": {"score": 50, "confidence": 50, "degreeMatch": 50, "fieldMatch": 50, "certificationsMatch": 50},
                        "softSkillsMatch": {"score": 50, "confidence": 50, "keyMatches": []},
                        "culturalFitMatch": {"score": 50, "confidence": 50, "valueAlignmentScore": 50, "workStyleMatch": 50}
                    },
                    "analysis": {
                        "summary": "Error parsing Gemini response",
                        "strengths": ["Unable to determine"],
                        "weaknesses": ["Unable to determine"],
                        "recommendations": ["Review manually"]
                    }
                }
            
        except Exception as e:
            # Return a error-indicating result
            return {
                "overallScore": 0,
                "error": str(e),
                "categoryScores": {
                    "skillsMatch": {"score": 0, "confidence": 0, "keyMatches": [], "missingCriticalSkills": []},
                    "experienceMatch": {"score": 0, "confidence": 0, "yearsExperienceMatch": 0, "domainExperienceMatch": 0, "roleAlignmentMatch": 0},
                    "educationMatch": {"score": 0, "confidence": 0, "degreeMatch": 0, "fieldMatch": 0, "certificationsMatch": 0},
                    "softSkillsMatch": {"score": 0, "confidence": 0, "keyMatches": []},
                    "culturalFitMatch": {"score": 0, "confidence": 0, "valueAlignmentScore": 0, "workStyleMatch": 0}
                },
                "analysis": {
                    "summary": f"Error analyzing match: {str(e)}",
                    "strengths": [],
                    "weaknesses": ["Unable to properly analyze the match"],
                    "recommendations": ["Review manually or try again later"]
                }
            }
    
    def _build_analysis_prompt(
        self, 
        resume_content: str, 
        job_description_content: str,
        github_data: Optional[Dict[str, Any]] = None,
        leetcode_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a detailed prompt for Gemini to analyze the match.
        
        Args:
            resume_content: The text content of the resume
            job_description_content: The text content of the job description
            github_data: Optional GitHub profile data for enhanced matching
            leetcode_data: Optional LeetCode profile data for enhanced matching
            
        Returns:
            A string containing the prompt for Gemini
        """
        # Prepare GitHub data section if available
        github_section = ""
        if github_data:
            # Extract only the most relevant GitHub data for matching
            github_section = """
# GITHUB PROFILE DATA:
"""
            # Add programming languages
            if github_data.get("insights_data", {}).get("top_languages"):
                languages = github_data["insights_data"]["top_languages"]
                github_section += "## Programming Languages\n"
                for lang, bytes_count in languages.items():
                    github_section += f"- {lang}\n"
            
            # Add personal projects (top 5)
            if github_data.get("insights_data", {}).get("personal_projects"):
                projects = github_data["insights_data"]["personal_projects"][:5]
                github_section += "\n## Top Projects\n"
                for project in projects:
                    github_section += f"- {project.get('name', 'Unnamed')}: {project.get('description', 'No description')}\n"
                    github_section += f"  Language: {project.get('language', 'Not specified')}\n"
            
            # Add contribution activity
            if github_data.get("insights_data", {}).get("contribution_activity"):
                activity = github_data["insights_data"]["contribution_activity"]
                github_section += f"\n## Activity\n"
                github_section += f"- Last 30 days: {activity.get('last_30_days', 0)} commits\n"
                github_section += f"- Last 90 days: {activity.get('last_90_days', 0)} commits\n"
        
        # Prepare LeetCode data section if available
        leetcode_section = ""
        if leetcode_data:
            leetcode_section = """
# LEETCODE PROFILE DATA:
"""
            # Add problem solving stats
            if leetcode_data.get("profile_data", {}).get("userProblemsSolved", {}).get("matchedUser", {}).get("submitStatsGlobal", {}).get("acSubmissionNum"):
                stats = leetcode_data["profile_data"]["userProblemsSolved"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
                leetcode_section += "## Problem Solving Stats\n"
                for stat in stats:
                    if stat.get("difficulty") and stat.get("count"):
                        leetcode_section += f"- {stat['difficulty']}: {stat['count']} problems solved\n"
            
            # Add top skills (from tag problem counts)
            if leetcode_data.get("profile_data", {}).get("skillStats", {}).get("matchedUser", {}).get("tagProblemCounts"):
                tag_counts = leetcode_data["profile_data"]["skillStats"]["matchedUser"]["tagProblemCounts"]
                
                # Add fundamental skills
                if tag_counts.get("fundamental"):
                    leetcode_section += "\n## Fundamental Skills\n"
                    for skill in tag_counts["fundamental"][:5]:  # Top 5 fundamental skills
                        leetcode_section += f"- {skill.get('tagName')}: {skill.get('problemsSolved')} problems\n"
                
                # Add intermediate skills
                if tag_counts.get("intermediate"):
                    leetcode_section += "\n## Intermediate Skills\n"
                    for skill in tag_counts["intermediate"][:5]:  # Top 5 intermediate skills
                        leetcode_section += f"- {skill.get('tagName')}: {skill.get('problemsSolved')} problems\n"
                
                # Add advanced skills
                if tag_counts.get("advanced"):
                    leetcode_section += "\n## Advanced Skills\n"
                    for skill in tag_counts["advanced"][:5]:  # Top 5 advanced skills
                        leetcode_section += f"- {skill.get('tagName')}: {skill.get('problemsSolved')} problems\n"
            
            # Add programming languages used
            if leetcode_data.get("profile_data", {}).get("languageStats", {}).get("matchedUser", {}).get("languageProblemCount"):
                languages = leetcode_data["profile_data"]["languageStats"]["matchedUser"]["languageProblemCount"]
                leetcode_section += "\n## Programming Languages Used\n"
                for lang in languages:
                    leetcode_section += f"- {lang.get('languageName')}: {lang.get('problemsSolved')} problems\n"

        # Build the complete prompt using the centralized template
        return JOB_MATCHING_ANALYSIS_PROMPT.format(
            resume_content=resume_content,
            job_description_content=job_description_content,
            github_section=github_section,
            leetcode_section=leetcode_section
        )

# Function to get a single match between resume and job description
async def get_match(
    candidate_id: str, 
    job_description_id: str, 
    resume_content: str, 
    job_description_content: str,
    github_data: Optional[Dict[str, Any]] = None,
    leetcode_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get a match analysis between a specific resume and job description.
    
    Args:
        candidate_id: ID of the candidate document
        job_description_id: ID of the job description document
        resume_content: Content extracted from the resume
        job_description_content: Content extracted from the job description
        github_data: Optional GitHub profile data for enhanced matching
        leetcode_data: Optional LeetCode profile data for enhanced matching
        
    Returns:
        Complete match analysis
    """
    matcher = ResumeJobMatcher()
    return await matcher.generate_match_analysis(
        candidate_id, job_description_id, resume_content, job_description_content, github_data, leetcode_data
    )

# Function to get matches for a single resume against multiple job descriptions
async def get_matches_for_resume(
    candidate_id: str, 
    resume_content: str, 
    job_descriptions: List[Dict[str, Any]],
    github_data: Optional[Dict[str, Any]] = None,
    leetcode_data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Get match analyses between a resume and multiple job descriptions.
    
    Args:
        candidate_id: ID of the candidate document
        resume_content: Content extracted from the resume
        job_descriptions: List of job description objects with id and content
        github_data: Optional GitHub profile data for enhanced matching
        leetcode_data: Optional LeetCode profile data for enhanced matching
        
    Returns:
        List of match analyses
    """
    matcher = ResumeJobMatcher()
    results = []
    
    for jd in job_descriptions:
        match_result = await matcher.generate_match_analysis(
            candidate_id, 
            jd["id"], 
            resume_content, 
            jd["content"],
            github_data,
            leetcode_data
        )
        results.append(match_result)
    
    return results

# Function to get matches for a single job description against multiple resumes
async def get_matches_for_job(
    job_description_id: str, 
    job_description_content: str,
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Get match analyses between a job description and multiple resumes.
    
    Args:
        job_description_id: ID of the job description document
        job_description_content: Content extracted from the job description
        candidates: List of candidate objects with id, resume content, and optional GitHub/LeetCode data
        
    Returns:
        List of match analyses
    """
    matcher = ResumeJobMatcher()
    results = []
    
    for candidate in candidates:
        match_result = await matcher.generate_match_analysis(
            candidate["id"], 
            job_description_id, 
            candidate["content"], 
            job_description_content,
            candidate.get("github_data"),
            candidate.get("leetcode_data")
        )
        results.append(match_result)
    
    return results
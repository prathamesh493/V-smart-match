import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.config import GEMINI_API_KEY
import google.generativeai as genai

# Initialize Gemini with your API key
genai.configure(api_key=GEMINI_API_KEY)

class ResumeJobMatcher:
    """
    Service for matching resumes to job descriptions using Gemini's AI capabilities.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-pro-exp-03-25"):
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
        job_description_content: str
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive match analysis between a resume and job description.
        
        Args:
            candidate_id: The ID of the candidate document
            job_description_id: The ID of the job description document
            resume_content: The extracted content from the resume
            job_description_content: The extracted content from the job description
            
        Returns:
            A dictionary containing the complete match analysis
        """
        start_time = time.time()
        
        # Generate a unique ID for this match
        match_id = f"match_{uuid.uuid4().hex}"
        
        # Get the analysis from Gemini
        analysis_result = await self._analyze_match(resume_content, job_description_content)
        
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
                "completionTokens": analysis_result.get("completionTokens", 0)
            }
        }
        
        return match_result
        
    async def _analyze_match(self, resume_content: str, job_description_content: str) -> Dict[str, Any]:
        """
        Use Gemini to analyze the match between resume and job description.
        
        Args:
            resume_content: The text content of the resume
            job_description_content: The text content of the job description
            
        Returns:
            A dictionary containing the analysis results
        """
        # Construct the prompt for Gemini
        prompt = self._build_analysis_prompt(resume_content, job_description_content)
        
        # Send the prompt to Gemini
        try:
            response = await self.model.generate_content_async(prompt)
            
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
                if hasattr(response, 'usage'):
                    analysis_result["promptTokens"] = response.usage.prompt_tokens
                    analysis_result["completionTokens"] = response.usage.completion_tokens
                
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
    
    def _build_analysis_prompt(self, resume_content: str, job_description_content: str) -> str:
        """
        Build a detailed prompt for Gemini to analyze the match.
        
        Args:
            resume_content: The text content of the resume
            job_description_content: The text content of the job description
            
        Returns:
            A string containing the prompt for Gemini
        """
        return f"""
You are an expert AI system for matching job candidates to job descriptions. You need to analyze the resume and job description provided below and generate a comprehensive match analysis with numerical scores and explanations.

# RESUME CONTENT:
{resume_content}

# JOB DESCRIPTION:
{job_description_content}

# YOUR TASK:
Analyze how well the candidate's resume matches the job description. Provide a structured analysis using the following format:

1. Calculate an overall match score (0-100)
2. Calculate category-specific scores
3. Identify strengths and weaknesses
4. Provide recommendations for the recruiter

Return your analysis as a JSON object with the following structure:

```
{{
  "overallScore": <number 0-100>,
  "categoryScores": {{
    "skillsMatch": {{
      "score": <number 0-100>,
      "confidence": <number 0-100>,
      "keyMatches": [
        {{ "skill": <string>, "relevance": <number 0-100> }}
      ],
      "missingCriticalSkills": [
        {{ "skill": <string>, "importance": <number 0-100> }}
      ]
    }},
    "experienceMatch": {{
      "score": <number 0-100>,
      "confidence": <number 0-100>,
      "yearsExperienceMatch": <number 0-100>,
      "domainExperienceMatch": <number 0-100>,
      "roleAlignmentMatch": <number 0-100>
    }},
    "educationMatch": {{
      "score": <number 0-100>,
      "confidence": <number 0-100>,
      "degreeMatch": <number 0-100>,
      "fieldMatch": <number 0-100>,
      "certificationsMatch": <number 0-100>
    }},
    "softSkillsMatch": {{
      "score": <number 0-100>,
      "confidence": <number 0-100>,
      "keyMatches": [
        {{ "skill": <string>, "relevance": <number 0-100> }}
      ]
    }},
    "culturalFitMatch": {{
      "score": <number 0-100>,
      "confidence": <number 0-100>,
      "valueAlignmentScore": <number 0-100>,
      "workStyleMatch": <number 0-100>
    }}
  }},
  "analysis": {{
    "summary": <string>,
    "strengths": [<string>, <string>, ...],
    "weaknesses": [<string>, <string>, ...],
    "recommendations": [<string>, <string>, ...]
  }}
}}
```

Your analysis must be data-driven and objective. Back up all scores with evidence from the resume and job description. Provide specific examples of matches and mismatches.

Return ONLY the JSON object with no additional text or explanation.
"""

# Function to get a single match between resume and job description
async def get_match(candidate_id: str, job_description_id: str, 
                    resume_content: str, job_description_content: str) -> Dict[str, Any]:
    """
    Get a match analysis between a specific resume and job description.
    
    Args:
        candidate_id: ID of the candidate document
        job_description_id: ID of the job description document
        resume_content: Content extracted from the resume
        job_description_content: Content extracted from the job description
        
    Returns:
        Complete match analysis
    """
    matcher = ResumeJobMatcher()
    return await matcher.generate_match_analysis(
        candidate_id, job_description_id, resume_content, job_description_content
    )

# Function to get matches for a single resume against multiple job descriptions
async def get_matches_for_resume(candidate_id: str, resume_content: str, 
                                job_descriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get match analyses between a resume and multiple job descriptions.
    
    Args:
        candidate_id: ID of the candidate document
        resume_content: Content extracted from the resume
        job_descriptions: List of job description objects with id and content
        
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
            jd["content"]
        )
        results.append(match_result)
    
    return results

# Function to get matches for a single job description against multiple resumes
async def get_matches_for_job(job_description_id: str, job_description_content: str,
                             candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get match analyses between a job description and multiple resumes.
    
    Args:
        job_description_id: ID of the job description document
        job_description_content: Content extracted from the job description
        candidates: List of candidate objects with id and resume content
        
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
            job_description_content
        )
        results.append(match_result)
    
    return results
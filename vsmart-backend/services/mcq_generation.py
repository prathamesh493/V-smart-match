"""
MCQ Generation Service using Gemini AI.
"""

import json
import hashlib
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio

import google.generativeai as genai
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from prompts.mcq.generation import get_mcq_prompt

# Configure logging
logger = logging.getLogger(__name__)

# Configure the Gemini client
genai.configure(api_key=GEMINI_API_KEY)

# Simple in-memory cache for questions (in production, use Redis or database)
_question_cache = {}
_cache_expiry = {}

class MCQGenerationService:
    """Service for generating MCQs using Gemini AI."""
    
    def __init__(self):
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
    async def generate_mcqs(
        self,
        skill: str,
        difficulty: str = "intermediate",
        question_type: str = "technical",
        num_questions: int = 5,
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Generate MCQs for specified parameters.
        
        Args:
            skill: The skill/topic to generate questions for
            difficulty: beginner, intermediate, or advanced
            question_type: technical, soft_skills, scenario_based, or code_based
            num_questions: Number of questions to generate (1-20)
            language: Language for questions (English, Spanish, etc.)
            
        Returns:
            Dictionary containing generated questions and metadata
        """
        # Validate inputs
        if not skill:
            raise ValueError("Skill parameter is required")
        
        if difficulty not in ["beginner", "intermediate", "advanced"]:
            raise ValueError("Difficulty must be beginner, intermediate, or advanced")
            
        if question_type not in ["technical", "soft_skills", "scenario_based", "code_based"]:
            raise ValueError("Invalid question type")
            
        if not (1 <= num_questions <= 20):
            raise ValueError("Number of questions must be between 1 and 20")
        
        # Check cache first
        cache_key = self._generate_cache_key(skill, difficulty, question_type, num_questions, language)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"Retrieved MCQs from cache for {skill}")
            return cached_result
        
        try:
            # Generate prompt
            prompt = get_mcq_prompt(
                question_type=question_type,
                skill=skill,
                difficulty=difficulty,
                num_questions=num_questions,
                language=language
            )
            
            logger.info(f"Generating {num_questions} {question_type} questions for {skill} ({difficulty})")
            
            # Call Gemini API
            response = await self.model.generate_content_async(prompt)
            
            # Parse response
            json_string = response.text.strip()
            if json_string.startswith("```json"):
                json_string = json_string[7:-3].strip()
            elif json_string.startswith("```"):
                json_string = json_string[3:-3].strip()
                
            parsed_response = json.loads(json_string)
            
            # Validate and enhance the response
            result = self._validate_and_enhance_questions(
                parsed_response,
                skill,
                difficulty,
                question_type,
                language
            )
            
            # Cache the result
            self._cache_result(cache_key, result)
            
            logger.info(f"Successfully generated {len(result['questions'])} questions")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response.text}")
            raise ValueError("Failed to parse AI response")
        except Exception as e:
            logger.error(f"Error generating MCQs: {e}")
            raise
    
    def _validate_and_enhance_questions(
        self,
        parsed_response: Dict[str, Any],
        skill: str,
        difficulty: str,
        question_type: str,
        language: str
    ) -> Dict[str, Any]:
        """Validate and enhance the generated questions."""
        
        if "questions" not in parsed_response:
            raise ValueError("Invalid response format: missing 'questions' field")
        
        questions = parsed_response["questions"]
        validated_questions = []
        
        for i, q in enumerate(questions):
            # Validate required fields
            required_fields = ["question", "options", "correct_answer"]
            for field in required_fields:
                if field not in q:
                    logger.warning(f"Question {i} missing required field: {field}")
                    continue
            
            # Validate options
            options = q.get("options", {})
            if not all(opt in options for opt in ["A", "B", "C", "D"]):
                logger.warning(f"Question {i} missing required options A, B, C, D")
                continue
            
            # Validate correct answer
            correct_answer = q.get("correct_answer")
            if correct_answer not in ["A", "B", "C", "D"]:
                logger.warning(f"Question {i} has invalid correct answer: {correct_answer}")
                continue
            
            # Generate unique ID if not present
            if "id" not in q:
                q["id"] = self._generate_question_id(q["question"], skill)
            
            # Ensure metadata fields
            q["skill"] = skill
            q["difficulty"] = difficulty
            q["type"] = question_type
            q["language"] = language
            q["generated_at"] = datetime.now().isoformat()
            
            # Add default tags if missing
            if "tags" not in q:
                q["tags"] = [skill.lower(), difficulty, question_type]
            
            validated_questions.append(q)
        
        return {
            "questions": validated_questions,
            "metadata": {
                "skill": skill,
                "difficulty": difficulty,
                "question_type": question_type,
                "language": language,
                "total_questions": len(validated_questions),
                "generated_at": datetime.now().isoformat(),
                "model_used": GEMINI_MODEL
            }
        }
    
    def _generate_cache_key(self, skill: str, difficulty: str, question_type: str, num_questions: int, language: str) -> str:
        """Generate a cache key for the given parameters."""
        key_string = f"{skill}_{difficulty}_{question_type}_{num_questions}_{language}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache if still valid."""
        if cache_key in _question_cache:
            expiry_time = _cache_expiry.get(cache_key)
            if expiry_time and datetime.now() < expiry_time:
                return _question_cache[cache_key]
            else:
                # Remove expired entry
                del _question_cache[cache_key]
                if cache_key in _cache_expiry:
                    del _cache_expiry[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache the result with expiry time."""
        _question_cache[cache_key] = result
        _cache_expiry[cache_key] = datetime.now() + timedelta(hours=24)  # Cache for 24 hours
    
    def _generate_question_id(self, question: str, skill: str) -> str:
        """Generate a unique ID for a question."""
        id_string = f"{question}_{skill}_{datetime.now().timestamp()}"
        return hashlib.sha256(id_string.encode()).hexdigest()[:16]
    
    async def validate_question_quality(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the quality of a generated question.
        
        Returns:
            Dictionary with validation results and suggestions
        """
        validation_result = {
            "is_valid": True,
            "issues": [],
            "suggestions": []
        }
        
        # Check question length
        question_text = question.get("question", "")
        if len(question_text) < 10:
            validation_result["issues"].append("Question too short")
            validation_result["is_valid"] = False
        elif len(question_text) > 500:
            validation_result["issues"].append("Question too long")
            validation_result["suggestions"].append("Consider shortening the question")
        
        # Check options diversity
        options = question.get("options", {})
        option_lengths = [len(opt) for opt in options.values()]
        if max(option_lengths) - min(option_lengths) > 100:
            validation_result["suggestions"].append("Options vary significantly in length")
        
        # Check for obvious answers
        correct_answer = question.get("correct_answer")
        correct_option = options.get(correct_answer, "")
        if "all of the above" in correct_option.lower() or "none of the above" in correct_option.lower():
            validation_result["suggestions"].append("Avoid 'all/none of the above' options when possible")
        
        return validation_result
    
    async def detect_duplicate_questions(self, new_questions: List[Dict[str, Any]], existing_questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect potential duplicate questions.
        
        Returns:
            List of potential duplicates with similarity scores
        """
        duplicates = []
        
        for new_q in new_questions:
            new_text = new_q.get("question", "").lower()
            for existing_q in existing_questions:
                existing_text = existing_q.get("question", "").lower()
                
                # Simple similarity check (in production, use more sophisticated NLP)
                similarity = self._calculate_text_similarity(new_text, existing_text)
                if similarity > 0.8:  # 80% similarity threshold
                    duplicates.append({
                        "new_question_id": new_q.get("id"),
                        "existing_question_id": existing_q.get("id"),
                        "similarity_score": similarity
                    })
        
        return duplicates
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (Jaccard similarity)."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_supported_skills(self) -> List[str]:
        """Get list of supported skills for MCQ generation."""
        return [
            # Technical Skills
            "Python", "JavaScript", "Java", "C++", "React", "Node.js", "Django", "Flask",
            "SQL", "MongoDB", "PostgreSQL", "MySQL", "Docker", "Kubernetes", "AWS", "Azure",
            "Machine Learning", "Data Science", "DevOps", "System Design", "Algorithms",
            "Data Structures", "Frontend Development", "Backend Development", "Full Stack",
            
            # Soft Skills
            "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management",
            "Project Management", "Critical Thinking", "Adaptability", "Conflict Resolution",
            "Presentation Skills", "Negotiation", "Customer Service", "Sales", "Marketing"
        ]

# Global service instance
mcq_service = MCQGenerationService()
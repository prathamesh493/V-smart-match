"""
Simplified tests for MCQ generation service without dependencies.
"""

import pytest
import json
from unittest.mock import patch, AsyncMock

# Mock the entire services module to avoid import issues
import sys
from unittest.mock import MagicMock

# Mock problematic imports
sys.modules['services.embedding'] = MagicMock()
sys.modules['services.pinecone_service'] = MagicMock()

from services.mcq_generation import MCQGenerationService
from prompts.mcq.generation import get_mcq_prompt

class TestMCQGenerationService:
    """Test MCQ generation service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = MCQGenerationService()
    
    @pytest.mark.asyncio
    async def test_input_validation(self):
        """Test input validation for MCQ generation."""
        
        # Test invalid difficulty
        with pytest.raises(ValueError, match="Difficulty must be"):
            await self.service.generate_mcqs(
                skill="Python",
                difficulty="invalid"
            )
        
        # Test invalid question type
        with pytest.raises(ValueError, match="Invalid question type"):
            await self.service.generate_mcqs(
                skill="Python",
                question_type="invalid"
            )
        
        # Test invalid number of questions
        with pytest.raises(ValueError, match="Number of questions must be"):
            await self.service.generate_mcqs(
                skill="Python",
                num_questions=25
            )
        
        # Test empty skill
        with pytest.raises(ValueError, match="Skill parameter is required"):
            await self.service.generate_mcqs(skill="")
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = self.service._generate_cache_key("Python", "intermediate", "technical", 5, "English")
        key2 = self.service._generate_cache_key("Python", "intermediate", "technical", 5, "English")
        key3 = self.service._generate_cache_key("Java", "intermediate", "technical", 5, "English")
        
        assert key1 == key2  # Same parameters should generate same key
        assert key1 != key3  # Different skill should generate different key
        assert len(key1) == 32  # MD5 hash should be 32 characters
    
    def test_question_id_generation(self):
        """Test question ID generation."""
        question1 = "What is Python?"
        question2 = "What is Java?"
        
        id1 = self.service._generate_question_id(question1, "Python")
        id2 = self.service._generate_question_id(question1, "Python")
        id3 = self.service._generate_question_id(question2, "Python")
        
        assert len(id1) == 16  # Should be 16 characters
        assert id1 != id2  # Should be unique due to timestamp
        assert id1 != id3  # Different questions should have different IDs
    
    def test_text_similarity_calculation(self):
        """Test text similarity calculation."""
        text1 = "what is python programming language"
        text2 = "what is python programming language"
        text3 = "what is java programming language"
        text4 = "completely different text here"
        
        # Identical texts should have similarity 1.0
        similarity1 = self.service._calculate_text_similarity(text1, text2)
        assert similarity1 == 1.0
        
        # Similar texts should have high similarity
        similarity2 = self.service._calculate_text_similarity(text1, text3)
        assert 0.5 < similarity2 < 1.0
        
        # Different texts should have low similarity
        similarity3 = self.service._calculate_text_similarity(text1, text4)
        assert similarity3 < 0.5
    
    @pytest.mark.asyncio
    async def test_question_validation(self):
        """Test question quality validation."""
        # Valid question
        valid_question = {
            "question": "What is the output of print('Hello World') in Python?",
            "options": {
                "A": "Hello World",
                "B": "print('Hello World')",
                "C": "SyntaxError",
                "D": "None"
            },
            "correct_answer": "A"
        }
        
        result = await self.service.validate_question_quality(valid_question)
        assert result["is_valid"] is True
        
        # Invalid question (too short)
        invalid_question = {
            "question": "What?",
            "options": {
                "A": "A",
                "B": "B",
                "C": "C",
                "D": "D"
            },
            "correct_answer": "A"
        }
        
        result = await self.service.validate_question_quality(invalid_question)
        assert result["is_valid"] is False
        assert "Question too short" in result["issues"]
    
    @pytest.mark.asyncio
    async def test_duplicate_detection(self):
        """Test duplicate question detection."""
        question1 = {
            "id": "1",
            "question": "What is Python used for?"
        }
        question2 = {
            "id": "2", 
            "question": "What is Python programming used for?"
        }
        question3 = {
            "id": "3",
            "question": "What is Java used for?"
        }
        
        new_questions = [question1]
        existing_questions = [question2, question3]
        
        duplicates = await self.service.detect_duplicate_questions(new_questions, existing_questions)
        
        # Should detect similarity between question1 and question2
        assert len(duplicates) > 0
        assert duplicates[0]["new_question_id"] == "1"
        assert duplicates[0]["existing_question_id"] == "2"
        assert duplicates[0]["similarity_score"] > 0.8
    
    def test_supported_skills(self):
        """Test supported skills retrieval."""
        skills = self.service.get_supported_skills()
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        assert "Python" in skills
        assert "JavaScript" in skills
        assert "Communication" in skills
        assert "Leadership" in skills
    
    def test_validate_and_enhance_questions(self):
        """Test question validation and enhancement."""
        parsed_response = {
            "questions": [
                {
                    "question": "What is Python?",
                    "options": {
                        "A": "A programming language",
                        "B": "A snake",
                        "C": "A tool",
                        "D": "A framework"
                    },
                    "correct_answer": "A",
                    "explanation": "Python is a programming language"
                }
            ]
        }
        
        result = self.service._validate_and_enhance_questions(
            parsed_response, "Python", "beginner", "technical", "English"
        )
        
        assert "questions" in result
        assert "metadata" in result
        assert len(result["questions"]) == 1
        
        question = result["questions"][0]
        assert question["skill"] == "Python"
        assert question["difficulty"] == "beginner"
        assert question["type"] == "technical"
        assert question["language"] == "English"
        assert "id" in question
        assert "generated_at" in question


class TestMCQPrompts:
    """Test MCQ prompt generation."""
    
    def test_get_mcq_prompt_technical(self):
        """Test technical MCQ prompt generation."""
        prompt = get_mcq_prompt(
            question_type="technical",
            skill="Python",
            difficulty="intermediate", 
            num_questions=5,
            language="English"
        )
        
        assert "technical" in prompt.lower()
        assert "python" in prompt.lower()
        assert "intermediate" in prompt.lower()
        assert "5" in prompt
    
    def test_get_mcq_prompt_soft_skills(self):
        """Test soft skills MCQ prompt generation."""
        prompt = get_mcq_prompt(
            question_type="soft_skills",
            skill="Leadership",
            difficulty="advanced",
            num_questions=3,
            language="English"
        )
        
        assert "soft skills" in prompt.lower() or "hr professional" in prompt.lower()
        assert "leadership" in prompt.lower()
        assert "advanced" in prompt.lower()
        assert "3" in prompt
    
    def test_get_mcq_prompt_scenario_based(self):
        """Test scenario-based MCQ prompt generation."""
        prompt = get_mcq_prompt(
            question_type="scenario_based",
            skill="Project Management",
            difficulty="intermediate",
            num_questions=2,
            language="English"
        )
        
        assert "scenario" in prompt.lower()
        assert "project management" in prompt.lower()
        assert "intermediate" in prompt.lower()
        assert "2" in prompt
    
    def test_get_mcq_prompt_code_based(self):
        """Test code-based MCQ prompt generation."""
        prompt = get_mcq_prompt(
            question_type="code_based",
            skill="JavaScript",
            difficulty="beginner",
            num_questions=1,
            language="English"
        )
        
        assert "code" in prompt.lower()
        assert "javascript" in prompt.lower()
        assert "beginner" in prompt.lower()
        assert "1" in prompt
        assert "```" in prompt  # Code block formatting
    
    def test_get_mcq_prompt_default(self):
        """Test default MCQ prompt generation."""
        prompt = get_mcq_prompt(
            question_type="unknown",
            skill="General",
            difficulty="intermediate",
            num_questions=1,
            language="English"
        )
        
        assert "multiple-choice" in prompt.lower()
        assert "general" in prompt.lower()
        assert "intermediate" in prompt.lower()

if __name__ == "__main__":
    pytest.main([__file__])
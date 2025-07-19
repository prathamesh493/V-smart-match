"""
Tests for MCQ generation service and API.
"""

import pytest
import json
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from services.mcq_generation import MCQGenerationService
from api.schemas.mcq import MCQGenerationRequest

client = TestClient(app)

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

class TestMCQAPI:
    """Test MCQ API endpoints."""
    
    def test_generate_mcqs_endpoint(self):
        """Test the MCQ generation endpoint."""
        # Mock the service to avoid actual API calls
        with patch('services.mcq_generation.mcq_service.generate_mcqs') as mock_generate:
            mock_generate.return_value = {
                "questions": [
                    {
                        "id": "test_id",
                        "question": "What is Python?",
                        "options": {
                            "A": "A programming language",
                            "B": "A snake",
                            "C": "A tool",
                            "D": "A framework"
                        },
                        "correct_answer": "A",
                        "explanation": "Python is a programming language",
                        "difficulty": "beginner",
                        "skill": "Python",
                        "type": "technical",
                        "language": "English",
                        "tags": ["python", "beginner", "technical"],
                        "generated_at": "2024-01-01T00:00:00"
                    }
                ],
                "metadata": {
                    "skill": "Python",
                    "difficulty": "beginner", 
                    "question_type": "technical",
                    "language": "English",
                    "total_questions": 1,
                    "generated_at": "2024-01-01T00:00:00",
                    "model_used": "gemini-2.5-flash-preview-04-17"
                }
            }
            
            response = client.post(
                "/api/mcq/generate",
                json={
                    "skill": "Python",
                    "difficulty": "beginner",
                    "question_type": "technical",
                    "num_questions": 1,
                    "language": "English"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "questions" in data
            assert "metadata" in data
            assert len(data["questions"]) == 1
            assert data["questions"][0]["skill"] == "Python"
    
    def test_generate_mcqs_validation_error(self):
        """Test validation error in MCQ generation."""
        response = client.post(
            "/api/mcq/generate",
            json={
                "skill": "Python",
                "difficulty": "invalid",  # Invalid difficulty
                "question_type": "technical",
                "num_questions": 1
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_supported_skills_endpoint(self):
        """Test the supported skills endpoint."""
        response = client.get("/api/mcq/supported-skills")
        
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert "total_skills" in data
        assert isinstance(data["skills"], list)
        assert len(data["skills"]) > 0
    
    def test_validate_mcq_endpoint(self):
        """Test the MCQ validation endpoint."""
        with patch('services.mcq_generation.mcq_service.validate_question_quality') as mock_validate:
            mock_validate.return_value = {
                "is_valid": True,
                "issues": [],
                "suggestions": []
            }
            
            response = client.post(
                "/api/mcq/validate",
                json={
                    "question": {
                        "id": "test_id",
                        "question": "What is Python?",
                        "options": {
                            "A": "A programming language",
                            "B": "A snake", 
                            "C": "A tool",
                            "D": "A framework"
                        },
                        "correct_answer": "A",
                        "difficulty": "beginner",
                        "skill": "Python",
                        "type": "technical"
                    }
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_valid"] is True
    
    def test_batch_generate_endpoint(self):
        """Test the batch MCQ generation endpoint."""
        with patch('services.mcq_generation.mcq_service.generate_mcqs') as mock_generate:
            mock_generate.return_value = {
                "questions": [{
                    "id": "test_id",
                    "question": "Test question?",
                    "options": {"A": "A", "B": "B", "C": "C", "D": "D"},
                    "correct_answer": "A",
                    "difficulty": "beginner",
                    "skill": "Python",
                    "type": "technical",
                    "language": "English",
                    "tags": ["python"],
                    "generated_at": "2024-01-01T00:00:00"
                }],
                "metadata": {
                    "skill": "Python",
                    "difficulty": "beginner",
                    "question_type": "technical", 
                    "language": "English",
                    "total_questions": 1,
                    "generated_at": "2024-01-01T00:00:00",
                    "model_used": "gemini-2.5-flash-preview-04-17"
                }
            }
            
            response = client.get(
                "/api/mcq/batch-generate?skills=Python,JavaScript&num_questions_per_skill=1"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2  # Two skills

if __name__ == "__main__":
    pytest.main([__file__])
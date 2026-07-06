"""
Schemas for MCQ generation API.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime

class MCQGenerationRequest(BaseModel):
    """Schema for MCQ generation request."""
    
    skill: str = Field(..., description="Skill or topic to generate questions for", min_length=1, max_length=100)
    difficulty: str = Field(default="intermediate", description="Difficulty level: beginner, intermediate, or advanced")
    question_type: str = Field(default="technical", description="Type of questions: technical, soft_skills, scenario_based, or code_based")
    num_questions: int = Field(default=5, description="Number of questions to generate", ge=1, le=20)
    language: str = Field(default="English", description="Language for questions", max_length=50)
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v not in ["beginner", "intermediate", "advanced"]:
            raise ValueError("Difficulty must be beginner, intermediate, or advanced")
        return v
    
    @validator('question_type')
    def validate_question_type(cls, v):
        if v not in ["technical", "soft_skills", "scenario_based", "code_based"]:
            raise ValueError("Question type must be technical, soft_skills, scenario_based, or code_based")
        return v

class MCQOption(BaseModel):
    """Schema for MCQ options."""
    A: str = Field(..., description="Option A text")
    B: str = Field(..., description="Option B text")
    C: str = Field(..., description="Option C text")
    D: str = Field(..., description="Option D text")

class MCQQuestion(BaseModel):
    """Schema for a single MCQ question."""
    
    id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., description="Question text")
    options: MCQOption = Field(..., description="Answer options")
    correct_answer: str = Field(..., description="Correct answer (A, B, C, or D)")
    explanation: Optional[str] = Field(None, description="Explanation for the correct answer")
    difficulty: str = Field(..., description="Difficulty level")
    skill: str = Field(..., description="Associated skill")
    type: str = Field(..., description="Question type")
    language: str = Field(default="English", description="Question language")
    tags: List[str] = Field(default_factory=list, description="Question tags")
    generated_at: Optional[str] = Field(None, description="Generation timestamp")
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v):
        if v not in ["A", "B", "C", "D"]:
            raise ValueError("Correct answer must be A, B, C, or D")
        return v

class MCQMetadata(BaseModel):
    """Schema for MCQ generation metadata."""
    
    skill: str = Field(..., description="Skill for which questions were generated")
    difficulty: str = Field(..., description="Difficulty level")
    question_type: str = Field(..., description="Type of questions generated")
    language: str = Field(..., description="Language of questions")
    total_questions: int = Field(..., description="Total number of questions generated")
    generated_at: str = Field(..., description="Generation timestamp")
    model_used: str = Field(..., description="AI model used for generation")

class MCQGenerationResponse(BaseModel):
    """Schema for MCQ generation response."""
    
    questions: List[MCQQuestion] = Field(..., description="Generated MCQ questions")
    metadata: MCQMetadata = Field(..., description="Generation metadata")

class MCQValidationRequest(BaseModel):
    """Schema for question validation request."""
    
    question: MCQQuestion = Field(..., description="Question to validate")

class MCQValidationResult(BaseModel):
    """Schema for question validation result."""
    
    is_valid: bool = Field(..., description="Whether the question is valid")
    issues: List[str] = Field(default_factory=list, description="Validation issues found")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")

class MCQDuplicateDetectionRequest(BaseModel):
    """Schema for duplicate detection request."""
    
    new_questions: List[MCQQuestion] = Field(..., description="New questions to check")
    existing_questions: List[MCQQuestion] = Field(..., description="Existing questions to compare against")

class MCQDuplicate(BaseModel):
    """Schema for duplicate question information."""
    
    new_question_id: str = Field(..., description="ID of the new question")
    existing_question_id: str = Field(..., description="ID of the existing similar question")
    similarity_score: float = Field(..., description="Similarity score (0-1)")

class MCQDuplicateDetectionResponse(BaseModel):
    """Schema for duplicate detection response."""
    
    duplicates: List[MCQDuplicate] = Field(default_factory=list, description="Found duplicates")
    total_duplicates: int = Field(default=0, description="Total number of duplicates found")

class SupportedSkillsResponse(BaseModel):
    """Schema for supported skills response."""
    
    skills: List[str] = Field(..., description="List of supported skills")
    total_skills: int = Field(..., description="Total number of supported skills")

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Specific error code")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")
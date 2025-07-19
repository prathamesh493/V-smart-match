"""
API routes for MCQ generation.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from api.schemas.mcq import (
    MCQGenerationRequest,
    MCQGenerationResponse,
    MCQValidationRequest,
    MCQValidationResult,
    MCQDuplicateDetectionRequest,
    MCQDuplicateDetectionResponse,
    SupportedSkillsResponse,
    ErrorResponse,
    MCQQuestion
)
from services.mcq_generation import mcq_service

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/mcq/generate",
    response_model=MCQGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Generate MCQ questions",
    description="Generate multiple-choice questions for specified skills and parameters"
)
async def generate_mcqs(request: MCQGenerationRequest):
    """
    Generate MCQ questions based on specified parameters.
    
    - **skill**: The skill or topic to generate questions for
    - **difficulty**: Difficulty level (beginner, intermediate, advanced)
    - **question_type**: Type of questions (technical, soft_skills, scenario_based, code_based)
    - **num_questions**: Number of questions to generate (1-20)
    - **language**: Language for questions
    """
    try:
        logger.info(f"Generating MCQs for skill: {request.skill}, difficulty: {request.difficulty}")
        
        result = await mcq_service.generate_mcqs(
            skill=request.skill,
            difficulty=request.difficulty,
            question_type=request.question_type,
            num_questions=request.num_questions,
            language=request.language
        )
        
        return MCQGenerationResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error in MCQ generation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating MCQs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating questions")

@router.post(
    "/mcq/validate",
    response_model=MCQValidationResult,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Validate MCQ question quality",
    description="Validate the quality of an MCQ question and get improvement suggestions"
)
async def validate_mcq_question(request: MCQValidationRequest):
    """
    Validate the quality of an MCQ question.
    
    Returns validation results and suggestions for improvement.
    """
    try:
        result = await mcq_service.validate_question_quality(request.question.dict())
        return MCQValidationResult(**result)
        
    except Exception as e:
        logger.error(f"Error validating MCQ question: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while validating question")

@router.post(
    "/mcq/detect-duplicates",
    response_model=MCQDuplicateDetectionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Detect duplicate questions",
    description="Detect potential duplicate questions between new and existing question sets"
)
async def detect_duplicate_mcqs(request: MCQDuplicateDetectionRequest):
    """
    Detect potential duplicate questions.
    
    Compares new questions against existing questions and returns similarity matches.
    """
    try:
        new_questions = [q.dict() for q in request.new_questions]
        existing_questions = [q.dict() for q in request.existing_questions]
        
        duplicates = await mcq_service.detect_duplicate_questions(new_questions, existing_questions)
        
        return MCQDuplicateDetectionResponse(
            duplicates=duplicates,
            total_duplicates=len(duplicates)
        )
        
    except Exception as e:
        logger.error(f"Error detecting duplicate MCQs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while detecting duplicates")

@router.get(
    "/mcq/supported-skills",
    response_model=SupportedSkillsResponse,
    summary="Get supported skills",
    description="Get list of skills supported for MCQ generation"
)
async def get_supported_skills():
    """
    Get list of supported skills for MCQ generation.
    
    Returns both technical and soft skills that can be used for question generation.
    """
    try:
        skills = mcq_service.get_supported_skills()
        return SupportedSkillsResponse(
            skills=skills,
            total_skills=len(skills)
        )
        
    except Exception as e:
        logger.error(f"Error getting supported skills: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching supported skills")

@router.get(
    "/mcq/batch-generate",
    response_model=List[MCQGenerationResponse],
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Generate MCQs for multiple skills",
    description="Generate questions for multiple skills in a single request"
)
async def batch_generate_mcqs(
    skills: str,  # Comma-separated skills
    difficulty: str = "intermediate",
    question_type: str = "technical",
    num_questions_per_skill: int = 3,
    language: str = "English"
):
    """
    Generate MCQs for multiple skills in a batch.
    
    - **skills**: Comma-separated list of skills
    - **difficulty**: Difficulty level for all questions
    - **question_type**: Type of questions for all skills
    - **num_questions_per_skill**: Number of questions per skill
    - **language**: Language for all questions
    """
    try:
        skill_list = [skill.strip() for skill in skills.split(",")]
        
        if len(skill_list) > 10:  # Limit to prevent abuse
            raise HTTPException(status_code=400, detail="Maximum 10 skills allowed per batch")
        
        results = []
        for skill in skill_list:
            if skill:  # Skip empty skills
                result = await mcq_service.generate_mcqs(
                    skill=skill,
                    difficulty=difficulty,
                    question_type=question_type,
                    num_questions=num_questions_per_skill,
                    language=language
                )
                results.append(MCQGenerationResponse(**result))
        
        return results
        
    except ValueError as e:
        logger.error(f"Validation error in batch MCQ generation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in batch MCQ generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating batch questions")
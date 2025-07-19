"""
Chatbot service for managing conversation flow and question delivery.
Integrates with existing MCQ generation service and session management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import uuid

from api.schemas.chatbot import (
    ConversationStatus, MessageType, Question, QuestionType,
    SessionInitResponse, AnswerSubmissionResponse, SessionStatusResponse,
    MCQOption
)
from services.session_manager import session_manager
from services.mcq_generation import mcq_service

logger = logging.getLogger(__name__)


class ChatbotService:
    """Main service for chatbot conversation management"""
    
    def __init__(self):
        self.session_manager = session_manager
        self.mcq_service = mcq_service
    
    async def initialize_session(
        self,
        user_id: str,
        skills: List[str],
        difficulty: str = "intermediate",
        num_questions: int = 10,
        session_timeout_minutes: int = 30,
        question_timeout_seconds: int = 120,
        language: str = "English"
    ) -> SessionInitResponse:
        """
        Initialize a new chatbot session with the first question.
        
        Args:
            user_id: User identifier
            skills: List of skills to assess
            difficulty: Question difficulty level
            num_questions: Total number of questions
            session_timeout_minutes: Session timeout in minutes
            question_timeout_seconds: Per-question timeout in seconds
            language: Language for questions
            
        Returns:
            SessionInitResponse with session details and first question
        """
        try:
            # Create session
            session_id = await self.session_manager.create_session(
                user_id=user_id,
                skills=skills,
                difficulty=difficulty,
                num_questions=num_questions,
                session_timeout_minutes=session_timeout_minutes,
                question_timeout_seconds=question_timeout_seconds,
                language=language
            )
            
            # Add welcome message
            await self.session_manager.add_message(
                session_id=session_id,
                message_type=MessageType.SYSTEM,
                content=f"Welcome to your skill assessment! You'll be asked {num_questions} questions covering: {', '.join(skills)}",
                metadata={"skills": skills, "difficulty": difficulty}
            )
            
            # Generate first question
            first_question = await self._generate_next_question(session_id, skills[0])
            
            session = await self.session_manager.get_session(session_id)
            if not session:
                raise Exception("Failed to retrieve session after creation")
            
            return SessionInitResponse(
                session_id=session_id,
                status=ConversationStatus.ACTIVE,
                total_questions=num_questions,
                current_question_index=0,
                skills=skills,
                expires_at=session["expires_at"],
                first_question=first_question
            )
            
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            raise Exception(f"Failed to initialize session: {str(e)}")
    
    async def submit_answer(
        self,
        user_id: str,
        session_id: str,
        question_id: str,
        answer: str,
        time_taken_seconds: Optional[int] = None
    ) -> AnswerSubmissionResponse:
        """
        Submit an answer and get the next question or session completion.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            question_id: Question identifier
            answer: User's answer
            time_taken_seconds: Time taken to answer
            
        Returns:
            AnswerSubmissionResponse with feedback and next question
        """
        try:
            # Verify session belongs to user
            session = await self.session_manager.get_session(session_id)
            if not session or session["user_id"] != user_id:
                raise Exception("Session not found or access denied")
            
            if session["status"] != ConversationStatus.ACTIVE:
                raise Exception(f"Session is not active: {session['status']}")
            
            # Find the question
            question_data = None
            for q in session["questions"]:
                if q["id"] == question_id:
                    question_data = q
                    break
            
            if not question_data:
                raise Exception("Question not found in session")
            
            # Check answer
            is_correct = self._check_answer(question_data, answer)
            correct_answer = question_data.get("correct_answer")
            
            # Record the answer
            await self.session_manager.record_answer(
                session_id=session_id,
                question_id=question_id,
                answer=answer,
                is_correct=is_correct,
                time_taken_seconds=time_taken_seconds
            )
            
            # Add answer to conversation history
            await self.session_manager.add_message(
                session_id=session_id,
                message_type=MessageType.USER_ANSWER,
                content=answer,
                metadata={
                    "question_id": question_id,
                    "is_correct": is_correct,
                    "time_taken_seconds": time_taken_seconds
                }
            )
            
            # Get updated session
            session = await self.session_manager.get_session(session_id)
            current_index = session["current_question_index"]
            total_questions = session["num_questions"]
            
            # Check if session is complete
            session_completed = current_index >= total_questions
            next_question = None
            
            if not session_completed:
                # Generate next question
                skill_index = current_index % len(session["skills"])
                next_skill = session["skills"][skill_index]
                next_question = await self._generate_next_question(session_id, next_skill)
            else:
                # Complete the session
                await self.session_manager.complete_session(session_id)
            
            # Generate explanation/feedback
            explanation = self._generate_explanation(question_data, is_correct)
            
            # Add feedback to conversation
            feedback_content = f"{'Correct!' if is_correct else 'Incorrect.'}"
            if explanation:
                feedback_content += f" {explanation}"
            
            await self.session_manager.add_message(
                session_id=session_id,
                message_type=MessageType.FEEDBACK,
                content=feedback_content,
                metadata={"question_id": question_id, "explanation": explanation}
            )
            
            return AnswerSubmissionResponse(
                is_correct=is_correct,
                correct_answer=correct_answer,
                explanation=explanation,
                points_earned=1 if is_correct else 0,
                total_score=session["score"],
                next_question=next_question,
                session_completed=session_completed
            )
            
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            raise Exception(f"Failed to submit answer: {str(e)}")
    
    async def get_session_status(self, user_id: str, session_id: str) -> SessionStatusResponse:
        """Get current session status"""
        try:
            session = await self.session_manager.get_session(session_id)
            if not session or session["user_id"] != user_id:
                raise Exception("Session not found or access denied")
            
            # Calculate time remaining
            time_remaining = None
            if session["status"] == ConversationStatus.ACTIVE:
                expires_at = session["expires_at"]
                remaining_seconds = (expires_at - datetime.now()).total_seconds()
                time_remaining = max(0, int(remaining_seconds))
            
            return SessionStatusResponse(
                session_id=session_id,
                status=session["status"],
                current_question_index=session["current_question_index"],
                total_questions=session["num_questions"],
                score=session["score"],
                max_score=session["max_score"],
                time_remaining_seconds=time_remaining,
                skills_assessed=session["skills"],
                started_at=session["started_at"],
                expires_at=session["expires_at"]
            )
            
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            raise Exception(f"Failed to get session status: {str(e)}")
    
    async def pause_session(self, user_id: str, session_id: str) -> bool:
        """Pause an active session"""
        try:
            session = await self.session_manager.get_session(session_id)
            if not session or session["user_id"] != user_id:
                return False
            
            if session["status"] != ConversationStatus.ACTIVE:
                return False
            
            success = await self.session_manager.pause_session(session_id)
            
            if success:
                await self.session_manager.add_message(
                    session_id=session_id,
                    message_type=MessageType.SYSTEM,
                    content="Session paused"
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error pausing session: {e}")
            return False
    
    async def resume_session(self, user_id: str, session_id: str) -> bool:
        """Resume a paused session"""
        try:
            session = await self.session_manager.get_session(session_id)
            if not session or session["user_id"] != user_id:
                return False
            
            if session["status"] != ConversationStatus.PAUSED:
                return False
            
            success = await self.session_manager.resume_session(session_id)
            
            if success:
                await self.session_manager.add_message(
                    session_id=session_id,
                    message_type=MessageType.SYSTEM,
                    content="Session resumed"
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error resuming session: {e}")
            return False
    
    async def cancel_session(self, user_id: str, session_id: str) -> bool:
        """Cancel a session"""
        try:
            session = await self.session_manager.get_session(session_id)
            if not session or session["user_id"] != user_id:
                return False
            
            success = await self.session_manager.cancel_session(session_id)
            
            if success:
                await self.session_manager.add_message(
                    session_id=session_id,
                    message_type=MessageType.SYSTEM,
                    content="Session cancelled"
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error cancelling session: {e}")
            return False
    
    async def get_conversation_history(self, user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        try:
            session = await self.session_manager.get_session(session_id)
            if not session or session["user_id"] != user_id:
                return []
            
            return session.get("conversation_history", [])
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def _generate_next_question(self, session_id: str, skill: str) -> Question:
        """Generate the next question for the session"""
        try:
            session = await self.session_manager.get_session(session_id)
            if not session:
                raise Exception("Session not found")
            
            # Generate MCQ using existing service
            mcq_result = await self.mcq_service.generate_mcqs(
                skill=skill,
                difficulty=session["difficulty"],
                question_type="technical",
                num_questions=1,
                language=session["language"]
            )
            
            if not mcq_result or not mcq_result.get("questions"):
                raise Exception("Failed to generate question")
            
            mcq_data = mcq_result["questions"][0]
            
            # Convert to our Question format
            options = []
            for key, text in mcq_data.get("options", {}).items():
                options.append(MCQOption(key=key, text=text))
            
            question = Question(
                id=mcq_data.get("id", str(uuid.uuid4())),
                type=QuestionType.MCQ,
                content=mcq_data["question"],
                options=options,
                correct_answer=mcq_data["correct_answer"],
                skill=skill,
                difficulty=session["difficulty"],
                points=1,
                time_limit_seconds=session["question_timeout_seconds"],
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "language": session["language"]
                }
            )
            
            # Add question to session
            await self.session_manager.add_question(session_id, question)
            
            # Add question to conversation history
            await self.session_manager.add_message(
                session_id=session_id,
                message_type=MessageType.QUESTION,
                content=question.content,
                metadata={
                    "question_id": question.id,
                    "skill": skill,
                    "options": [opt.dict() for opt in options]
                }
            )
            
            return question
            
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            raise Exception(f"Failed to generate question: {str(e)}")
    
    def _check_answer(self, question_data: Dict[str, Any], user_answer: str) -> bool:
        """Check if user's answer is correct"""
        correct_answer = question_data.get("correct_answer")
        if not correct_answer:
            return False
        
        # For MCQ, check exact match (case-insensitive)
        return user_answer.strip().upper() == correct_answer.strip().upper()
    
    def _generate_explanation(self, question_data: Dict[str, Any], is_correct: bool) -> Optional[str]:
        """Generate explanation for the answer"""
        if is_correct:
            return "Well done! You selected the correct answer."
        else:
            correct_answer = question_data.get("correct_answer")
            if correct_answer:
                options = question_data.get("options", {})
                correct_text = options.get(correct_answer, correct_answer)
                return f"The correct answer is {correct_answer}: {correct_text}"
        
        return None


# Global chatbot service instance
chatbot_service = ChatbotService()
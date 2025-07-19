"""
Session management service for chatbot conversations.
Handles session state, timeouts, and persistence using Firebase Firestore.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import json

from api.schemas.chatbot import (
    ConversationStatus, MessageType, Question, ConversationMessage,
    SessionSummaryResponse, QuestionType
)
from services.firebase import get_db

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages chatbot conversation sessions"""
    
    def __init__(self):
        self.db = get_db()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def create_session(
        self,
        user_id: str,
        skills: List[str],
        difficulty: str = "intermediate",
        num_questions: int = 10,
        session_timeout_minutes: int = 30,
        question_timeout_seconds: int = 120,
        language: str = "English"
    ) -> str:
        """
        Create a new chatbot session.
        
        Returns:
            session_id: Unique identifier for the session
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = now + timedelta(minutes=session_timeout_minutes)
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "status": ConversationStatus.ACTIVE,
            "skills": skills,
            "difficulty": difficulty,
            "num_questions": num_questions,
            "current_question_index": 0,
            "score": 0,
            "max_score": num_questions,  # Assuming 1 point per question
            "questions": [],  # Will be populated by chatbot service
            "answers": [],
            "conversation_history": [],
            "session_timeout_minutes": session_timeout_minutes,
            "question_timeout_seconds": question_timeout_seconds,
            "language": language,
            "created_at": now,
            "started_at": now,
            "expires_at": expires_at,
            "updated_at": now
        }
        
        # Store in Firestore
        try:
            session_ref = self.db.collection("chatbot_sessions").document(session_id)
            session_ref.set(self._serialize_session_data(session_data))
            
            # Cache in memory for quick access
            self._active_sessions[session_id] = session_data
            
            logger.info(f"Created new session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise Exception(f"Failed to create session: {str(e)}")
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        # Check memory cache first
        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            # Check if session is expired
            if self._is_session_expired(session):
                await self._expire_session(session_id)
                return None
            return session
        
        # Check Firestore
        try:
            session_ref = self.db.collection("chatbot_sessions").document(session_id)
            doc = session_ref.get()
            
            if not doc.exists:
                return None
                
            session_data = self._deserialize_session_data(doc.to_dict())
            
            # Check if session is expired
            if self._is_session_expired(session_data):
                await self._expire_session(session_id)
                return None
            
            # Cache in memory
            self._active_sessions[session_id] = session_data
            return session_data
            
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {e}")
            return None
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            # Update in memory
            session.update(updates)
            session["updated_at"] = datetime.now()
            
            # Update in Firestore
            session_ref = self.db.collection("chatbot_sessions").document(session_id)
            session_ref.update(self._serialize_session_data(updates))
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    async def add_message(
        self,
        session_id: str,
        message_type: MessageType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a message to conversation history"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            message = ConversationMessage(
                id=str(uuid.uuid4()),
                type=message_type,
                content=content,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            session["conversation_history"].append(message.dict())
            await self.update_session(session_id, {
                "conversation_history": session["conversation_history"]
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to session {session_id}: {e}")
            return False
    
    async def add_question(self, session_id: str, question: Question) -> bool:
        """Add a question to the session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            session["questions"].append(question.dict())
            await self.update_session(session_id, {
                "questions": session["questions"]
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding question to session {session_id}: {e}")
            return False
    
    async def record_answer(
        self,
        session_id: str,
        question_id: str,
        answer: str,
        is_correct: bool,
        time_taken_seconds: Optional[int] = None
    ) -> bool:
        """Record user's answer"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            answer_record = {
                "question_id": question_id,
                "answer": answer,
                "is_correct": is_correct,
                "time_taken_seconds": time_taken_seconds,
                "timestamp": datetime.now().isoformat()
            }
            
            session["answers"].append(answer_record)
            
            # Update score if correct
            if is_correct:
                session["score"] += 1
            
            # Move to next question
            session["current_question_index"] += 1
            
            await self.update_session(session_id, {
                "answers": session["answers"],
                "score": session["score"],
                "current_question_index": session["current_question_index"]
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording answer for session {session_id}: {e}")
            return False
    
    async def complete_session(self, session_id: str) -> Optional[SessionSummaryResponse]:
        """Mark session as completed and generate summary"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return None
            
            # Update status
            session["status"] = ConversationStatus.COMPLETED
            session["completed_at"] = datetime.now()
            
            # Calculate metrics
            total_questions = len(session["questions"])
            correct_answers = session["score"]
            accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            # Calculate time taken
            start_time = session["started_at"]
            end_time = session["completed_at"]
            time_taken = (end_time - start_time).total_seconds()
            
            # Generate skill breakdown
            skill_breakdown = self._generate_skill_breakdown(session)
            
            await self.update_session(session_id, {
                "status": session["status"],
                "completed_at": session["completed_at"]
            })
            
            # Remove from active cache
            if session_id in self._active_sessions:
                del self._active_sessions[session_id]
            
            summary = SessionSummaryResponse(
                session_id=session_id,
                candidate_id=session["user_id"],
                skills_assessed=session["skills"],
                total_questions=total_questions,
                correct_answers=correct_answers,
                score=session["score"],
                max_score=session["max_score"],
                accuracy_percentage=accuracy,
                time_taken_seconds=int(time_taken),
                skill_breakdown=skill_breakdown,
                completed_at=session["completed_at"]
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error completing session {session_id}: {e}")
            return None
    
    async def pause_session(self, session_id: str) -> bool:
        """Pause an active session"""
        return await self.update_session(session_id, {
            "status": ConversationStatus.PAUSED
        })
    
    async def resume_session(self, session_id: str) -> bool:
        """Resume a paused session"""
        return await self.update_session(session_id, {
            "status": ConversationStatus.ACTIVE
        })
    
    async def cancel_session(self, session_id: str) -> bool:
        """Cancel a session"""
        success = await self.update_session(session_id, {
            "status": ConversationStatus.CANCELLED
        })
        
        # Remove from active cache
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        
        return success
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10,
        status: Optional[ConversationStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get sessions for a user"""
        try:
            query = self.db.collection("chatbot_sessions").where("user_id", "==", user_id)
            
            if status:
                query = query.where("status", "==", status.value)
            
            query = query.order_by("created_at", direction="DESCENDING").limit(limit)
            
            docs = query.stream()
            sessions = []
            
            for doc in docs:
                session_data = self._deserialize_session_data(doc.to_dict())
                sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []
    
    def _is_session_expired(self, session: Dict[str, Any]) -> bool:
        """Check if session is expired"""
        expires_at = session.get("expires_at")
        if not expires_at:
            return False
        return datetime.now() > expires_at
    
    async def _expire_session(self, session_id: str):
        """Mark session as expired"""
        await self.update_session(session_id, {
            "status": ConversationStatus.EXPIRED
        })
        
        # Remove from active cache
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
    
    def _generate_skill_breakdown(self, session: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Generate skill-wise performance breakdown"""
        breakdown = {}
        
        for skill in session["skills"]:
            breakdown[skill] = {
                "total_questions": 0,
                "correct_answers": 0,
                "accuracy": 0.0,
                "average_time": 0.0
            }
        
        # Analyze questions and answers
        questions = session.get("questions", [])
        answers = session.get("answers", [])
        
        for i, question in enumerate(questions):
            skill = question.get("skill", "unknown")
            if skill in breakdown:
                breakdown[skill]["total_questions"] += 1
                
                # Find corresponding answer
                if i < len(answers):
                    answer = answers[i]
                    if answer.get("is_correct"):
                        breakdown[skill]["correct_answers"] += 1
        
        # Calculate percentages
        for skill in breakdown:
            total = breakdown[skill]["total_questions"]
            correct = breakdown[skill]["correct_answers"]
            breakdown[skill]["accuracy"] = (correct / total * 100) if total > 0 else 0
        
        return breakdown
    
    def _serialize_session_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize session data for Firestore storage"""
        serialized = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                serialized[key] = json.dumps(value, default=str)
            else:
                serialized[key] = value
        return serialized
    
    def _deserialize_session_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize session data from Firestore"""
        deserialized = {}
        for key, value in data.items():
            if key.endswith("_at") and isinstance(value, str):
                try:
                    deserialized[key] = datetime.fromisoformat(value)
                except:
                    deserialized[key] = value
            elif key in ["questions", "answers", "conversation_history", "skills"] and isinstance(value, str):
                try:
                    deserialized[key] = json.loads(value)
                except:
                    deserialized[key] = value if isinstance(value, list) else []
            else:
                deserialized[key] = value
        return deserialized


# Global session manager instance
session_manager = SessionManager()
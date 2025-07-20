"""
Schemas for chatbot interaction API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ConversationStatus(str, Enum):
    """Status of a conversation session"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class MessageType(str, Enum):
    """Type of message in conversation"""
    SYSTEM = "system"
    QUESTION = "question"
    USER_ANSWER = "user_answer"
    FEEDBACK = "feedback"
    PROGRESS = "progress"


class QuestionType(str, Enum):
    """Type of question being asked"""
    MCQ = "mcq"
    OPEN_ENDED = "open_ended"
    CODE_REVIEW = "code_review"
    SCENARIO = "scenario"


class ConversationMessage(BaseModel):
    """Individual message in conversation"""
    id: str
    type: MessageType
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class MCQOption(BaseModel):
    """Multiple choice question option"""
    key: str = Field(..., description="Option key (A, B, C, D)")
    text: str = Field(..., description="Option text")


class Question(BaseModel):
    """Question model for chatbot interaction"""
    id: str
    type: QuestionType
    content: str
    options: Optional[List[MCQOption]] = None
    correct_answer: Optional[str] = None
    skill: str
    difficulty: str
    points: int = 1
    time_limit_seconds: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionInitRequest(BaseModel):
    """Request to initialize a chatbot session"""
    skills: List[str] = Field(..., description="Skills to assess")
    difficulty: str = Field(default="intermediate", description="Difficulty level")
    num_questions: int = Field(default=10, description="Number of questions")
    session_timeout_minutes: int = Field(default=30, description="Session timeout in minutes")
    question_timeout_seconds: int = Field(default=120, description="Per question timeout")
    language: str = Field(default="English", description="Language for questions")


class SessionInitResponse(BaseModel):
    """Response from session initialization"""
    session_id: str
    status: ConversationStatus
    total_questions: int
    current_question_index: int
    skills: List[str]
    expires_at: datetime
    first_question: Optional[Question] = None


class AnswerSubmissionRequest(BaseModel):
    """Request to submit an answer"""
    session_id: str
    question_id: str
    answer: str
    time_taken_seconds: Optional[int] = None


class AnswerSubmissionResponse(BaseModel):
    """Response from answer submission"""
    is_correct: bool
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points_earned: int
    total_score: int
    next_question: Optional[Question] = None
    session_completed: bool = False


class SessionStatusResponse(BaseModel):
    """Session status information"""
    session_id: str
    status: ConversationStatus
    current_question_index: int
    total_questions: int
    score: int
    max_score: int
    time_remaining_seconds: Optional[int] = None
    skills_assessed: List[str]
    started_at: datetime
    expires_at: datetime


class ConversationHistoryResponse(BaseModel):
    """Conversation history for a session"""
    session_id: str
    messages: List[ConversationMessage]
    total_messages: int


class SessionSummaryResponse(BaseModel):
    """Summary of completed session"""
    session_id: str
    candidate_id: str
    skills_assessed: List[str]
    total_questions: int
    correct_answers: int
    score: int
    max_score: int
    accuracy_percentage: float
    time_taken_seconds: int
    skill_breakdown: Dict[str, Dict[str, Any]]
    completed_at: datetime


class AnalyticsRequest(BaseModel):
    """Request for analytics data"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    candidate_id: Optional[str] = None
    skills: Optional[List[str]] = None


class AnalyticsResponse(BaseModel):
    """Analytics response"""
    total_sessions: int
    completed_sessions: int
    average_score: float
    average_time_per_session: float
    skill_performance: Dict[str, Dict[str, Any]]
    popular_skills: List[Dict[str, Any]]
    completion_rate: float


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str
    session_id: Optional[str] = None
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response format"""
    error: str
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class RateLimitResponse(BaseModel):
    """Rate limit response"""
    message: str
    retry_after_seconds: int
    requests_remaining: int
    reset_time: datetime
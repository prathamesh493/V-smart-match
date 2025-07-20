"""
Unit tests for chatbot schemas and basic functionality.
These tests don't require external services or network access.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from api.schemas.chatbot import (
    SessionInitRequest, SessionInitResponse, AnswerSubmissionRequest,
    AnswerSubmissionResponse, ConversationStatus, MessageType, QuestionType,
    Question, MCQOption, ConversationMessage, SessionStatusResponse,
    AnalyticsRequest, AnalyticsResponse, WebSocketMessage, ErrorResponse
)


class TestChatbotSchemas:
    """Test chatbot schema validation and behavior"""
    
    def test_session_init_request_valid(self):
        """Test valid SessionInitRequest creation"""
        request = SessionInitRequest(
            skills=["Python", "JavaScript"],
            difficulty="intermediate",
            num_questions=5,
            session_timeout_minutes=45,
            question_timeout_seconds=90,
            language="English"
        )
        
        assert request.skills == ["Python", "JavaScript"]
        assert request.difficulty == "intermediate"
        assert request.num_questions == 5
        assert request.session_timeout_minutes == 45
        assert request.question_timeout_seconds == 90
        assert request.language == "English"
    
    def test_session_init_request_defaults(self):
        """Test SessionInitRequest default values"""
        request = SessionInitRequest(skills=["Java"])
        
        assert request.skills == ["Java"]
        assert request.difficulty == "intermediate"
        assert request.num_questions == 10
        assert request.session_timeout_minutes == 30
        assert request.question_timeout_seconds == 120
        assert request.language == "English"
    
    def test_session_init_request_validation(self):
        """Test SessionInitRequest validation"""
        # Empty skills should be allowed (pydantic allows empty lists)
        request = SessionInitRequest(skills=[])
        assert request.skills == []
        
        # Valid request should pass
        request = SessionInitRequest(skills=["Python"])
        assert len(request.skills) == 1
    
    def test_mcq_option_creation(self):
        """Test MCQOption model"""
        option = MCQOption(key="A", text="This is option A")
        assert option.key == "A"
        assert option.text == "This is option A"
    
    def test_question_creation(self):
        """Test Question model creation"""
        options = [
            MCQOption(key="A", text="Option A"),
            MCQOption(key="B", text="Option B"),
            MCQOption(key="C", text="Option C"),
            MCQOption(key="D", text="Option D")
        ]
        
        question = Question(
            id="q1",
            type=QuestionType.MCQ,
            content="What is Python?",
            options=options,
            correct_answer="A",
            skill="Python",
            difficulty="beginner",
            points=1,
            time_limit_seconds=120
        )
        
        assert question.id == "q1"
        assert question.type == QuestionType.MCQ
        assert question.content == "What is Python?"
        assert len(question.options) == 4
        assert question.correct_answer == "A"
        assert question.skill == "Python"
        assert question.difficulty == "beginner"
        assert question.points == 1
        assert question.time_limit_seconds == 120
    
    def test_conversation_message_creation(self):
        """Test ConversationMessage model"""
        now = datetime.now()
        message = ConversationMessage(
            id="msg1",
            type=MessageType.QUESTION,
            content="What is your favorite programming language?",
            timestamp=now,
            metadata={"skill": "general", "difficulty": "easy"}
        )
        
        assert message.id == "msg1"
        assert message.type == MessageType.QUESTION
        assert message.content == "What is your favorite programming language?"
        assert message.timestamp == now
        assert message.metadata["skill"] == "general"
    
    def test_answer_submission_request(self):
        """Test AnswerSubmissionRequest model"""
        request = AnswerSubmissionRequest(
            session_id="session123",
            question_id="q1",
            answer="A",
            time_taken_seconds=45
        )
        
        assert request.session_id == "session123"
        assert request.question_id == "q1"
        assert request.answer == "A"
        assert request.time_taken_seconds == 45
    
    def test_answer_submission_response(self):
        """Test AnswerSubmissionResponse model"""
        response = AnswerSubmissionResponse(
            is_correct=True,
            correct_answer="A",
            explanation="Correct! Python is indeed a programming language.",
            points_earned=1,
            total_score=5,
            next_question=None,
            session_completed=False
        )
        
        assert response.is_correct is True
        assert response.correct_answer == "A"
        assert response.explanation == "Correct! Python is indeed a programming language."
        assert response.points_earned == 1
        assert response.total_score == 5
        assert response.next_question is None
        assert response.session_completed is False
    
    def test_session_status_response(self):
        """Test SessionStatusResponse model"""
        now = datetime.now()
        expires_at = datetime(2024, 12, 31, 23, 59, 59)
        
        response = SessionStatusResponse(
            session_id="session123",
            status=ConversationStatus.ACTIVE,
            current_question_index=2,
            total_questions=10,
            score=1,
            max_score=10,
            time_remaining_seconds=1800,
            skills_assessed=["Python", "JavaScript"],
            started_at=now,
            expires_at=expires_at
        )
        
        assert response.session_id == "session123"
        assert response.status == ConversationStatus.ACTIVE
        assert response.current_question_index == 2
        assert response.total_questions == 10
        assert response.score == 1
        assert response.max_score == 10
        assert response.time_remaining_seconds == 1800
        assert response.skills_assessed == ["Python", "JavaScript"]
        assert response.started_at == now
        assert response.expires_at == expires_at
    
    def test_analytics_request(self):
        """Test AnalyticsRequest model"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        request = AnalyticsRequest(
            start_date=start_date,
            end_date=end_date,
            candidate_id="user123",
            skills=["Python", "JavaScript"]
        )
        
        assert request.start_date == start_date
        assert request.end_date == end_date
        assert request.candidate_id == "user123"
        assert request.skills == ["Python", "JavaScript"]
    
    def test_analytics_response(self):
        """Test AnalyticsResponse model"""
        response = AnalyticsResponse(
            total_sessions=100,
            completed_sessions=85,
            average_score=75.5,
            average_time_per_session=1200.0,
            skill_performance={
                "Python": {
                    "total_questions": 50,
                    "correct_answers": 40,
                    "accuracy_percentage": 80.0
                }
            },
            popular_skills=[
                {"skill": "Python", "usage_count": 45},
                {"skill": "JavaScript", "usage_count": 35}
            ],
            completion_rate=85.0
        )
        
        assert response.total_sessions == 100
        assert response.completed_sessions == 85
        assert response.average_score == 75.5
        assert response.average_time_per_session == 1200.0
        assert "Python" in response.skill_performance
        assert len(response.popular_skills) == 2
        assert response.completion_rate == 85.0
    
    def test_websocket_message(self):
        """Test WebSocketMessage model"""
        message = WebSocketMessage(
            type="question_delivered",
            session_id="session123",
            data={"question_id": "q1", "content": "What is Python?"}
        )
        
        assert message.type == "question_delivered"
        assert message.session_id == "session123"
        assert message.data["question_id"] == "q1"
        assert isinstance(message.timestamp, datetime)
    
    def test_error_response(self):
        """Test ErrorResponse model"""
        error = ErrorResponse(
            error="validation_error",
            message="Invalid input provided",
            code="E001",
            details={"field": "skills", "issue": "cannot be empty"}
        )
        
        assert error.error == "validation_error"
        assert error.message == "Invalid input provided"
        assert error.code == "E001"
        assert error.details["field"] == "skills"


class TestEnums:
    """Test enum values and behavior"""
    
    def test_conversation_status_enum(self):
        """Test ConversationStatus enum values"""
        assert ConversationStatus.ACTIVE == "active"
        assert ConversationStatus.PAUSED == "paused"
        assert ConversationStatus.COMPLETED == "completed"
        assert ConversationStatus.EXPIRED == "expired"
        assert ConversationStatus.CANCELLED == "cancelled"
    
    def test_message_type_enum(self):
        """Test MessageType enum values"""
        assert MessageType.SYSTEM == "system"
        assert MessageType.QUESTION == "question"
        assert MessageType.USER_ANSWER == "user_answer"
        assert MessageType.FEEDBACK == "feedback"
        assert MessageType.PROGRESS == "progress"
    
    def test_question_type_enum(self):
        """Test QuestionType enum values"""
        assert QuestionType.MCQ == "mcq"
        assert QuestionType.OPEN_ENDED == "open_ended"
        assert QuestionType.CODE_REVIEW == "code_review"
        assert QuestionType.SCENARIO == "scenario"


class TestValidationEdgeCases:
    """Test edge cases and validation scenarios"""
    
    def test_session_init_request_edge_cases(self):
        """Test edge cases for SessionInitRequest"""
        # Test with single skill
        request = SessionInitRequest(skills=["Python"])
        assert len(request.skills) == 1
        
        # Test with multiple skills
        request = SessionInitRequest(skills=["Python", "Java", "JavaScript", "C++"])
        assert len(request.skills) == 4
        
        # Test with minimum questions
        request = SessionInitRequest(skills=["Python"], num_questions=1)
        assert request.num_questions == 1
        
        # Test with different difficulty levels
        for difficulty in ["beginner", "intermediate", "advanced"]:
            request = SessionInitRequest(skills=["Python"], difficulty=difficulty)
            assert request.difficulty == difficulty
    
    def test_question_without_options(self):
        """Test Question model without options (for open-ended questions)"""
        question = Question(
            id="q1",
            type=QuestionType.OPEN_ENDED,
            content="Explain the difference between a list and a tuple in Python.",
            skill="Python",
            difficulty="intermediate",
            points=2
        )
        
        assert question.options is None
        assert question.correct_answer is None
        assert question.type == QuestionType.OPEN_ENDED
    
    def test_answer_submission_without_time(self):
        """Test AnswerSubmissionRequest without time_taken_seconds"""
        request = AnswerSubmissionRequest(
            session_id="session123",
            question_id="q1",
            answer="A"
        )
        
        assert request.time_taken_seconds is None
    
    def test_analytics_request_minimal(self):
        """Test AnalyticsRequest with minimal data"""
        request = AnalyticsRequest()
        
        assert request.start_date is None
        assert request.end_date is None
        assert request.candidate_id is None
        assert request.skills is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
API routes for chatbot interaction flow.
Handles session management, question delivery, answer submission, and real-time communication.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, status, Request
from fastapi.responses import JSONResponse

from api.auth import get_current_user, UserData
from api.schemas.chatbot import (
    SessionInitRequest, SessionInitResponse, AnswerSubmissionRequest,
    AnswerSubmissionResponse, SessionStatusResponse, ConversationHistoryResponse,
    AnalyticsRequest, AnalyticsResponse, WebSocketMessage, ErrorResponse,
    RateLimitResponse, ConversationStatus
)
from services.chatbot import chatbot_service
from services.analytics import analytics_service

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_message(self, session_id: str, message: Dict):
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                self.disconnect(session_id)
    
    async def broadcast_to_user_sessions(self, user_id: str, message: Dict):
        """Broadcast message to all sessions for a user"""
        # This would require tracking user_id to session_id mapping
        # For now, just implement single session per user
        pass

manager = ConnectionManager()

# Add rate limit error handler
# Note: Rate limiting will be handled at the application level


@router.post(
    "/chatbot/session/init",
    response_model=SessionInitResponse,
    responses={
        400: {"model": ErrorResponse},
        429: {"model": RateLimitResponse},
        500: {"model": ErrorResponse}
    },
    summary="Initialize chatbot session",
    description="Create a new chatbot session for skill assessment with the first question"
)
async def init_session(
    request: SessionInitRequest,
    current_user: UserData = Depends(get_current_user)
):
    """
    Initialize a new chatbot session for skill assessment.
    
    - **skills**: List of skills to assess (required)
    - **difficulty**: Question difficulty level (beginner/intermediate/advanced)
    - **num_questions**: Total number of questions (1-50)
    - **session_timeout_minutes**: Session timeout in minutes
    - **question_timeout_seconds**: Per-question timeout in seconds
    - **language**: Language for questions
    """
    try:
        # Validate request
        if not request.skills:
            raise HTTPException(status_code=400, detail="At least one skill is required")
        
        if not (1 <= request.num_questions <= 50):
            raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 50")
        
        response = await chatbot_service.initialize_session(
            user_id=current_user.user_id,
            skills=request.skills,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            session_timeout_minutes=request.session_timeout_minutes,
            question_timeout_seconds=request.question_timeout_seconds,
            language=request.language
        )
        
        # Track analytics event
        await analytics_service.track_session_event(
            session_id=response.session_id,
            event_type="session_initialized",
            metadata={
                "user_id": current_user.user_id,
                "skills": request.skills,
                "difficulty": request.difficulty,
                "num_questions": request.num_questions
            }
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in session initialization: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initializing session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/chatbot/session/{session_id}/answer",
    response_model=AnswerSubmissionResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        429: {"model": RateLimitResponse},
        500: {"model": ErrorResponse}
    },
    summary="Submit answer",
    description="Submit an answer to the current question and get feedback with next question"
)
async def submit_answer(
    session_id: str,
    request: AnswerSubmissionRequest,
    current_user: UserData = Depends(get_current_user)
):
    """
    Submit an answer to the current question.
    
    - **question_id**: ID of the question being answered
    - **answer**: User's answer (A, B, C, D for MCQ)
    - **time_taken_seconds**: Time taken to answer (optional)
    """
    try:
        if request.session_id != session_id:
            raise HTTPException(status_code=400, detail="Session ID mismatch")
        
        response = await chatbot_service.submit_answer(
            user_id=current_user.user_id,
            session_id=session_id,
            question_id=request.question_id,
            answer=request.answer,
            time_taken_seconds=request.time_taken_seconds
        )
        
        # Send real-time update via WebSocket
        ws_message = {
            "type": "answer_result",
            "session_id": session_id,
            "data": response.dict(),
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_message(session_id, ws_message)
        
        # Track analytics event
        await analytics_service.track_session_event(
            session_id=session_id,
            event_type="answer_submitted",
            metadata={
                "user_id": current_user.user_id,
                "question_id": request.question_id,
                "is_correct": response.is_correct,
                "time_taken": request.time_taken_seconds
            }
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in answer submission: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/chatbot/session/{session_id}/status",
    response_model=SessionStatusResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Get session status",
    description="Get current status and progress of a chatbot session"
)
async def get_session_status(
    session_id: str,
    current_user: UserData = Depends(get_current_user)
):
    """Get current session status and progress"""
    try:
        response = await chatbot_service.get_session_status(
            user_id=current_user.user_id,
            session_id=session_id
        )
        return response
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/chatbot/session/{session_id}/pause",
    responses={
        200: {"description": "Session paused successfully"},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Pause session",
    description="Pause an active chatbot session"
)
async def pause_session(
    session_id: str,
    current_user: UserData = Depends(get_current_user)
):
    """Pause an active session"""
    try:
        success = await chatbot_service.pause_session(
            user_id=current_user.user_id,
            session_id=session_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or cannot be paused")
        
        # Send real-time update
        ws_message = {
            "type": "session_paused",
            "session_id": session_id,
            "data": {"status": ConversationStatus.PAUSED},
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_message(session_id, ws_message)
        
        return {"message": "Session paused successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/chatbot/session/{session_id}/resume",
    responses={
        200: {"description": "Session resumed successfully"},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Resume session",
    description="Resume a paused chatbot session"
)
async def resume_session(
    session_id: str,
    current_user: UserData = Depends(get_current_user)
):
    """Resume a paused session"""
    try:
        success = await chatbot_service.resume_session(
            user_id=current_user.user_id,
            session_id=session_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or cannot be resumed")
        
        # Send real-time update
        ws_message = {
            "type": "session_resumed",
            "session_id": session_id,
            "data": {"status": ConversationStatus.ACTIVE},
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_message(session_id, ws_message)
        
        return {"message": "Session resumed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/chatbot/session/{session_id}",
    responses={
        200: {"description": "Session cancelled successfully"},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Cancel session",
    description="Cancel a chatbot session"
)
async def cancel_session(
    session_id: str,
    current_user: UserData = Depends(get_current_user)
):
    """Cancel a session"""
    try:
        success = await chatbot_service.cancel_session(
            user_id=current_user.user_id,
            session_id=session_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or cannot be cancelled")
        
        # Send real-time update and close WebSocket
        ws_message = {
            "type": "session_cancelled",
            "session_id": session_id,
            "data": {"status": ConversationStatus.CANCELLED},
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_message(session_id, ws_message)
        manager.disconnect(session_id)
        
        return {"message": "Session cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/chatbot/session/{session_id}/history",
    response_model=ConversationHistoryResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Get conversation history",
    description="Get the complete conversation history for a session"
)
async def get_conversation_history(
    session_id: str,
    current_user: UserData = Depends(get_current_user)
):
    """Get conversation history for a session"""
    try:
        history = await chatbot_service.get_conversation_history(
            user_id=current_user.user_id,
            session_id=session_id
        )
        
        return ConversationHistoryResponse(
            session_id=session_id,
            messages=history,
            total_messages=len(history)
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/chatbot/analytics",
    response_model=AnalyticsResponse,
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Get analytics data",
    description="Get analytics and performance metrics for chatbot interactions"
)
async def get_analytics(
    request: AnalyticsRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Get analytics data for chatbot interactions"""
    try:
        response = await analytics_service.get_analytics(
            start_date=request.start_date,
            end_date=request.end_date,
            candidate_id=request.candidate_id,
            skills=request.skills
        )
        return response
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/chatbot/analytics/user-trends",
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Get user performance trends",
    description="Get performance trends for the current user"
)
async def get_user_trends(
    days: int = 30,
    current_user: UserData = Depends(get_current_user)
):
    """Get performance trends for the current user"""
    try:
        trends = await analytics_service.get_user_performance_trends(
            user_id=current_user.user_id,
            days=days
        )
        return trends
        
    except Exception as e:
        logger.error(f"Error getting user trends: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/chatbot/health",
    summary="Get system health metrics",
    description="Get system health and performance metrics"
)
async def get_system_health():
    """Get system health metrics"""
    try:
        health_metrics = await analytics_service.get_system_health_metrics()
        return health_metrics
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.websocket("/chatbot/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chatbot communication.
    
    Supports:
    - Real-time question delivery
    - Live session status updates  
    - Session timeout notifications
    - Connection heartbeat
    """
    await manager.connect(websocket, session_id)
    
    try:
        # Send connection confirmation
        await manager.send_message(session_id, {
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "ping":
                    # Heartbeat response
                    await manager.send_message(session_id, {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
                elif message_type == "get_status":
                    # Send current session status
                    # This would require authentication over WebSocket
                    # For now, just acknowledge
                    await manager.send_message(session_id, {
                        "type": "status_request_received",
                        "timestamp": datetime.now().isoformat()
                    })
                
            except json.JSONDecodeError:
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(session_id)
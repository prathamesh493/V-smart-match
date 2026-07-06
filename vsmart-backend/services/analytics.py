"""
Analytics service for chatbot interactions and user engagement metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

from api.schemas.chatbot import AnalyticsResponse, ConversationStatus
from services.firebase import get_db

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for tracking and analyzing chatbot usage and performance"""
    
    def __init__(self):
        self.db = get_db()
    
    async def get_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        candidate_id: Optional[str] = None,
        skills: Optional[List[str]] = None
    ) -> AnalyticsResponse:
        """
        Get comprehensive analytics for chatbot sessions.
        
        Args:
            start_date: Start date for analytics period
            end_date: End date for analytics period
            candidate_id: Specific candidate to analyze
            skills: Specific skills to analyze
            
        Returns:
            AnalyticsResponse with aggregated metrics
        """
        try:
            # Set default date range to last 30 days if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Build query
            query = self.db.collection("chatbot_sessions")
            
            # Add filters
            query = query.where("created_at", ">=", start_date.isoformat())
            query = query.where("created_at", "<=", end_date.isoformat())
            
            if candidate_id:
                query = query.where("user_id", "==", candidate_id)
            
            # Execute query
            sessions_docs = query.stream()
            sessions = []
            
            for doc in sessions_docs:
                session_data = doc.to_dict()
                # Filter by skills if specified
                if skills:
                    session_skills = session_data.get("skills", [])
                    if not any(skill in session_skills for skill in skills):
                        continue
                sessions.append(session_data)
            
            # Calculate metrics
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.get("status") == ConversationStatus.COMPLETED.value])
            
            # Calculate averages
            total_scores = []
            session_durations = []
            skill_stats = defaultdict(lambda: {"total": 0, "correct": 0, "sessions": 0})
            skill_popularity = defaultdict(int)
            
            for session in sessions:
                # Score analysis
                if session.get("status") == ConversationStatus.COMPLETED.value:
                    score = session.get("score", 0)
                    max_score = session.get("max_score", 1)
                    score_percentage = (score / max_score * 100) if max_score > 0 else 0
                    total_scores.append(score_percentage)
                    
                    # Duration analysis
                    if session.get("started_at") and session.get("completed_at"):
                        try:
                            start_time = datetime.fromisoformat(session["started_at"])
                            end_time = datetime.fromisoformat(session["completed_at"])
                            duration = (end_time - start_time).total_seconds()
                            session_durations.append(duration)
                        except:
                            pass
                
                # Skill analysis
                session_skills = session.get("skills", [])
                for skill in session_skills:
                    skill_popularity[skill] += 1
                    skill_stats[skill]["sessions"] += 1
                
                # Question-level skill analysis
                questions = session.get("questions", [])
                answers = session.get("answers", [])
                
                for i, question in enumerate(questions):
                    skill = question.get("skill", "unknown")
                    skill_stats[skill]["total"] += 1
                    
                    if i < len(answers) and answers[i].get("is_correct"):
                        skill_stats[skill]["correct"] += 1
            
            # Calculate averages
            average_score = sum(total_scores) / len(total_scores) if total_scores else 0
            average_duration = sum(session_durations) / len(session_durations) if session_durations else 0
            completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            # Build skill performance data
            skill_performance = {}
            for skill, stats in skill_stats.items():
                accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
                skill_performance[skill] = {
                    "total_questions": stats["total"],
                    "correct_answers": stats["correct"],
                    "accuracy_percentage": round(accuracy, 2),
                    "total_sessions": stats["sessions"]
                }
            
            # Build popular skills data
            popular_skills = [
                {"skill": skill, "usage_count": count}
                for skill, count in sorted(skill_popularity.items(), key=lambda x: x[1], reverse=True)
            ]
            
            return AnalyticsResponse(
                total_sessions=total_sessions,
                completed_sessions=completed_sessions,
                average_score=round(average_score, 2),
                average_time_per_session=round(average_duration, 2),
                skill_performance=skill_performance,
                popular_skills=popular_skills[:10],  # Top 10 skills
                completion_rate=round(completion_rate, 2)
            )
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            raise Exception(f"Failed to generate analytics: {str(e)}")
    
    async def track_session_event(
        self,
        session_id: str,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track specific events during sessions for detailed analytics"""
        try:
            event_data = {
                "session_id": session_id,
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Store in analytics collection
            self.db.collection("chatbot_events").add(event_data)
            return True
            
        except Exception as e:
            logger.error(f"Error tracking session event: {e}")
            return False
    
    async def get_user_performance_trends(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance trends for a specific user"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get user sessions
            query = self.db.collection("chatbot_sessions").where("user_id", "==", user_id)
            query = query.where("created_at", ">=", start_date.isoformat())
            query = query.where("created_at", "<=", end_date.isoformat())
            query = query.order_by("created_at")
            
            sessions_docs = query.stream()
            sessions = [doc.to_dict() for doc in sessions_docs]
            
            # Calculate trends
            daily_scores = defaultdict(list)
            skill_progress = defaultdict(list)
            
            for session in sessions:
                if session.get("status") == ConversationStatus.COMPLETED.value:
                    date_key = session["created_at"][:10]  # YYYY-MM-DD
                    
                    score = session.get("score", 0)
                    max_score = session.get("max_score", 1)
                    score_percentage = (score / max_score * 100) if max_score > 0 else 0
                    daily_scores[date_key].append(score_percentage)
                    
                    # Track skill progress
                    for skill in session.get("skills", []):
                        skill_progress[skill].append({
                            "date": date_key,
                            "score": score_percentage
                        })
            
            return {
                "user_id": user_id,
                "period_days": days,
                "daily_average_scores": {
                    date: sum(scores) / len(scores) if scores else 0
                    for date, scores in daily_scores.items()
                },
                "skill_progress": dict(skill_progress),
                "total_sessions": len(sessions),
                "improvement_trend": self._calculate_improvement_trend(daily_scores)
            }
            
        except Exception as e:
            logger.error(f"Error getting user performance trends: {e}")
            return {}
    
    async def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get system health and performance metrics"""
        try:
            now = datetime.now()
            last_24h = now - timedelta(hours=24)
            
            # Active sessions
            active_sessions = self.db.collection("chatbot_sessions").where(
                "status", "==", ConversationStatus.ACTIVE.value
            ).stream()
            active_count = len(list(active_sessions))
            
            # Sessions in last 24h
            recent_sessions = self.db.collection("chatbot_sessions").where(
                "created_at", ">=", last_24h.isoformat()
            ).stream()
            recent_sessions_list = list(recent_sessions)
            
            # Error tracking (if we implement error logging)
            error_count = 0  # Placeholder
            
            # Average response time (placeholder for actual implementation)
            avg_response_time = 0.5  # seconds
            
            return {
                "active_sessions": active_count,
                "sessions_last_24h": len(recent_sessions_list),
                "error_rate": error_count,
                "average_response_time_seconds": avg_response_time,
                "system_status": "healthy",
                "last_updated": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health metrics: {e}")
            return {
                "system_status": "error",
                "error_message": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def _calculate_improvement_trend(self, daily_scores: Dict[str, List[float]]) -> str:
        """Calculate improvement trend based on daily scores"""
        if len(daily_scores) < 2:
            return "insufficient_data"
        
        dates = sorted(daily_scores.keys())
        first_half = dates[:len(dates)//2]
        second_half = dates[len(dates)//2:]
        
        first_half_avg = sum(
            sum(daily_scores[date]) / len(daily_scores[date])
            for date in first_half if daily_scores[date]
        ) / len(first_half) if first_half else 0
        
        second_half_avg = sum(
            sum(daily_scores[date]) / len(daily_scores[date])
            for date in second_half if daily_scores[date]
        ) / len(second_half) if second_half else 0
        
        if second_half_avg > first_half_avg + 5:
            return "improving"
        elif second_half_avg < first_half_avg - 5:
            return "declining"
        else:
            return "stable"


# Global analytics service instance
analytics_service = AnalyticsService()
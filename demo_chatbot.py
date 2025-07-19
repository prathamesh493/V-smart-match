"""
Demonstration script for chatbot API endpoints.
Shows how the chatbot interaction flow would work.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Mock implementations for demonstration
class MockChatbotService:
    """Mock chatbot service for demonstration"""
    
    def __init__(self):
        self.sessions = {}
        self.question_pool = [
            {
                "id": "q1",
                "question": "What is Python?",
                "options": {
                    "A": "A snake",
                    "B": "A programming language",
                    "C": "A type of car",
                    "D": "A mathematical concept"
                },
                "correct_answer": "B",
                "skill": "Python",
                "difficulty": "beginner"
            },
            {
                "id": "q2", 
                "question": "Which of the following is a Python web framework?",
                "options": {
                    "A": "React",
                    "B": "Angular",
                    "C": "Django",
                    "D": "Vue.js"
                },
                "correct_answer": "C",
                "skill": "Python",
                "difficulty": "intermediate"
            }
        ]
    
    async def initialize_session(self, user_id: str, skills: list, **kwargs) -> Dict[str, Any]:
        """Mock session initialization"""
        session_id = f"session_{len(self.sessions) + 1}"
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "skills": skills,
            "current_question_index": 0,
            "score": 0,
            "questions": [],
            "answers": [],
            "status": "active",
            "created_at": datetime.now(),
            **kwargs
        }
        
        self.sessions[session_id] = session_data
        
        # Generate first question
        first_question = self.question_pool[0].copy()
        session_data["questions"].append(first_question)
        
        return {
            "session_id": session_id,
            "status": "active",
            "total_questions": kwargs.get("num_questions", 5),
            "current_question_index": 0,
            "skills": skills,
            "expires_at": datetime.now(),
            "first_question": first_question
        }
    
    async def submit_answer(self, user_id: str, session_id: str, question_id: str, answer: str, **kwargs) -> Dict[str, Any]:
        """Mock answer submission"""
        session = self.sessions.get(session_id)
        if not session or session["user_id"] != user_id:
            raise Exception("Session not found")
        
        # Find the current question
        current_question = session["questions"][session["current_question_index"]]
        is_correct = current_question["correct_answer"] == answer.upper()
        
        # Record answer
        session["answers"].append({
            "question_id": question_id,
            "answer": answer,
            "is_correct": is_correct
        })
        
        if is_correct:
            session["score"] += 1
        
        session["current_question_index"] += 1
        
        # Generate next question if available
        next_question = None
        session_completed = session["current_question_index"] >= len(self.question_pool)
        
        if not session_completed and session["current_question_index"] < len(self.question_pool):
            next_question = self.question_pool[session["current_question_index"]].copy()
            session["questions"].append(next_question)
        
        return {
            "is_correct": is_correct,
            "correct_answer": current_question["correct_answer"],
            "explanation": f"The correct answer is {current_question['correct_answer']}: {current_question['options'][current_question['correct_answer']]}",
            "points_earned": 1 if is_correct else 0,
            "total_score": session["score"],
            "next_question": next_question,
            "session_completed": session_completed
        }
    
    async def get_session_status(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Mock session status"""
        session = self.sessions.get(session_id)
        if not session or session["user_id"] != user_id:
            raise Exception("Session not found")
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "current_question_index": session["current_question_index"],
            "total_questions": len(self.question_pool),
            "score": session["score"],
            "max_score": len(self.question_pool),
            "skills_assessed": session["skills"],
            "started_at": session["created_at"],
            "expires_at": session["created_at"]
        }


async def demonstrate_chatbot_flow():
    """Demonstrate the complete chatbot interaction flow"""
    print("🤖 Chatbot API Demonstration")
    print("=" * 50)
    
    service = MockChatbotService()
    user_id = "demo_user_123"
    
    # 1. Initialize Session
    print("\n1. 🚀 Initializing chatbot session...")
    init_response = await service.initialize_session(
        user_id=user_id,
        skills=["Python", "JavaScript"],
        difficulty="intermediate",
        num_questions=2
    )
    
    session_id = init_response["session_id"]
    print(f"   ✓ Session created: {session_id}")
    print(f"   ✓ Skills to assess: {init_response['skills']}")
    print(f"   ✓ Total questions: {init_response['total_questions']}")
    
    # Show first question
    first_question = init_response["first_question"]
    print(f"\n   📝 First Question: {first_question['question']}")
    for key, option in first_question["options"].items():
        print(f"      {key}. {option}")
    
    # 2. Submit First Answer
    print("\n2. 📤 Submitting answer to first question...")
    answer1 = "B"  # Correct answer
    answer_response1 = await service.submit_answer(
        user_id=user_id,
        session_id=session_id,
        question_id=first_question["id"],
        answer=answer1
    )
    
    print(f"   Answer submitted: {answer1}")
    print(f"   ✓ Correct: {answer_response1['is_correct']}")
    print(f"   📊 Current score: {answer_response1['total_score']}")
    print(f"   💬 Explanation: {answer_response1['explanation']}")
    
    # Show next question
    if answer_response1["next_question"]:
        next_question = answer_response1["next_question"]
        print(f"\n   📝 Next Question: {next_question['question']}")
        for key, option in next_question["options"].items():
            print(f"      {key}. {option}")
    
    # 3. Submit Second Answer
    print("\n3. 📤 Submitting answer to second question...")
    answer2 = "A"  # Incorrect answer
    answer_response2 = await service.submit_answer(
        user_id=user_id,
        session_id=session_id,
        question_id=next_question["id"],
        answer=answer2
    )
    
    print(f"   Answer submitted: {answer2}")
    print(f"   ✗ Correct: {answer_response2['is_correct']}")
    print(f"   📊 Final score: {answer_response2['total_score']}")
    print(f"   💬 Explanation: {answer_response2['explanation']}")
    print(f"   🏁 Session completed: {answer_response2['session_completed']}")
    
    # 4. Get Final Session Status
    print("\n4. 📋 Getting final session status...")
    final_status = await service.get_session_status(user_id, session_id)
    
    print(f"   Session ID: {final_status['session_id']}")
    print(f"   Status: {final_status['status']}")
    print(f"   Questions answered: {final_status['current_question_index']}/{final_status['total_questions']}")
    print(f"   Final score: {final_status['score']}/{final_status['max_score']}")
    print(f"   Skills assessed: {', '.join(final_status['skills_assessed'])}")
    
    # 5. Show API Endpoint Summary
    print("\n5. 🌐 API Endpoints Summary")
    print("-" * 30)
    
    endpoints = [
        ("POST", "/api/chatbot/session/init", "Initialize new session"),
        ("POST", "/api/chatbot/session/{id}/answer", "Submit answer"),
        ("GET", "/api/chatbot/session/{id}/status", "Get session status"),
        ("POST", "/api/chatbot/session/{id}/pause", "Pause session"),
        ("POST", "/api/chatbot/session/{id}/resume", "Resume session"),
        ("DELETE", "/api/chatbot/session/{id}", "Cancel session"),
        ("GET", "/api/chatbot/session/{id}/history", "Get conversation history"),
        ("POST", "/api/chatbot/analytics", "Get analytics data"),
        ("GET", "/api/chatbot/analytics/user-trends", "Get user trends"),
        ("GET", "/api/chatbot/health", "System health metrics"),
        ("WebSocket", "/api/chatbot/ws/{id}", "Real-time communication")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"   {method:10} {endpoint:35} - {description}")
    
    print("\n✨ Chatbot API demonstration complete!")
    print("\nKey Features Implemented:")
    print("  ✓ Session management with timeouts")
    print("  ✓ Question delivery and answer processing")
    print("  ✓ Real-time WebSocket communication")
    print("  ✓ Integration with existing MCQ generation")
    print("  ✓ Comprehensive analytics and reporting")
    print("  ✓ JWT authentication and authorization")
    print("  ✓ Rate limiting and abuse prevention")
    print("  ✓ Error handling and status reporting")


async def demonstrate_websocket_flow():
    """Demonstrate WebSocket message flow"""
    print("\n\n🔌 WebSocket Message Flow Demonstration")
    print("=" * 50)
    
    # Example WebSocket messages
    messages = [
        {
            "type": "connection_established",
            "session_id": "session_123",
            "timestamp": datetime.now().isoformat()
        },
        {
            "type": "question_delivered", 
            "session_id": "session_123",
            "data": {
                "question_id": "q1",
                "question": "What is Python?",
                "options": {"A": "Snake", "B": "Language", "C": "Car", "D": "Concept"}
            },
            "timestamp": datetime.now().isoformat()
        },
        {
            "type": "answer_result",
            "session_id": "session_123", 
            "data": {
                "is_correct": True,
                "points_earned": 1,
                "total_score": 1
            },
            "timestamp": datetime.now().isoformat()
        },
        {
            "type": "session_completed",
            "session_id": "session_123",
            "data": {
                "final_score": 3,
                "total_questions": 5,
                "accuracy": 60.0
            },
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    print("\nWebSocket Message Examples:")
    for i, message in enumerate(messages, 1):
        print(f"\n{i}. {message['type'].upper()}")
        print(f"   {json.dumps(message, indent=4)}")
    
    print("\nWebSocket Features:")
    print("  ✓ Real-time question delivery")
    print("  ✓ Live session status updates")
    print("  ✓ Session timeout notifications")
    print("  ✓ Connection heartbeat (ping/pong)")
    print("  ✓ Error reporting and recovery")


async def main():
    """Run the complete demonstration"""
    await demonstrate_chatbot_flow()
    await demonstrate_websocket_flow()


if __name__ == "__main__":
    asyncio.run(main())
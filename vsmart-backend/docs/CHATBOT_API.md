# Chatbot API Documentation

## Overview

The VSmart Chatbot API provides comprehensive endpoints for managing real-time skill assessment conversations. It integrates with the existing MCQ generation system to deliver personalized, interactive learning experiences.

## Features

- **Real-time Conversation Management**: WebSocket-powered live interactions
- **Session Persistence**: Firebase-based state management with automatic timeouts
- **MCQ Integration**: Leverages existing Gemini LLM for intelligent question generation
- **Analytics Dashboard**: Comprehensive performance tracking and user engagement metrics
- **Authentication**: JWT/Firebase-based secure communication
- **Rate Limiting**: Built-in protection against API abuse
- **Multi-skill Assessment**: Support for technical and soft skills evaluation

## Authentication

All chatbot endpoints require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <firebase_jwt_token>
```

## Session Lifecycle

### 1. Initialize Session
**POST** `/api/chatbot/session/init`

Creates a new assessment session and delivers the first question.

```json
{
  "skills": ["Python", "JavaScript"],
  "difficulty": "intermediate",
  "num_questions": 10,
  "session_timeout_minutes": 30,
  "question_timeout_seconds": 120,
  "language": "English"
}
```

**Response:**
```json
{
  "session_id": "uuid-session-id",
  "status": "active",
  "total_questions": 10,
  "current_question_index": 0,
  "skills": ["Python", "JavaScript"],
  "expires_at": "2024-07-19T21:00:00Z",
  "first_question": {
    "id": "q1",
    "type": "mcq",
    "content": "What is Python?",
    "options": [
      {"key": "A", "text": "A snake"},
      {"key": "B", "text": "A programming language"},
      {"key": "C", "text": "A type of car"},
      {"key": "D", "text": "A mathematical concept"}
    ],
    "skill": "Python",
    "difficulty": "intermediate",
    "points": 1,
    "time_limit_seconds": 120
  }
}
```

### 2. Submit Answer
**POST** `/api/chatbot/session/{session_id}/answer`

Submits an answer and receives feedback with the next question.

```json
{
  "session_id": "uuid-session-id",
  "question_id": "q1",
  "answer": "B",
  "time_taken_seconds": 45
}
```

**Response:**
```json
{
  "is_correct": true,
  "correct_answer": "B",
  "explanation": "Correct! Python is indeed a programming language.",
  "points_earned": 1,
  "total_score": 1,
  "next_question": {
    "id": "q2",
    "type": "mcq",
    "content": "Which framework is used for web development in Python?",
    "options": [
      {"key": "A", "text": "React"},
      {"key": "B", "text": "Django"},
      {"key": "C", "text": "Angular"},
      {"key": "D", "text": "Vue.js"}
    ],
    "skill": "Python",
    "difficulty": "intermediate",
    "points": 1
  },
  "session_completed": false
}
```

### 3. Session Management

#### Get Session Status
**GET** `/api/chatbot/session/{session_id}/status`

```json
{
  "session_id": "uuid-session-id",
  "status": "active",
  "current_question_index": 2,
  "total_questions": 10,
  "score": 1,
  "max_score": 10,
  "time_remaining_seconds": 1500,
  "skills_assessed": ["Python", "JavaScript"],
  "started_at": "2024-07-19T20:30:00Z",
  "expires_at": "2024-07-19T21:00:00Z"
}
```

#### Pause Session
**POST** `/api/chatbot/session/{session_id}/pause`

Temporarily pauses an active session.

#### Resume Session
**POST** `/api/chatbot/session/{session_id}/resume`

Resumes a paused session.

#### Cancel Session
**DELETE** `/api/chatbot/session/{session_id}`

Permanently cancels a session.

### 4. Conversation History
**GET** `/api/chatbot/session/{session_id}/history`

Retrieves the complete conversation transcript.

```json
{
  "session_id": "uuid-session-id",
  "messages": [
    {
      "id": "msg1",
      "type": "system",
      "content": "Welcome to your skill assessment!",
      "timestamp": "2024-07-19T20:30:00Z",
      "metadata": {"skills": ["Python"], "difficulty": "intermediate"}
    },
    {
      "id": "msg2",
      "type": "question",
      "content": "What is Python?",
      "timestamp": "2024-07-19T20:30:05Z",
      "metadata": {"question_id": "q1", "skill": "Python"}
    },
    {
      "id": "msg3",
      "type": "user_answer",
      "content": "B",
      "timestamp": "2024-07-19T20:30:50Z",
      "metadata": {"question_id": "q1", "is_correct": true}
    }
  ],
  "total_messages": 3
}
```

## WebSocket Real-time Communication

### Connection
**WebSocket** `/api/chatbot/ws/{session_id}`

Establishes real-time communication for live updates.

### Message Types

#### Connection Established
```json
{
  "type": "connection_established",
  "session_id": "uuid-session-id",
  "timestamp": "2024-07-19T20:30:00Z"
}
```

#### Question Delivered
```json
{
  "type": "question_delivered",
  "session_id": "uuid-session-id",
  "data": {
    "question_id": "q1",
    "question": "What is Python?",
    "options": {"A": "Snake", "B": "Language", "C": "Car", "D": "Concept"}
  },
  "timestamp": "2024-07-19T20:30:05Z"
}
```

#### Answer Result
```json
{
  "type": "answer_result",
  "session_id": "uuid-session-id",
  "data": {
    "is_correct": true,
    "points_earned": 1,
    "total_score": 1
  },
  "timestamp": "2024-07-19T20:30:50Z"
}
```

#### Session Status Update
```json
{
  "type": "session_paused",
  "session_id": "uuid-session-id",
  "data": {"status": "paused"},
  "timestamp": "2024-07-19T20:35:00Z"
}
```

#### Heartbeat
```json
{
  "type": "ping"
}
```

**Response:**
```json
{
  "type": "pong",
  "timestamp": "2024-07-19T20:30:00Z"
}
```

## Analytics

### Get Analytics Data
**POST** `/api/chatbot/analytics`

Retrieves comprehensive performance metrics.

```json
{
  "start_date": "2024-07-01T00:00:00Z",
  "end_date": "2024-07-31T23:59:59Z",
  "candidate_id": "user123",
  "skills": ["Python", "JavaScript"]
}
```

**Response:**
```json
{
  "total_sessions": 150,
  "completed_sessions": 127,
  "average_score": 78.5,
  "average_time_per_session": 1200.0,
  "skill_performance": {
    "Python": {
      "total_questions": 500,
      "correct_answers": 390,
      "accuracy_percentage": 78.0,
      "total_sessions": 75
    }
  },
  "popular_skills": [
    {"skill": "Python", "usage_count": 75},
    {"skill": "JavaScript", "usage_count": 65}
  ],
  "completion_rate": 84.7
}
```

### User Performance Trends
**GET** `/api/chatbot/analytics/user-trends?days=30`

Gets performance trends for the authenticated user.

```json
{
  "user_id": "user123",
  "period_days": 30,
  "daily_average_scores": {
    "2024-07-01": 75.0,
    "2024-07-02": 82.5,
    "2024-07-03": 78.0
  },
  "skill_progress": {
    "Python": [
      {"date": "2024-07-01", "score": 75.0},
      {"date": "2024-07-02", "score": 80.0}
    ]
  },
  "total_sessions": 15,
  "improvement_trend": "improving"
}
```

### System Health
**GET** `/api/chatbot/health`

Monitors system health and performance.

```json
{
  "active_sessions": 45,
  "sessions_last_24h": 120,
  "error_rate": 0.02,
  "average_response_time_seconds": 0.35,
  "system_status": "healthy",
  "last_updated": "2024-07-19T20:30:00Z"
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": "validation_error",
  "message": "Invalid input provided",
  "code": "E001",
  "details": {
    "field": "skills",
    "issue": "cannot be empty"
  }
}
```

### HTTP Status Codes

- **200 OK**: Successful request
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **404 Not Found**: Session or resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Rate Limiting

Rate limits are applied per user:
- Session initialization: 10 requests/minute
- Answer submission: 60 requests/minute
- General endpoints: 100 requests/minute

Rate limit response:
```json
{
  "message": "Rate limit exceeded",
  "retry_after_seconds": 60,
  "requests_remaining": 0,
  "reset_time": "2024-07-19T20:31:00Z"
}
```

## Integration Examples

### JavaScript/TypeScript Client

```typescript
// Initialize session
const response = await fetch('/api/chatbot/session/init', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    skills: ['Python', 'JavaScript'],
    difficulty: 'intermediate',
    num_questions: 10
  })
});

const session = await response.json();

// Connect WebSocket
const ws = new WebSocket(`ws://localhost:8000/api/chatbot/ws/${session.session_id}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

// Submit answer
const answerResponse = await fetch(`/api/chatbot/session/${session.session_id}/answer`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    session_id: session.session_id,
    question_id: 'q1',
    answer: 'B',
    time_taken_seconds: 45
  })
});
```

### Python Client

```python
import requests
import websocket
import json

# Initialize session
response = requests.post('/api/chatbot/session/init', 
  headers={'Authorization': f'Bearer {token}'},
  json={
    'skills': ['Python', 'JavaScript'],
    'difficulty': 'intermediate',
    'num_questions': 10
  }
)

session = response.json()

# WebSocket connection
def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")

ws = websocket.WebSocketApp(f"ws://localhost:8000/api/chatbot/ws/{session['session_id']}")
ws.on_message = on_message
ws.run_forever()
```

## Best Practices

1. **Session Management**: Always check session status before submitting answers
2. **Error Handling**: Implement proper error handling for network issues and API errors
3. **Rate Limiting**: Implement exponential backoff for rate-limited requests
4. **WebSocket Reconnection**: Handle WebSocket disconnections gracefully
5. **Security**: Never expose JWT tokens in client-side logs
6. **Performance**: Use WebSocket for real-time updates instead of polling
7. **Analytics**: Track user engagement for product improvement

## Supported Skills

The system supports assessment for:

**Technical Skills:**
- Python, JavaScript, Java, C++, React, Node.js
- Django, Flask, SQL, MongoDB, PostgreSQL
- Docker, Kubernetes, AWS, Azure
- Machine Learning, Data Science, DevOps
- System Design, Algorithms, Data Structures

**Soft Skills:**
- Communication, Leadership, Teamwork
- Problem Solving, Time Management
- Project Management, Critical Thinking
- Adaptability, Conflict Resolution

## Deployment Notes

- Requires Firebase authentication setup
- WebSocket support needs proper reverse proxy configuration
- Rate limiting requires Redis or in-memory storage
- Analytics data is stored in Firestore
- Session data persists across server restarts

## Support

For technical support or feature requests, please contact the development team or create an issue in the repository.
# MCQ Generation Engine

## Overview

The MCQ Generation Engine is an AI-powered system that automatically generates relevant multiple-choice questions for different skills, job roles, and difficulty levels using Google's Gemini LLM technology.

## Features

### Question Types
- **Technical Questions**: Programming concepts, frameworks, best practices
- **Soft Skills**: Communication, leadership, teamwork scenarios
- **Scenario-based**: Real workplace situations and decision-making
- **Code-based**: Code comprehension, debugging, output prediction

### Difficulty Levels
- **Beginner**: Basic concepts and simple scenarios
- **Intermediate**: Complex scenarios and best practices
- **Advanced**: System design, optimization, strategic thinking

### Additional Features
- Multi-language support (English, Spanish, etc.)
- Quality validation and duplicate detection
- Caching for improved performance
- Batch generation for multiple skills
- Comprehensive error handling and logging

## API Endpoints

### Generate MCQ Questions
```http
POST /api/mcq/generate
Content-Type: application/json

{
  "skill": "Python",
  "difficulty": "intermediate",
  "question_type": "technical",
  "num_questions": 5,
  "language": "English"
}
```

**Response:**
```json
{
  "questions": [
    {
      "id": "unique_question_id",
      "question": "What is the output of the following Python code?",
      "options": {
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      },
      "correct_answer": "A",
      "explanation": "Brief explanation",
      "difficulty": "intermediate",
      "skill": "Python",
      "type": "technical",
      "tags": ["python", "intermediate", "technical"],
      "generated_at": "2024-01-01T00:00:00"
    }
  ],
  "metadata": {
    "skill": "Python",
    "difficulty": "intermediate",
    "question_type": "technical",
    "language": "English",
    "total_questions": 5,
    "generated_at": "2024-01-01T00:00:00",
    "model_used": "gemini-2.5-flash-preview-04-17"
  }
}
```

### Validate Question Quality
```http
POST /api/mcq/validate
Content-Type: application/json

{
  "question": {
    "id": "test_id",
    "question": "What is Python?",
    "options": {
      "A": "A programming language",
      "B": "A snake",
      "C": "A tool",
      "D": "A framework"
    },
    "correct_answer": "A",
    "difficulty": "beginner",
    "skill": "Python",
    "type": "technical"
  }
}
```

### Detect Duplicate Questions
```http
POST /api/mcq/detect-duplicates
Content-Type: application/json

{
  "new_questions": [...],
  "existing_questions": [...]
}
```

### Get Supported Skills
```http
GET /api/mcq/supported-skills
```

### Batch Generate Questions
```http
GET /api/mcq/batch-generate?skills=Python,JavaScript&difficulty=intermediate&num_questions_per_skill=3
```

## Supported Skills

### Technical Skills
- Programming Languages: Python, JavaScript, Java, C++, Go, Rust
- Web Frameworks: React, Vue.js, Angular, Node.js, Django, Flask
- Databases: SQL, MongoDB, PostgreSQL, MySQL, Redis
- Cloud & DevOps: AWS, Azure, Docker, Kubernetes, CI/CD
- Data & AI: Machine Learning, Data Science, Analytics

### Soft Skills
- Communication and Presentation
- Leadership and Management
- Teamwork and Collaboration
- Problem Solving and Critical Thinking
- Time Management and Organization
- Conflict Resolution and Negotiation

## Usage Examples

### Basic Python Questions
```python
from services.mcq_generation import mcq_service

# Generate technical Python questions
result = await mcq_service.generate_mcqs(
    skill="Python",
    difficulty="intermediate", 
    question_type="technical",
    num_questions=5
)
```

### Soft Skills Assessment
```python
# Generate leadership scenario questions
result = await mcq_service.generate_mcqs(
    skill="Leadership",
    difficulty="advanced",
    question_type="scenario_based",
    num_questions=3
)
```

### Code-based Questions
```python
# Generate JavaScript code comprehension questions
result = await mcq_service.generate_mcqs(
    skill="JavaScript",
    difficulty="intermediate",
    question_type="code_based",
    num_questions=4
)
```

### Multi-language Support
```python
# Generate questions in Spanish
result = await mcq_service.generate_mcqs(
    skill="Python",
    difficulty="beginner",
    question_type="technical",
    num_questions=3,
    language="Spanish"
)
```

## Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash-preview-04-17
```

### Caching
The system uses in-memory caching by default with a 24-hour expiry. For production use, consider implementing Redis or database-backed caching.

## Quality Assurance

### Validation Features
- Question length validation (10-500 characters)
- Option diversity checks
- Correct answer validation
- Duplicate detection using Jaccard similarity

### Performance Optimization
- Intelligent caching to reduce API calls
- Batch processing support
- Configurable rate limiting
- Error recovery and retry mechanisms

## Integration

The MCQ Generation Engine integrates seamlessly with the existing VSmart backend:

1. **Gemini AI Integration**: Uses the same Gemini service configuration
2. **FastAPI Routes**: Follows existing API patterns and conventions
3. **Error Handling**: Consistent error responses and logging
4. **Schema Validation**: Pydantic models for request/response validation

## Testing

Run the test suite:
```bash
pytest tests/test_mcq_simplified.py -v
```

## Future Enhancements

- Database persistence for generated questions
- Advanced similarity detection using embeddings
- Question difficulty auto-adjustment based on performance
- Integration with candidate assessment workflows
- Analytics and reporting for question effectiveness
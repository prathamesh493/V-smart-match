"""
MCQ generation prompts for Gemini AI service.
"""

BASE_MCQ_PROMPT = """
You are an expert question designer specializing in creating high-quality multiple-choice questions for skills assessment and hiring.

Generate {num_questions} multiple-choice questions based on the following parameters:
- Skill/Topic: {skill}
- Difficulty Level: {difficulty} (beginner/intermediate/advanced)
- Language: {language}

Requirements:
1. Each question must have exactly 4 options (A, B, C, D)
2. Only ONE option should be correct
3. All options should be plausible to avoid obvious answers
4. Questions should be relevant to real-world scenarios
5. Avoid overly complex or trick questions
6. Ensure questions test understanding, not just memorization

Return the response as a valid JSON object with this exact structure:
{{
  "questions": [
    {{
      "id": "unique_question_id",
      "question": "Question text here",
      "options": {{
        "A": "Option A text",
        "B": "Option B text", 
        "C": "Option C text",
        "D": "Option D text"
      }},
      "correct_answer": "A",
      "explanation": "Brief explanation of why this answer is correct",
      "difficulty": "beginner|intermediate|advanced",
      "skill": "skill_name",
      "type": "question_type",
      "tags": ["tag1", "tag2"]
    }}
  ]
}}

Do NOT include any text before or after the JSON object.
"""

TECHNICAL_MCQ_PROMPT = """
You are an expert technical interviewer. Generate {num_questions} technical multiple-choice questions for {skill}.

Focus on:
- Practical programming concepts and best practices
- Real-world problem-solving scenarios
- Code comprehension and debugging
- Framework/technology-specific knowledge
- System design concepts (for advanced level)

For {difficulty} level:
- Beginner: Basic syntax, fundamental concepts, simple problem-solving
- Intermediate: Complex scenarios, optimization, debugging, best practices
- Advanced: System design, performance optimization, architecture decisions

{base_prompt}
"""

SOFT_SKILLS_MCQ_PROMPT = """
You are an expert HR professional. Generate {num_questions} soft skills multiple-choice questions for {skill}.

Focus on:
- Workplace scenarios and behavioral responses
- Communication and teamwork situations
- Leadership and decision-making
- Problem-solving approaches
- Professional ethics and best practices

For {difficulty} level:
- Beginner: Basic workplace etiquette, simple communication scenarios
- Intermediate: Complex team dynamics, conflict resolution, leadership scenarios
- Advanced: Strategic thinking, complex stakeholder management, organizational leadership

{base_prompt}
"""

SCENARIO_BASED_MCQ_PROMPT = """
You are an expert in workplace scenario assessment. Generate {num_questions} scenario-based multiple-choice questions for {skill}.

Focus on:
- Real workplace situations and challenges
- Decision-making under pressure
- Problem-solving with constraints
- Team collaboration scenarios
- Client/stakeholder interaction situations

Present realistic scenarios that a {skill} professional would encounter, then ask about the best course of action.

{base_prompt}
"""

CODE_BASED_MCQ_PROMPT = """
You are an expert coding interviewer. Generate {num_questions} code-based multiple-choice questions for {skill}.

Requirements:
- Include actual code snippets in questions
- Focus on code comprehension, debugging, or output prediction
- Use proper code formatting and syntax highlighting
- Questions should test practical coding knowledge

For {difficulty} level:
- Beginner: Simple code reading, basic syntax understanding
- Intermediate: Debugging, code optimization, algorithm understanding
- Advanced: Complex algorithms, system design code, performance analysis

Format code blocks using proper markdown syntax:
```{language}
code here
```

{base_prompt}
"""

def get_mcq_prompt(question_type: str, **kwargs) -> str:
    """
    Get the appropriate MCQ generation prompt based on question type.
    """
    base_params = {
        'base_prompt': BASE_MCQ_PROMPT,
        **kwargs
    }
    
    if question_type == 'technical':
        return TECHNICAL_MCQ_PROMPT.format(**base_params)
    elif question_type == 'soft_skills':
        return SOFT_SKILLS_MCQ_PROMPT.format(**base_params)
    elif question_type == 'scenario_based':
        return SCENARIO_BASED_MCQ_PROMPT.format(**base_params)
    elif question_type == 'code_based':
        return CODE_BASED_MCQ_PROMPT.format(**base_params)
    else:
        return BASE_MCQ_PROMPT.format(**base_params)
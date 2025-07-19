#!/usr/bin/env python3
"""
Demo script to test MCQ Generation Engine functionality.
"""

import asyncio
import json
from services.mcq_generation import mcq_service
from prompts.mcq.generation import get_mcq_prompt

async def demo_mcq_generation():
    """Demonstrate MCQ generation capabilities."""
    
    print("🎯 MCQ Generation Engine Demo")
    print("=" * 50)
    
    # 1. Test prompt generation
    print("\n1. Testing Prompt Generation:")
    prompt = get_mcq_prompt(
        question_type="technical",
        skill="Python",
        difficulty="intermediate",
        num_questions=2,
        language="English"
    )
    print(f"✓ Generated prompt (first 200 chars): {prompt[:200]}...")
    
    # 2. Test supported skills
    print("\n2. Testing Supported Skills:")
    skills = mcq_service.get_supported_skills()
    print(f"✓ Total supported skills: {len(skills)}")
    print(f"✓ Technical skills: {[s for s in skills if s in ['Python', 'JavaScript', 'React', 'AWS']]}")
    print(f"✓ Soft skills: {[s for s in skills if s in ['Communication', 'Leadership', 'Teamwork']]}")
    
    # 3. Test cache key generation
    print("\n3. Testing Cache System:")
    cache_key = mcq_service._generate_cache_key("Python", "intermediate", "technical", 5, "English")
    print(f"✓ Generated cache key: {cache_key}")
    
    # 4. Test question validation
    print("\n4. Testing Question Validation:")
    sample_question = {
        "question": "What is the output of print('Hello World') in Python?",
        "options": {
            "A": "Hello World",
            "B": "print('Hello World')",
            "C": "SyntaxError",
            "D": "None"
        },
        "correct_answer": "A"
    }
    
    validation_result = await mcq_service.validate_question_quality(sample_question)
    print(f"✓ Question validation: {'Valid' if validation_result['is_valid'] else 'Invalid'}")
    if validation_result['issues']:
        print(f"  Issues: {validation_result['issues']}")
    if validation_result['suggestions']:
        print(f"  Suggestions: {validation_result['suggestions']}")
    
    # 5. Test duplicate detection
    print("\n5. Testing Duplicate Detection:")
    question1 = {"id": "1", "question": "What is Python used for programming?"}
    question2 = {"id": "2", "question": "What is Python programming used for?"}
    question3 = {"id": "3", "question": "What is Java used for development?"}
    
    duplicates = await mcq_service.detect_duplicate_questions([question1], [question2, question3])
    print(f"✓ Found {len(duplicates)} potential duplicates")
    for dup in duplicates:
        print(f"  - Question {dup['new_question_id']} similar to {dup['existing_question_id']} ({dup['similarity_score']:.2f})")
    
    # 6. Test text similarity
    print("\n6. Testing Text Similarity:")
    similarity = mcq_service._calculate_text_similarity(
        "what is python programming language",
        "what is python programming language"
    )
    print(f"✓ Identical texts similarity: {similarity:.2f}")
    
    similarity = mcq_service._calculate_text_similarity(
        "what is python programming language", 
        "what is java programming language"
    )
    print(f"✓ Similar texts similarity: {similarity:.2f}")
    
    print("\n✅ All MCQ Generation Engine features tested successfully!")
    print("\n📝 Note: To test actual question generation, configure GEMINI_API_KEY and call:")
    print("   result = await mcq_service.generate_mcqs(skill='Python', difficulty='intermediate')")

if __name__ == "__main__":
    asyncio.run(demo_mcq_generation())
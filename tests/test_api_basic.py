"""
Test the API endpoints without dependencies.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys

# Mock problematic imports
sys.modules['services.embedding'] = MagicMock()
sys.modules['services.pinecone_service'] = MagicMock()
sys.modules['services.firebase'] = MagicMock()
sys.modules['services.firestore'] = MagicMock()

# Mock the Gemini client to avoid API calls
with patch('google.generativeai.configure'):
    with patch('google.generativeai.GenerativeModel'):
        from fastapi.testclient import TestClient
        from app.main import app

client = TestClient(app)

def test_mcq_supported_skills_endpoint():
    """Test that the supported skills endpoint works."""
    response = client.get("/api/mcq/supported-skills")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert "total_skills" in data
    assert isinstance(data["skills"], list)
    assert len(data["skills"]) > 0

def test_mcq_generate_endpoint_validation():
    """Test MCQ generation endpoint validation."""
    # Test invalid request
    response = client.post(
        "/api/mcq/generate",
        json={
            "skill": "",  # Empty skill should fail validation
            "difficulty": "beginner"
        }
    )
    assert response.status_code == 422  # Validation error

def test_health_endpoint():
    """Test that the health endpoint still works."""
    response = client.get("/api/health")
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])
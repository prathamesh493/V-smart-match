from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SkillMatch(BaseModel):
    skill: str
    relevance: float = Field(..., ge=0, le=100)

class MissingSkill(BaseModel):
    skill: str
    importance: float = Field(..., ge=0, le=100)

class SkillsMatchScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=100)
    key_matches: List[SkillMatch] = Field(..., alias="keyMatches")
    missing_critical_skills: List[MissingSkill] = Field(..., alias="missingCriticalSkills")

class ExperienceMatchScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=100)
    years_experience_match: float = Field(..., ge=0, le=100, alias="yearsExperienceMatch")
    domain_experience_match: float = Field(..., ge=0, le=100, alias="domainExperienceMatch")
    role_alignment_match: float = Field(..., ge=0, le=100, alias="roleAlignmentMatch")

class EducationMatchScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=100)
    degree_match: float = Field(..., ge=0, le=100, alias="degreeMatch")
    field_match: float = Field(..., ge=0, le=100, alias="fieldMatch")
    certifications_match: float = Field(..., ge=0, le=100, alias="certificationsMatch")

class SoftSkillsMatchScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=100)
    key_matches: List[SkillMatch] = Field(..., alias="keyMatches")

class CulturalFitMatchScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=100)
    value_alignment_score: float = Field(..., ge=0, le=100, alias="valueAlignmentScore")
    work_style_match: float = Field(..., ge=0, le=100, alias="workStyleMatch")

class CategoryScores(BaseModel):
    skills_match: Optional[SkillsMatchScore] = Field(None, alias="skillsMatch")
    skillsMatch: Optional[Dict[str, Any]] = None
    experience_match: Optional[ExperienceMatchScore] = Field(None, alias="experienceMatch")
    experienceMatch: Optional[Dict[str, Any]] = None
    education_match: Optional[EducationMatchScore] = Field(None, alias="educationMatch")
    educationMatch: Optional[Dict[str, Any]] = None
    soft_skills_match: Optional[SoftSkillsMatchScore] = Field(None, alias="softSkillsMatch")
    softSkillsMatch: Optional[Dict[str, Any]] = None
    cultural_fit_match: Optional[CulturalFitMatchScore] = Field(None, alias="culturalFitMatch")
    culturalFitMatch: Optional[Dict[str, Any]] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class Analysis(BaseModel):
    summary: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class MetadataModel(BaseModel):
    model_version: Optional[str] = Field(None, alias="modelVersion")
    modelVersion: Optional[str] = None
    processing_time: Optional[int] = Field(None, alias="processingTime")
    processingTime: Optional[int] = None
    prompt_tokens: Optional[int] = Field(None, alias="promptTokens")
    promptTokens: Optional[int] = None
    completion_tokens: Optional[int] = Field(None, alias="completionTokens")
    completionTokens: Optional[int] = None
    
    class Config:
        allow_population_by_field_name = True

class MatchResult(BaseModel):
    match_id: Optional[str] = Field(None, alias="matchId")
    matchId: Optional[str] = None
    candidate_id: Optional[str] = Field(None, alias="candidateId")
    candidateId: Optional[str] = None
    job_description_id: Optional[str] = Field(None, alias="jobDescriptionId")
    jobDescriptionId: Optional[str] = None
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    createdAt: Optional[str] = None
    overall_score: Optional[float] = Field(None, ge=0, le=100, alias="overallScore")
    overallScore: Optional[float] = None
    category_scores: Optional[CategoryScores] = Field(None, alias="categoryScores")
    categoryScores: Optional[Dict[str, Any]] = None
    analysis: Optional[Analysis] = None
    metadata: Optional[MetadataModel] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        
    @classmethod
    def parse_obj(cls, obj):
        # Handle both snake_case and camelCase field names
        if isinstance(obj, dict):
            # Map camelCase fields to snake_case fields if they exist
            if "matchId" in obj and "match_id" not in obj:
                obj["match_id"] = obj["matchId"]
            if "candidateId" in obj and "candidate_id" not in obj:
                obj["candidate_id"] = obj["candidateId"]
            if "jobDescriptionId" in obj and "job_description_id" not in obj:
                obj["job_description_id"] = obj["jobDescriptionId"]
            if "createdAt" in obj and "created_at" not in obj:
                obj["created_at"] = obj["createdAt"]
            if "overallScore" in obj and "overall_score" not in obj:
                obj["overall_score"] = obj["overallScore"]
            if "categoryScores" in obj and "category_scores" not in obj:
                obj["category_scores"] = obj["categoryScores"]
        return super().parse_obj(obj)
        schema_extra = {
            "example": {
                "matchId": "match_abc123",
                "candidateId": "candidate_123",
                "jobDescriptionId": "jd_456",
                "createdAt": "2025-05-02T14:30:00.123456",
                "overallScore": 82,
                "categoryScores": {
                    "skillsMatch": {
                        "score": 85,
                        "confidence": 90,
                        "keyMatches": [
                            {"skill": "Python", "relevance": 95},
                            {"skill": "React", "relevance": 80},
                            {"skill": "REST APIs", "relevance": 85}
                        ],
                        "missingCriticalSkills": [
                            {"skill": "AWS", "importance": 75},
                            {"skill": "GraphQL", "importance": 60}
                        ]
                    },
                    "experienceMatch": {
                        "score": 80,
                        "confidence": 85,
                        "yearsExperienceMatch": 90,
                        "domainExperienceMatch": 70,
                        "roleAlignmentMatch": 85
                    },
                    "educationMatch": {
                        "score": 90,
                        "confidence": 95,
                        "degreeMatch": 100,
                        "fieldMatch": 90,
                        "certificationsMatch": 70
                    },
                    "softSkillsMatch": {
                        "score": 75,
                        "confidence": 70,
                        "keyMatches": [
                            {"skill": "Communication", "relevance": 80},
                            {"skill": "Problem-solving", "relevance": 85}
                        ]
                    },
                    "culturalFitMatch": {
                        "score": 80,
                        "confidence": 75,
                        "valueAlignmentScore": 85,
                        "workStyleMatch": 75
                    }
                },
                "analysis": {
                    "summary": "Strong technical match with excellent education background. Some gaps in cloud experience.",
                    "strengths": [
                        "Strong programming skills with Python and React",
                        "Relevant degree in Computer Science",
                        "Good experience level for the role"
                    ],
                    "weaknesses": [
                        "Missing experience with AWS",
                        "Limited domain experience in finance sector"
                    ],
                    "recommendations": [
                        "Proceed to technical interview",
                        "Assess cloud knowledge during interview",
                        "Inquire about willingness to learn financial domain"
                    ]
                },
                "metadata": {
                    "modelVersion": "gemini-2.5-pro-preview-03-25",
                    "processingTime": 2134,
                    "promptTokens": 3250,
                    "completionTokens": 1450
                }
            }
        }

# Request models
class CreateMatchRequest(BaseModel):
    candidate_id: str = Field(..., alias="candidateId")
    job_description_id: str = Field(..., alias="jobDescriptionId")
    
    class Config:
        allow_population_by_field_name = True

class BulkMatchRequest(BaseModel):
    candidate_ids: List[str] = Field(..., alias="candidateIds")
    job_description_ids: List[str] = Field(..., alias="jobDescriptionIds")
    
    class Config:
        allow_population_by_field_name = True
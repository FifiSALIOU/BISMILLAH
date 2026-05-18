from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.enums import Provider, ContentType


class QuestionRequest(BaseModel):
    question: str
    provider: Optional[Provider] = Provider.OPENAI
    model: Optional[str] = None
    temperature: Optional[float] = 0.3
    max_tokens: Optional[int] = 512
    top_k: Optional[int] = 3


class AdvancedQuestionResponse(BaseModel):
    id: str
    answer: str
    context_found: bool
    provider_used: str
    model_used: str
    response_time_ms: float
    timestamp: str
    search_results: int
    ranked_results: int
    enhanced_queries: List[str]
    sources: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]


class DocumentResponse(BaseModel):
    document_id: str
    chunks_created: int
    processing_time_ms: float
    status: str


class PerformanceMetrics(BaseModel):
    total_queries: int
    average_response_time_ms: float
    cache_hit_rate: float
    error_rate: float
    active_documents: int


class MultimodalUploadRequest(BaseModel):
    file_type: str = Field(..., description="Type de fichier: 'document', 'image', 'mixed'")
    extract_text_from_images: bool = Field(True, description="Extraire le texte des images (OCR)")
    generate_captions: bool = Field(True, description="Générer des descriptions d'images")


class MultimodalQuestionRequest(QuestionRequest):
    content_types: Optional[List[ContentType]] = Field(
        default=[ContentType.DOCUMENT, ContentType.IMAGE],
        description="Types de contenu à rechercher"
    )
    include_images: bool = Field(True, description="Inclure les résultats d'images")
    multimodal_boost: float = Field(0.1, description="Boost pour les résultats multimodaux")


class SatisfactionRequest(BaseModel):
    response_id: str = Field(..., description="ID de la réponse à évaluer")
    is_satisfied: bool = Field(..., description="Satisfaction de l'utilisateur (True/False)")


class SatisfactionResponse(BaseModel):
    satisfaction_id: str
    response_id: str
    question: str
    response: str
    is_satisfied: bool
    timestamp: str
    status: str

class QuestionStats(BaseModel):
    question: str
    count: int
    percentage: float

class CategoryStats(BaseModel):
    categorie: str
    count: int
    percentage: float

class DailyStats(BaseModel):
    date: str
    count: int

class KeywordStats(BaseModel):
    keyword: str
    count: int

class GeneralStats(BaseModel):
    total_questions: int
    unique_questions: int
    date_debut: str
    date_fin: str
    moyenne_par_jour: float

class StatisticsResponse(BaseModel):
    general_stats: GeneralStats
    top_questions: List[QuestionStats]
    categories: List[CategoryStats]
    daily_evolution: List[DailyStats]
    top_keywords: List[KeywordStats]
    models_distribution: Dict[str, int] 
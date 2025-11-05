from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for better type safety
class DocumentType(str, Enum):
    MANUAL = "manual"
    FAQ = "faq" 
    GUIDE = "guide"
    ERROR_CODE = "error_code"
    SOP = "sop"
    TRAINING = "training"

class IndustryType(str, Enum):
    PHARMACY = "pharmacy"
    AUTO_PARTS = "auto_parts"
    FMCG = "fmcg"
    GROCERY = "grocery"
    RESTAURANT = "restaurant"
    GENERAL = "general"

class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"

# Document Schemas
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=10)
    document_type: DocumentType
    industry_type: Optional[IndustryType] = IndustryType.GENERAL
    language: Language = Language.ENGLISH
    file_path: Optional[str] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    document_type: Optional[DocumentType] = None
    industry_type: Optional[IndustryType] = None
    language: Optional[Language] = None
    is_active: Optional[bool] = None

class DocumentResponse(BaseModel):
    id: str  # Changed from int to str for UUID support
    title: str
    content: str
    document_type: str
    industry_type: Optional[str]
    language: str
    file_path: Optional[str]
    file_size: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    chunk_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

# Document Chunk Schemas
class DocumentChunkCreate(BaseModel):
    document_id: int
    chunk_text: str = Field(..., min_length=10)
    chunk_index: int = Field(..., ge=0)
    section_title: Optional[str] = None
    keywords: Optional[str] = None

class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_text: str
    chunk_index: int
    chunk_size: int
    overlap_with_previous: int
    embedding_id: Optional[str]
    embedding_created: bool
    keywords: Optional[str]
    section_title: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Document Upload Schema
class DocumentUploadRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    document_type: DocumentType
    industry_type: Optional[IndustryType] = IndustryType.GENERAL
    language: Language = Language.ENGLISH
    
    # Chunking parameters
    chunk_size: Optional[int] = Field(1000, ge=100, le=4000)
    chunk_overlap: Optional[int] = Field(200, ge=0, le=1000)
    auto_generate_keywords: Optional[bool] = True

class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document: DocumentResponse
    chunks_created: int
    processing_time_ms: int

# Search and Retrieval Schemas
class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    document_types: Optional[List[DocumentType]] = None
    industry_types: Optional[List[IndustryType]] = None
    language: Optional[Language] = None
    limit: Optional[int] = Field(5, ge=1, le=50)
    min_confidence: Optional[float] = Field(0.0, ge=0.0, le=1.0)

class SearchResult(BaseModel):
    chunk_id: str  # Changed from int to str for UUID support
    document_id: str  # Changed from int to str for UUID support
    document_title: str
    chunk_text: str
    chunk_index: int
    section_title: Optional[str]
    confidence_score: float
    keywords: Optional[str]
    document_type: str
    industry_type: Optional[str]

class DocumentSearchResponse(BaseModel):
    success: bool
    message: str
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: int
    
# Bulk Operations
class BulkDocumentResponse(BaseModel):
    success: bool
    message: str
    documents: List[DocumentResponse]
    total_count: int
    
class DocumentAnalytics(BaseModel):
    total_documents: int
    documents_by_type: Dict[str, int]
    documents_by_industry: Dict[str, int]
    documents_by_language: Dict[str, int]
    total_chunks: int
    average_chunks_per_doc: float
    total_queries_today: int
    popular_search_terms: List[str]

# Knowledge Base Query Schema
class KnowledgeQueryCreate(BaseModel):
    query_text: str = Field(..., min_length=1, max_length=1000)
    query_language: Language = Language.ENGLISH
    user_id: Optional[int] = None
    session_id: Optional[int] = None

class KnowledgeQueryResponse(BaseModel):
    id: int
    query_text: str
    query_language: str
    chunks_retrieved: int
    search_time_ms: Optional[int]
    response_generated: bool
    response_time_ms: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# File Upload Helper Schema
class FileUploadInfo(BaseModel):
    filename: str
    content_type: str
    file_size: int
    supported_types: List[str] = ["text/plain", "application/pdf", "text/markdown"]
    
    @validator('content_type')
    def validate_content_type(cls, v):
        supported = ["text/plain", "application/pdf", "text/markdown", "text/html"]
        if v not in supported:
            raise ValueError(f'Content type {v} not supported. Supported types: {supported}')
        return v
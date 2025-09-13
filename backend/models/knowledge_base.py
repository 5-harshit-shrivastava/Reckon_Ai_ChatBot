from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    document_type = Column(String(50), nullable=False)  # manual, faq, guide, error_code
    industry_type = Column(String(50), nullable=True)  # pharmacy, auto_parts, fmcg, etc.
    language = Column(String(10), default="en")  # en, hi
    file_path = Column(String(500), nullable=True)  # original file path
    file_size = Column(Integer, nullable=True)  # file size in bytes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', type='{self.document_type}')>"

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # order within the document
    chunk_size = Column(Integer, nullable=False)  # number of characters
    overlap_with_previous = Column(Integer, default=0)  # characters overlapping with previous chunk
    
    # Vector/embedding info (will be used with vector DB)
    embedding_id = Column(String(255), nullable=True)  # ID in vector database
    embedding_created = Column(Boolean, default=False)
    
    # Metadata for better search
    keywords = Column(Text, nullable=True)  # comma-separated keywords
    section_title = Column(String(255), nullable=True)  # section/chapter title
    confidence_score = Column(Float, nullable=True)  # quality score of chunk
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>"

class KnowledgeBaseQuery(Base):
    __tablename__ = "kb_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    
    query_text = Column(Text, nullable=False)
    query_language = Column(String(10), default="en")
    
    # Search results
    chunks_retrieved = Column(Integer, default=0)
    top_chunk_ids = Column(Text, nullable=True)  # JSON array of chunk IDs
    search_time_ms = Column(Integer, nullable=True)
    
    # Response generation
    response_generated = Column(Boolean, default=False)
    response_time_ms = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<KnowledgeBaseQuery(id={self.id}, user_id={self.user_id})>"


from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base
import uuid

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    channel = Column(String(50), default="web")  # web, mobile, whatsapp
    language = Column(String(10), default="en")  # en, hi
    is_active = Column(Boolean, default=True)
    session_metadata = Column(Text, nullable=True)  # JSON string for session data like user names
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    messages = relationship("ChatMessage", back_populates="session")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}', user_id={self.user_id})>"

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    message_type = Column(String(20), nullable=False)  # user, assistant, system
    message_text = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)  # billing, order_status, technical_support, etc.
    confidence_score = Column(Float, nullable=True)  # AI confidence level (0.0 to 1.0)
    escalated_to_human = Column(Boolean, default=False)
    response_time_ms = Column(Integer, nullable=True)  # Response time in milliseconds
    message_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, type='{self.message_type}', session_id={self.session_id})>"
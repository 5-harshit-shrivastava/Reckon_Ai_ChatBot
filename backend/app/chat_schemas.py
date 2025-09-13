from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json

# Enums for better type safety
class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatChannel(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    WHATSAPP = "whatsapp"

class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"

# Chat Session Schemas
class ChatSessionCreate(BaseModel):
    user_id: int
    channel: ChatChannel = ChatChannel.WEB
    language: Language = Language.ENGLISH

class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    session_id: str
    channel: str
    language: str
    is_active: bool
    created_at: datetime
    ended_at: Optional[datetime] = None
    message_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

# Chat Message Schemas
class ChatMessageCreate(BaseModel):
    session_id: int
    message_text: str
    message_type: MessageType = MessageType.USER
    intent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('metadata', pre=True)
    def serialize_metadata(cls, v):
        if v is not None and isinstance(v, dict):
            return json.dumps(v)
        return v

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    message_type: str
    message_text: str
    intent: Optional[str] = None
    confidence_score: Optional[float] = None
    escalated_to_human: bool = False
    response_time_ms: Optional[int] = None
    message_metadata: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @property
    def metadata_dict(self) -> Optional[Dict[str, Any]]:
        """Convert message_metadata JSON string to dict"""
        if self.message_metadata:
            try:
                return json.loads(self.message_metadata)
            except json.JSONDecodeError:
                return None
        return None

# Chat Conversation Schema (Session + Messages)
class ChatConversationResponse(BaseModel):
    session: ChatSessionResponse
    messages: List[ChatMessageResponse] = []
    total_messages: int = 0

# Chat API Request/Response Schemas
class SendMessageRequest(BaseModel):
    session_id: int
    message: str
    user_id: Optional[int] = None
    channel: ChatChannel = ChatChannel.WEB
    language: Language = Language.ENGLISH

class SendMessageResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]
    user_message: ChatMessageResponse
    assistant_response: Optional[ChatMessageResponse] = None
    session_info: ChatSessionResponse

# Chat Session Update Schema
class ChatSessionUpdate(BaseModel):
    is_active: Optional[bool] = None
    language: Optional[Language] = None
    ended_at: Optional[datetime] = None

# Bulk Operations
class BulkMessageResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]
    messages: List[ChatMessageResponse] = []
    pagination: Optional[Dict[str, Any]] = None

# Chat Analytics Schema
class ChatSessionAnalytics(BaseModel):
    session_id: int
    total_messages: int
    user_messages: int
    assistant_messages: int
    average_response_time: Optional[float] = None
    session_duration_minutes: Optional[float] = None
    intents_detected: List[str] = []
    escalated_to_human: bool = False
    satisfaction_score: Optional[float] = None
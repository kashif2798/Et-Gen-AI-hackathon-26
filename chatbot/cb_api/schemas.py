"""
Pydantic schemas for chatbot API and data models
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class QAPair(BaseModel):
    """
    Represents a single Question-Answer pair from q&a.md
    """
    id: str = Field(..., description="Unique identifier (e.g., 'qa_001')")
    question: str = Field(..., description="The question text")
    answer: str = Field(..., description="The answer text")
    category: str = Field(..., description="Category/topic of the Q&A")
    category_number: int = Field(..., description="Category number (1-5)")
    question_number: int = Field(..., description="Question number within category")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "qa_001",
                "question": "How does the latest RBI repo rate hike affect my home loan EMI?",
                "answer": "A repo rate hike increases the cost at which banks borrow...",
                "category": "Personalized Market Impact",
                "category_number": 1,
                "question_number": 1,
                "keywords": ["RBI", "repo rate", "home loan", "EMI"],
                "metadata": {"length": 150}
            }
        }


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint
    """
    session_id: str = Field(..., description="Unique session identifier")
    user_message: str = Field(..., description="User's message/question")
    user_profile: Optional[Dict] = Field(None, description="Optional user profile data")
    article_text: Optional[str] = Field(None, description="Optional text of the active article")


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint
    """
    session_id: str
    ai_reply: str
    sources: List[QAPair] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict = Field(default_factory=dict)


class Message(BaseModel):
    """
    Represents a single message in conversation history
    """
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatHistory(BaseModel):
    """
    Conversation history for a session
    """
    session_id: str
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

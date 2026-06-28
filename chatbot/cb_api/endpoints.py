"""
FastAPI Endpoints for Chatbot

Provides REST API for chat functionality.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.schemas import ChatRequest, ChatResponse, ChatHistory, Message
from engine.chat_engine import ChatEngine
from utils.config import ChatbotConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ET Nexus Chatbot API",
    description="Conversational RAG chatbot for financial Q&A",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chat engine (singleton)
chat_engine = None


def get_chat_engine() -> ChatEngine:
    """Get or create chat engine instance"""
    global chat_engine
    if chat_engine is None:
        logger.info("Initializing chat engine...")
        chat_engine = ChatEngine()
        logger.info("Chat engine initialized")
    return chat_engine


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting ET Nexus Chatbot API...")
    get_chat_engine()
    logger.info("API ready to serve requests")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ET Nexus Chatbot API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status of the service
    """
    engine = get_chat_engine()
    
    # Get memory stats
    memory_stats = engine.memory.get_stats()
    
    # Get model info
    model_info = engine.llm.get_model_info()
    
    return {
        "status": "healthy",
        "service": "chatbot",
        "components": {
            "chat_engine": "operational",
            "memory_manager": "operational",
            "llm_client": "operational" if model_info["api_available"] else "mock_mode",
            "retriever": "operational"
        },
        "stats": {
            "active_sessions": memory_stats["total_sessions"],
            "total_messages": memory_stats["total_messages"],
            "model": model_info["model"]
        },
        "config": {
            "max_history": ChatbotConfig.MAX_HISTORY_MESSAGES,
            "max_retrieval": ChatbotConfig.MAX_RETRIEVAL_RESULTS,
            "content_filter": ChatbotConfig.ENABLE_CONTENT_FILTER
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    
    Args:
        request: ChatRequest with session_id and user_message
        
    Returns:
        ChatResponse with AI reply and sources
        
    Raises:
        HTTPException: If chat processing fails
    """
    try:
        logger.info(f"Chat request from session {request.session_id}")
        
        # Validate request
        if not request.user_message or not request.user_message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_message cannot be empty"
            )
        
        if not request.session_id or not request.session_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id cannot be empty"
            )
        
        # Get chat engine
        engine = get_chat_engine()
        
        # Process chat
        response = engine.chat(
            user_message=request.user_message,
            session_id=request.session_id,
            user_profile=request.user_profile
        )
        
        logger.info(f"Chat response generated for session {request.session_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )


@app.get("/chat/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(session_id: str, limit: int = None):
    """
    Get conversation history for a session
    
    Args:
        session_id: Session identifier
        limit: Maximum messages to return (optional)
        
    Returns:
        ChatHistory with messages
        
    Raises:
        HTTPException: If session not found
    """
    try:
        engine = get_chat_engine()
        
        # Get session info
        session_info = engine.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Get messages
        messages = engine.memory.get_history(session_id, limit=limit)
        
        # Build response
        history = ChatHistory(
            session_id=session_id,
            messages=messages,
            created_at=engine.memory.sessions[session_id].created_at,
            last_updated=engine.memory.sessions[session_id].last_updated
        )
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting history: {str(e)}"
        )


@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear conversation history for a session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If session not found
    """
    try:
        engine = get_chat_engine()
        
        # Clear session
        cleared = engine.clear_session(session_id)
        
        if not cleared:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return {
            "status": "success",
            "message": f"Session {session_id} cleared",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing session: {str(e)}"
        )


@app.get("/chat/sessions")
async def list_sessions():
    """
    List all active sessions
    
    Returns:
        List of active session IDs with info
    """
    try:
        engine = get_chat_engine()
        
        # Get active sessions
        session_ids = engine.memory.get_active_sessions()
        
        # Get info for each session
        sessions = []
        for session_id in session_ids:
            info = engine.get_session_info(session_id)
            if info:
                sessions.append(info)
        
        return {
            "total_sessions": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing sessions: {str(e)}"
        )


@app.post("/chat/cleanup")
async def cleanup_old_sessions(max_age_hours: int = None):
    """
    Cleanup old sessions
    
    Args:
        max_age_hours: Maximum session age in hours (default: 24)
        
    Returns:
        Number of sessions cleaned up
    """
    try:
        engine = get_chat_engine()
        
        # Cleanup
        removed = engine.memory.cleanup_old_sessions(max_age_hours)
        
        return {
            "status": "success",
            "sessions_removed": removed,
            "max_age_hours": max_age_hours or ChatbotConfig.SESSION_TIMEOUT_HOURS
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning up sessions: {str(e)}"
        )


@app.get("/stats")
async def get_stats():
    """
    Get chatbot statistics
    
    Returns:
        Statistics about chatbot usage
    """
    try:
        engine = get_chat_engine()
        
        # Get memory stats
        memory_stats = engine.memory.get_stats()
        
        # Get model info
        model_info = engine.llm.get_model_info()
        
        return {
            "memory": memory_stats,
            "model": model_info,
            "config": {
                "max_history_messages": ChatbotConfig.MAX_HISTORY_MESSAGES,
                "max_retrieval_results": ChatbotConfig.MAX_RETRIEVAL_RESULTS,
                "relevance_threshold": ChatbotConfig.RELEVANCE_THRESHOLD,
                "session_timeout_hours": ChatbotConfig.SESSION_TIMEOUT_HOURS,
                "content_filter_enabled": ChatbotConfig.ENABLE_CONTENT_FILTER
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

"""
Memory Manager for Conversation History

Manages conversation history per session with in-memory storage.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import sys

from ..cb_api.schemas import Message, ChatHistory
from ..cb_utils.config import ChatbotConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages conversation history per session
    """
    
    def __init__(self, max_history: Optional[int] = None):
        """
        Initialize memory manager
        
        Args:
            max_history: Maximum messages to keep per session
        """
        self.max_history = max_history or ChatbotConfig.MAX_HISTORY_MESSAGES
        self.sessions: Dict[str, ChatHistory] = {}
        
        logger.info(f"Memory manager initialized (max_history: {self.max_history})")
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> Message:
        """
        Add message to conversation history
        
        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            Created message
        """
        # Create session if doesn't exist
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatHistory(
                session_id=session_id,
                messages=[],
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
        
        # Create message
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        # Add to session
        self.sessions[session_id].messages.append(message)
        self.sessions[session_id].last_updated = datetime.now()
        
        # Trim if exceeds max history
        if len(self.sessions[session_id].messages) > self.max_history:
            # Keep most recent messages
            self.sessions[session_id].messages = \
                self.sessions[session_id].messages[-self.max_history:]
        
        logger.debug(f"Added {role} message to session {session_id}")
        
        return message
    
    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get conversation history for session
        
        Args:
            session_id: Session identifier
            limit: Maximum messages to return (most recent)
            
        Returns:
            List of messages
        """
        if session_id not in self.sessions:
            return []
        
        messages = self.sessions[session_id].messages
        
        if limit:
            return messages[-limit:]
        
        return messages
    
    def get_history_text(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> str:
        """
        Get conversation history as formatted text
        
        Args:
            session_id: Session identifier
            limit: Maximum messages to return
            
        Returns:
            Formatted conversation history
        """
        messages = self.get_history(session_id, limit)
        
        if not messages:
            return ""
        
        history_lines = []
        for msg in messages:
            role_label = "User" if msg.role == "user" else "Assistant"
            history_lines.append(f"{role_label}: {msg.content}")
        
        return "\n".join(history_lines)
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear conversation history for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session existed and was cleared
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
            return True
        
        return False
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of active session IDs
        
        Returns:
            List of session IDs
        """
        return list(self.sessions.keys())
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get information about a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information dictionary
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "message_count": len(session.messages),
            "created_at": session.created_at.isoformat(),
            "last_updated": session.last_updated.isoformat(),
            "age_minutes": (datetime.now() - session.created_at).total_seconds() / 60
        }
    
    def cleanup_old_sessions(
        self,
        max_age_hours: Optional[int] = None
    ) -> int:
        """
        Remove sessions older than max_age_hours
        
        Args:
            max_age_hours: Maximum session age in hours
            
        Returns:
            Number of sessions removed
        """
        max_age_hours = max_age_hours or ChatbotConfig.SESSION_TIMEOUT_HOURS
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            if session.last_updated < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
        
        return len(sessions_to_remove)
    
    def get_stats(self) -> Dict:
        """
        Get memory manager statistics
        
        Returns:
            Statistics dictionary
        """
        total_messages = sum(
            len(session.messages) 
            for session in self.sessions.values()
        )
        
        return {
            "total_sessions": len(self.sessions),
            "total_messages": total_messages,
            "avg_messages_per_session": (
                total_messages / len(self.sessions) 
                if self.sessions else 0
            ),
            "max_history": self.max_history
        }


if __name__ == "__main__":
    # Test memory manager
    manager = MemoryManager()
    
    print("Testing Memory Manager")
    print("=" * 60)
    
    # Test session 1
    session1 = "test_session_1"
    manager.add_message(session1, "user", "What is a SIP?")
    manager.add_message(session1, "assistant", "A SIP is a systematic investment plan...")
    manager.add_message(session1, "user", "How do I start one?")
    
    print(f"\nSession 1 History:")
    print(manager.get_history_text(session1))
    
    # Test session 2
    session2 = "test_session_2"
    manager.add_message(session2, "user", "Explain RBI repo rate")
    manager.add_message(session2, "assistant", "The RBI repo rate is...")
    
    print(f"\n\nSession 2 History:")
    print(manager.get_history_text(session2))
    
    # Stats
    print(f"\n\nMemory Stats:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Active sessions
    print(f"\nActive Sessions: {manager.get_active_sessions()}")
    
    # Session info
    print(f"\nSession 1 Info:")
    info = manager.get_session_info(session1)
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)

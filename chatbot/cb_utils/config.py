"""
Configuration management for chatbot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ChatbotConfig:
    """
    Centralized configuration for chatbot
    """
    
    # Groq Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "800"))
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.9"))
    
    # Qdrant Configuration
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "et_nexus_faq")
    QDRANT_VECTOR_SIZE = int(os.getenv("QDRANT_VECTOR_SIZE", "384"))  # all-MiniLM-L6-v2
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    
    # Chat Configuration
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))
    MAX_RETRIEVAL_RESULTS = int(os.getenv("MAX_RETRIEVAL_RESULTS", "3"))
    RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.7"))
    SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
    
    # Safety Configuration
    ENABLE_CONTENT_FILTER = os.getenv("ENABLE_CONTENT_FILTER", "true").lower() == "true"
    SEBI_COMPLIANCE_MODE = os.getenv("SEBI_COMPLIANCE_MODE", "strict")
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "chatbot" / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    @classmethod
    def get_qdrant_url(cls) -> str:
        """Get Qdrant connection URL"""
        return f"http://{cls.QDRANT_HOST}:{cls.QDRANT_PORT}"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY == "your_api_key_here":
            raise ValueError("GROQ_API_KEY not set")
        
        if cls.QDRANT_VECTOR_SIZE not in [384, 768, 1024, 1536]:
            raise ValueError(f"Invalid QDRANT_VECTOR_SIZE: {cls.QDRANT_VECTOR_SIZE}")
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("=" * 60)
        print("CHATBOT CONFIGURATION")
        print("=" * 60)
        print(f"Groq Model: {cls.GROQ_MODEL}")
        print(f"Groq Max Tokens: {cls.GROQ_MAX_TOKENS}")
        print(f"Groq Temperature: {cls.GROQ_TEMPERATURE}")
        print(f"Qdrant URL: {cls.get_qdrant_url()}")
        print(f"Qdrant Collection: {cls.QDRANT_COLLECTION}")
        print(f"Qdrant Vector Size: {cls.QDRANT_VECTOR_SIZE}")
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"Max Retrieval Results: {cls.MAX_RETRIEVAL_RESULTS}")
        print(f"Content Filter: {cls.ENABLE_CONTENT_FILTER}")
        print("=" * 60)


if __name__ == "__main__":
    ChatbotConfig.print_config()

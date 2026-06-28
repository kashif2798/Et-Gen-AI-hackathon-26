"""
Main entry point for ET Nexus Chatbot API

Run with: python chatbot/main.py
Or: uvicorn chatbot.main:app --reload
"""
import uvicorn
from api.endpoints import app

if __name__ == "__main__":
    print("=" * 70)
    print("ET NEXUS CHATBOT API")
    print("=" * 70)
    print()
    print("Starting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print()
    print("Press CTRL+C to stop")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

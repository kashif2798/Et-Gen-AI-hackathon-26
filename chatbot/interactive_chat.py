"""
Interactive Chat Client for ET Nexus Chatbot

Run this script to manually test the chatbot in your terminal.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine.chat_engine import ChatEngine
from datetime import datetime
import uuid


def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("ET NEXUS CHATBOT - Interactive Test")
    print("=" * 70)
    print()
    print("Welcome! Ask me anything about investments, markets, and finance.")
    print()
    print("Commands:")
    print("  - Type your question and press Enter")
    print("  - Type 'quit' or 'exit' to end the session")
    print("  - Type 'clear' to start a new conversation")
    print("  - Type 'history' to see conversation history")
    print("  - Type 'help' for more information")
    print()
    print("=" * 70)
    print()


def print_help():
    """Print help information"""
    print()
    print("=" * 70)
    print("HELP")
    print("=" * 70)
    print()
    print("Example Questions:")
    print("  - What is a SIP?")
    print("  - Explain LTCG tax")
    print("  - What are the benefits of mutual funds?")
    print("  - Tell me about bull and bear markets")
    print("  - What are SEBI guidelines?")
    print()
    print("Tips:")
    print("  - Ask specific questions for better answers")
    print("  - Use follow-up questions to dig deeper")
    print("  - The bot remembers your conversation context")
    print()
    print("Note:")
    print("  - Running in MOCK MODE (no real API calls)")
    print("  - Responses are simulated for testing")
    print()
    print("=" * 70)
    print()


def print_response(response, show_details=True):
    """Print chatbot response"""
    print()
    print("🤖 Assistant:")
    print("-" * 70)
    print(response.ai_reply)
    print("-" * 70)
    
    if show_details:
        print(f"Confidence: {response.confidence:.2%}")
        
        if response.sources:
            print(f"Sources: {len(response.sources)} Q&A pairs used")
        
        if response.metadata:
            print(f"Metadata: {response.metadata}")
    
    print()


def print_history(engine, session_id):
    """Print conversation history"""
    history = engine.memory.get_history(session_id)
    
    if not history:
        print("\nNo conversation history yet.\n")
        return
    
    print()
    print("=" * 70)
    print("CONVERSATION HISTORY")
    print("=" * 70)
    print()
    
    for i, msg in enumerate(history, 1):
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        role_name = "You" if msg["role"] == "user" else "Assistant"
        timestamp = msg.get("timestamp", "")
        
        print(f"{i}. {role_icon} {role_name}:")
        print(f"   {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
        if timestamp:
            print(f"   Time: {timestamp}")
        print()
    
    print("=" * 70)
    print()


def main():
    """Main interactive chat loop"""
    print_banner()
    
    # Initialize chat engine
    print("Initializing chatbot...")
    try:
        engine = ChatEngine()
        print("✅ Chatbot ready!\n")
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        print("\nNote: Make sure you're in the correct directory.")
        print("Run from project root: python chatbot/interactive_chat.py")
        return
    
    # Generate session ID
    session_id = f"interactive_{uuid.uuid4().hex[:8]}"
    print(f"Session ID: {session_id}")
    print()
    
    # Show initial help
    print("Type 'help' for example questions and tips.")
    print()
    
    # Main chat loop
    message_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for chatting! Goodbye!\n")
                break
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'clear':
                engine.clear_session(session_id)
                session_id = f"interactive_{uuid.uuid4().hex[:8]}"
                message_count = 0
                print(f"\n✅ New conversation started (Session: {session_id})\n")
                continue
            
            elif user_input.lower() == 'history':
                print_history(engine, session_id)
                continue
            
            # Process chat message
            print("\n🤔 Thinking...")
            
            try:
                response = engine.chat(user_input, session_id)
                message_count += 1
                print_response(response, show_details=True)
                
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                print("Please try again or type 'help' for assistance.\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")
            break
    
    # Show session stats
    if message_count > 0:
        print("=" * 70)
        print("SESSION SUMMARY")
        print("=" * 70)
        print(f"Messages sent: {message_count}")
        print(f"Session ID: {session_id}")
        print("=" * 70)
        print()


if __name__ == "__main__":
    main()

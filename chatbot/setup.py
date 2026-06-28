"""
Setup script for chatbot environment
"""
import subprocess
import sys
import os


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "chatbot/requirements.txt"
        ])
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_qdrant():
    """Check if Qdrant is running"""
    print("\nChecking Qdrant connection...")
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        print(f"✅ Qdrant is running ({len(collections.collections)} collections)")
        return True
    except Exception as e:
        print(f"⚠️  Qdrant not accessible: {e}")
        print("\nTo start Qdrant, run:")
        print("  docker run -p 6333:6333 qdrant/qdrant")
        return False


def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\nChecking .env file...")
    env_path = ".env"
    
    if os.path.exists(env_path):
        print("✅ .env file exists")
        return True
    
    print("Creating .env file...")
    env_content = """# Chatbot Configuration

# Groq Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile
GROQ_MAX_TOKENS=500
GROQ_TEMPERATURE=0.7

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=et_nexus_faq
QDRANT_VECTOR_SIZE=384

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=32

# Chat Configuration
MAX_HISTORY_MESSAGES=10
MAX_RETRIEVAL_RESULTS=3
RELEVANCE_THRESHOLD=0.7
SESSION_TIMEOUT_HOURS=24

# Safety Configuration
ENABLE_CONTENT_FILTER=true
SEBI_COMPLIANCE_MODE=strict
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created")
    return True


def verify_qa_data():
    """Verify Q&A data exists"""
    print("\nChecking Q&A data...")
    
    if not os.path.exists("q&a.md"):
        print("❌ q&a.md not found")
        return False
    print("✅ q&a.md found")
    
    if not os.path.exists("qa_pairs.json"):
        print("⚠️  qa_pairs.json not found")
        print("   Run: python chatbot/data/qa_processor.py --input q&a.md --output qa_pairs.json")
        return False
    print("✅ qa_pairs.json found")
    
    return True


def main():
    """Main setup function"""
    print("=" * 70)
    print("CHATBOT SETUP")
    print("=" * 70)
    print()
    
    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Environment File", create_env_file),
        ("Q&A Data", verify_qa_data),
        ("Qdrant Connection", check_qdrant)
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            success = step_func()
            results.append((step_name, success))
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            results.append((step_name, False))
    
    print("\n" + "=" * 70)
    print("SETUP SUMMARY")
    print("=" * 70)
    
    for step_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {step_name}")
    
    all_success = all(success for _, success in results)
    
    if all_success:
        print("\n🎉 Setup complete! You can now run:")
        print("  python chatbot/ingestion/qa_ingest.py --input qa_pairs.json --recreate --test-search")
    else:
        print("\n⚠️  Some steps failed. Please resolve the issues above.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()

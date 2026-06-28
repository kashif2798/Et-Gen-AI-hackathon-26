"""
Q&A Vector Store Ingestion

Manages Qdrant collection and ingests Q&A pairs with embeddings.
"""
import logging
from typing import List, Dict, Optional
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️  Warning: qdrant-client not installed. Install with: pip install qdrant-client")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")

try:
    from fastembed import TextEmbedding
    FASTEMBED_AVAILABLE = True
except ImportError:
    TextEmbedding = None
    FASTEMBED_AVAILABLE = False

from ..cb_api.schemas import QAPair
from ..cb_utils.config import ChatbotConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QAVectorStore:
    """
    Manages Q&A vector store operations with Qdrant
    """
    
    def __init__(
        self,
        collection_name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        embedding_model: Optional[str] = None,
        client: Optional[QdrantClient] = None
    ):
        """
        Initialize QA Vector Store
        
        Args:
            collection_name: Qdrant collection name
            host: Qdrant host
            port: Qdrant port
            embedding_model: Sentence transformer model name
            client: Optional pre-initialized QdrantClient instance
        """
        self.collection_name = collection_name or ChatbotConfig.QDRANT_COLLECTION
        self.host = host or ChatbotConfig.QDRANT_HOST
        self.port = port or ChatbotConfig.QDRANT_PORT
        self.embedding_model_name = embedding_model or ChatbotConfig.EMBEDDING_MODEL
        
        # Initialize clients
        if client is not None:
            self.client = client
            logger.info("Using shared QdrantClient instance for Q&A Vector Store")
        elif QDRANT_AVAILABLE:
            self.client = QdrantClient(host=self.host, port=self.port)
            logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
        else:
            self.client = None
            logger.warning("Qdrant client not available - running in mock mode")
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
            self.embedder_type = "sentence-transformers"
            logger.info(f"Embedding model loaded. Vector size: {self.vector_size}")
        elif FASTEMBED_AVAILABLE and TextEmbedding is not None:
            model_name = "BAAI/bge-small-en-v1.5" if "MiniLM" in self.embedding_model_name else self.embedding_model_name
            logger.info(f"Loading lightweight embedding model via fastembed: {model_name}")
            self.embedding_model = TextEmbedding(model_name=model_name)
            self.vector_size = 384
            self.embedder_type = "fastembed"
            logger.info(f"Fastembed model loaded. Vector size: {self.vector_size}")
        else:
            self.embedding_model = None
            self.vector_size = ChatbotConfig.QDRANT_VECTOR_SIZE
            self.embedder_type = None
            logger.warning("No embedding library available - running in mock mode")
    
    def create_collection(self, recreate: bool = False) -> bool:
        """
        Create Qdrant collection for Q&A pairs
        
        Args:
            recreate: If True, delete existing collection and recreate
            
        Returns:
            True if successful
        """
        if not self.client:
            logger.warning("Qdrant client not available")
            return False
        
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if collection_exists:
                if recreate:
                    logger.info(f"Deleting existing collection: {self.collection_name}")
                    self.client.delete_collection(self.collection_name)
                else:
                    logger.info(f"Collection already exists: {self.collection_name}")
                    return True
            
            # Create collection
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"✅ Collection created: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not self.embedding_model:
            # Mock embedding for testing
            import random
            return [random.random() for _ in range(self.vector_size)]
        
        if self.embedder_type == "sentence-transformers":
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        elif self.embedder_type == "fastembed":
            embeddings = list(self.embedding_model.embed([text]))
            return embeddings[0].tolist()
        else:
            import random
            return [random.random() for _ in range(self.vector_size)]
    
    def embed_qa_pairs(self, pairs: List[QAPair]) -> List[List[float]]:
        """
        Generate embeddings for multiple Q&A pairs
        
        Args:
            pairs: List of QAPair objects
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(pairs)} Q&A pairs...")
        
        # Combine question and answer for richer semantic matching
        texts = [f"Q: {pair.question}\nA: {pair.answer}" for pair in pairs]
        
        if not self.embedding_model:
            # Mock embeddings
            return [self.embed_text(text) for text in texts]
        
        if self.embedder_type == "sentence-transformers":
            # Batch encoding for efficiency
            embeddings = self.embedding_model.encode(
                texts,
                batch_size=ChatbotConfig.EMBEDDING_BATCH_SIZE,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return [emb.tolist() for emb in embeddings]
        elif self.embedder_type == "fastembed":
            embeddings = list(self.embedding_model.embed(texts))
            logger.info(f"✅ Generated {len(embeddings)} embeddings via fastembed")
            return [emb.tolist() for emb in embeddings]
        else:
            return [self.embed_text(text) for text in texts]
        
        logger.info(f"✅ Generated {len(embeddings)} embeddings")
        return [emb.tolist() for emb in embeddings]
    
    def upsert_qa_pairs(self, pairs: List[QAPair]) -> bool:
        """
        Upsert Q&A pairs into vector store
        
        Args:
            pairs: List of QAPair objects
            
        Returns:
            True if successful
        """
        if not self.client:
            logger.warning("Qdrant client not available")
            return False
        
        try:
            logger.info(f"Upserting {len(pairs)} Q&A pairs...")
            
            # Generate embeddings
            embeddings = self.embed_qa_pairs(pairs)
            
            # Create points
            points = []
            for i, (pair, embedding) in enumerate(zip(pairs, embeddings)):
                point = PointStruct(
                    id=i + 1,  # Qdrant IDs start from 1
                    vector=embedding,
                    payload={
                        "qa_id": pair.id,
                        "question": pair.question,
                        "answer": pair.answer,
                        "category": pair.category,
                        "category_number": pair.category_number,
                        "question_number": pair.question_number,
                        "keywords": pair.keywords,
                        "metadata": pair.metadata
                    }
                )
                points.append(point)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                logger.info(f"Upserted batch {i // batch_size + 1} ({len(batch)} points)")
            
            logger.info(f"✅ Successfully upserted {len(pairs)} Q&A pairs")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting Q&A pairs: {e}")
            return False
    
    def search_similar(
        self,
        query: str,
        limit: int = 3,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Search for similar Q&A pairs
        
        Args:
            query: Search query
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of matching Q&A pairs with scores
        """
        if not self.client:
            logger.warning("Qdrant client not available")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold or ChatbotConfig.RELEVANCE_THRESHOLD
            )
            
            # Format results
            matches = []
            for result in results:
                match = {
                    "qa_id": result.payload["qa_id"],
                    "question": result.payload["question"],
                    "answer": result.payload["answer"],
                    "category": result.payload["category"],
                    "score": result.score,
                    "keywords": result.payload.get("keywords", [])
                }
                matches.append(match)
            
            logger.info(f"Found {len(matches)} matches for query: {query[:50]}...")
            return matches
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """
        Get collection statistics
        
        Returns:
            Dictionary with collection stats
        """
        if not self.client:
            return {"error": "Qdrant client not available"}
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            stats = {
                "collection_name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "vector_size": self.vector_size,
                "status": collection_info.status,
                "optimizer_status": collection_info.optimizer_status
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
    
    def delete_collection(self) -> bool:
        """
        Delete the collection
        
        Returns:
            True if successful
        """
        if not self.client:
            logger.warning("Qdrant client not available")
            return False
        
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"✅ Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False


def main():
    """
    Main function to run Q&A ingestion
    """
    import argparse
    from data.qa_processor import QAProcessor
    
    parser = argparse.ArgumentParser(description="Ingest Q&A pairs into Qdrant")
    parser.add_argument("--input", default="qa_pairs.json", help="Input JSON file with Q&A pairs")
    parser.add_argument("--recreate", action="store_true", help="Recreate collection if exists")
    parser.add_argument("--test-search", action="store_true", help="Test search after ingestion")
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("Q&A VECTOR STORE INGESTION")
    logger.info("=" * 70)
    
    # Check dependencies
    if not QDRANT_AVAILABLE:
        logger.error("❌ qdrant-client not installed. Install with: pip install qdrant-client")
        return
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        logger.error("❌ sentence-transformers not installed. Install with: pip install sentence-transformers")
        return
    
    # Load Q&A pairs
    logger.info(f"\n1. Loading Q&A pairs from {args.input}...")
    processor = QAProcessor()
    qa_pairs = processor.load_from_json(args.input)
    logger.info(f"✅ Loaded {len(qa_pairs)} Q&A pairs")
    
    # Initialize vector store
    logger.info("\n2. Initializing vector store...")
    vector_store = QAVectorStore()
    
    # Create collection
    logger.info("\n3. Creating Qdrant collection...")
    success = vector_store.create_collection(recreate=args.recreate)
    if not success:
        logger.error("❌ Failed to create collection")
        return
    
    # Upsert Q&A pairs
    logger.info("\n4. Upserting Q&A pairs...")
    success = vector_store.upsert_qa_pairs(qa_pairs)
    if not success:
        logger.error("❌ Failed to upsert Q&A pairs")
        return
    
    # Get stats
    logger.info("\n5. Collection statistics:")
    stats = vector_store.get_collection_stats()
    for key, value in stats.items():
        logger.info(f"   {key}: {value}")
    
    # Test search
    if args.test_search:
        logger.info("\n6. Testing search functionality...")
        test_queries = [
            "What is a SIP?",
            "How does RBI repo rate affect home loans?",
            "Explain bull and bear market"
        ]
        
        for query in test_queries:
            logger.info(f"\n   Query: {query}")
            results = vector_store.search_similar(query, limit=3)
            for i, result in enumerate(results, 1):
                logger.info(f"   {i}. [{result['score']:.3f}] {result['question'][:60]}...")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ INGESTION COMPLETE!")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()

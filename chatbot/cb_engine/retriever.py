"""
Q&A Retriever

Retrieves relevant Q&A context from vector store with reranking.
"""
import logging
from typing import List, Dict, Optional
from pathlib import Path
import sys

from ..cb_ingestion.qa_ingest import QAVectorStore
from ..cb_api.schemas import QAPair
from ..cb_utils.config import ChatbotConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QARetriever:
    """
    Retrieves relevant Q&A context from vector store
    """
    
    def __init__(
        self,
        vector_store: Optional[QAVectorStore] = None,
        top_k: Optional[int] = None,
        relevance_threshold: Optional[float] = None
    ):
        """
        Initialize retriever
        
        Args:
            vector_store: QAVectorStore instance
            top_k: Number of results to retrieve
            relevance_threshold: Minimum relevance score
        """
        self.vector_store = vector_store or QAVectorStore()
        self.top_k = top_k or ChatbotConfig.MAX_RETRIEVAL_RESULTS
        self.relevance_threshold = relevance_threshold or ChatbotConfig.RELEVANCE_THRESHOLD
        
        logger.info(f"Retriever initialized (top_k: {self.top_k}, threshold: {self.relevance_threshold})")
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        include_metadata: bool = True
    ) -> List[Dict]:
        """
        Retrieve relevant Q&A pairs for query
        
        Args:
            query: User query
            top_k: Number of results to retrieve
            include_metadata: Whether to include metadata
            
        Returns:
            List of relevant Q&A pairs with scores
        """
        top_k = top_k or self.top_k
        
        logger.info(f"Retrieving top {top_k} results for query: {query[:50]}...")
        
        # Search vector store
        results = self.vector_store.search_similar(
            query=query,
            limit=top_k,
            score_threshold=self.relevance_threshold
        )
        
        if not results:
            logger.warning("No relevant results found")
            return []
        
        logger.info(f"Retrieved {len(results)} results")
        
        # Optionally filter metadata
        if not include_metadata:
            for result in results:
                result.pop('keywords', None)
        
        return results
    
    def rerank(
        self,
        query: str,
        candidates: List[Dict]
    ) -> List[Dict]:
        """
        Rerank candidates based on additional criteria
        
        Args:
            query: User query
            candidates: List of candidate Q&A pairs
            
        Returns:
            Reranked list
        """
        # Simple reranking based on keyword overlap
        query_words = set(query.lower().split())
        
        for candidate in candidates:
            # Calculate keyword overlap bonus
            keywords = candidate.get('keywords', [])
            keyword_overlap = len(
                set(k.lower() for k in keywords) & query_words
            )
            
            # Adjust score (small bonus for keyword overlap)
            original_score = candidate.get('score', 0.0)
            bonus = min(keyword_overlap * 0.02, 0.1)  # Max 0.1 bonus
            candidate['reranked_score'] = min(original_score + bonus, 1.0)
        
        # Sort by reranked score
        candidates.sort(key=lambda x: x.get('reranked_score', x.get('score', 0)), reverse=True)
        
        return candidates
    
    def filter_by_relevance(
        self,
        results: List[Dict],
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Filter results by relevance threshold
        
        Args:
            results: List of results
            threshold: Minimum relevance score
            
        Returns:
            Filtered results
        """
        threshold = threshold or self.relevance_threshold
        
        filtered = [
            result for result in results
            if result.get('score', 0.0) >= threshold
        ]
        
        logger.info(f"Filtered {len(results)} -> {len(filtered)} results (threshold: {threshold})")
        
        return filtered
    
    def format_context(
        self,
        results: List[Dict],
        include_scores: bool = False
    ) -> str:
        """
        Format retrieved results as context string
        
        Args:
            results: List of Q&A results
            include_scores: Whether to include relevance scores
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant information found."
        
        context_parts = []
        
        for i, result in enumerate(results, 1):
            score_text = f" (Relevance: {result['score']:.2f})" if include_scores else ""
            
            context_parts.append(
                f"[Context {i}]{score_text}\n"
                f"Q: {result['question']}\n"
                f"A: {result['answer']}"
            )
        
        return "\n\n".join(context_parts)
    
    def get_category_distribution(self, results: List[Dict]) -> Dict[str, int]:
        """
        Get distribution of categories in results
        
        Args:
            results: List of results
            
        Returns:
            Category distribution
        """
        distribution = {}
        
        for result in results:
            category = result.get('category', 'Unknown')
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution


if __name__ == "__main__":
    # Test retriever
    from ingestion.qa_ingest import QAVectorStore
    
    print("Testing Q&A Retriever")
    print("=" * 60)
    
    # Initialize
    vector_store = QAVectorStore()
    retriever = QARetriever(vector_store)
    
    # Test queries
    test_queries = [
        "What is a SIP?",
        "How does RBI repo rate affect home loans?",
        "Explain bull and bear markets"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        # Retrieve
        results = retriever.retrieve(query, top_k=3)
        
        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. [{result['score']:.3f}] {result['question'][:60]}...")
                print(f"   Category: {result.get('category', 'Unknown')}")
        else:
            print("No results found")
        
        # Format context
        if results:
            print("\nFormatted Context:")
            print(retriever.format_context(results[:2], include_scores=True))
    
    print("\n" + "=" * 60)

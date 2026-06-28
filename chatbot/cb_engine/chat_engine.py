"""
Chat Engine

Main conversational RAG engine that combines retrieval, LLM generation,
and conversation memory.
"""
import logging
from typing import Dict, Optional, List
from pathlib import Path
import sys

from .retriever import QARetriever
from .memory_manager import MemoryManager
from ..cb_utils.groq_client import GroqClient
from ..cb_api.schemas import ChatRequest, ChatResponse, QAPair
from ..cb_utils.config import ChatbotConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatEngine:
    """
    Main conversational RAG engine
    """
    
    # System prompt template
    SYSTEM_PROMPT_TEMPLATE = """You are E-newspaper Assistant, a helpful news and information chatbot.

Your role:
- Answer questions about news articles, current events, and general knowledge
- Use the provided context to answer questions accurately
- Be clear, concise, and informative
- Maintain conversation context from chat history
- Provide diverse, varied responses - avoid repeating the same information
- If the question is not covered in the context, use your general knowledge to provide a helpful answer

Response Guidelines:
- Keep responses concise and informative (2-3 paragraphs maximum)
- Vary your language and structure - don't use the same opening phrases repeatedly
- When asked similar questions, provide different angles or additional details
- Be conversational and natural in your responses
- Cite sources when information comes from the provided context

Context from Knowledge Base:
{context}

Conversation History:
{history}

User Question: {query}

Instructions:
1. Review the conversation history to avoid repetitive responses
2. Check if the context contains relevant information
3. Provide a clear, informative answer with varied language
4. If you've answered similar questions before, add new insights or perspectives
5. Be natural and conversational

Answer:"""
    
    def __init__(
        self,
        retriever: Optional[QARetriever] = None,
        memory_manager: Optional[MemoryManager] = None,
        llm_client: Optional[GroqClient] = None
    ):
        """
        Initialize chat engine
        
        Args:
            retriever: QARetriever instance
            memory_manager: MemoryManager instance
            llm_client: GroqClient instance
        """
        self.retriever = retriever or QARetriever()
        self.memory = memory_manager or MemoryManager()
        self.llm = llm_client or GroqClient()
        
        logger.info("Chat engine initialized")
    
    def chat(
        self,
        user_message: str,
        session_id: str,
        user_profile: Optional[Dict] = None,
        article_text: Optional[str] = None
    ) -> ChatResponse:
        """
        Process chat message and generate response
        
        Args:
            user_message: User's message
            session_id: Session identifier
            user_profile: Optional user profile data
            article_text: Optional text of the active article
            
        Returns:
            ChatResponse with AI reply and sources
        """
        logger.info(f"Processing chat for session {session_id}: {user_message[:50]}...")
        
        # 1. Retrieve relevant context
        context_results = self._retrieve_context(user_message)
        
        # 2. Get conversation history
        history = self.memory.get_history_text(session_id, limit=5)
        
        # 3. Build prompt
        prompt = self._build_prompt(user_message, context_results, history, article_text=article_text)
        
        # 4. Generate response
        ai_reply = self._generate_response(prompt)
        
        # 5. Apply guardrails
        ai_reply = self._apply_guardrails(ai_reply)
        
        # 6. Calculate confidence
        confidence = self._calculate_confidence(context_results, ai_reply)
        
        # 7. Update memory
        self.memory.add_message(session_id, "user", user_message)
        self.memory.add_message(session_id, "assistant", ai_reply)
        
        # 8. Build response
        response = ChatResponse(
            session_id=session_id,
            ai_reply=ai_reply,
            sources=[self._format_source(r) for r in context_results],
            confidence=confidence,
            metadata={
                "context_count": len(context_results),
                "history_length": len(self.memory.get_history(session_id)),
                "model": self.llm.model,
                "retrieval_scores": [r.get('score', 0) for r in context_results]
            }
        )
        
        logger.info(f"Generated response (confidence: {confidence:.2f})")
        
        return response
    
    def _retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant Q&A context
        
        Args:
            query: User query
            top_k: Number of results
            
        Returns:
            List of relevant Q&A pairs
        """
        results = self.retriever.retrieve(query, top_k=top_k)
        
        # Rerank for better relevance
        if results:
            results = self.retriever.rerank(query, results)
        
        return results
    
    def _build_prompt(
        self,
        query: str,
        context_results: List[Dict],
        history: str,
        article_text: Optional[str] = None
    ) -> str:
        """
        Build prompt for LLM
        
        Args:
            query: User query
            context_results: Retrieved context
            history: Conversation history
            article_text: Optional text of the active article
            
        Returns:
            Complete prompt
        """
        # Format context
        context = self.retriever.format_context(context_results, include_scores=False)
        if article_text:
            context = f"CURRENT ARTICLE ACTIVE IN FRONTEND SCREEN:\n{article_text}\n\nADDITIONAL CONTEXT FROM KNOWLEDGE BASE:\n{context}"
        
        # Format history
        if not history:
            history = "No previous conversation"
        
        # Build prompt from template
        prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            context=context,
            history=history,
            query=query
        )
        
        return prompt
    
    def _generate_response(self, prompt: str) -> str:
        """
        Generate response using LLM
        
        Args:
            prompt: Complete prompt
            
        Returns:
            Generated response
        """
        response = self.llm.generate(
            prompt=prompt,
            max_tokens=ChatbotConfig.GROQ_MAX_TOKENS,
            temperature=ChatbotConfig.GROQ_TEMPERATURE
        )
        
        return response.strip()
    
    def _apply_guardrails(self, response: str) -> str:
        """
        Apply SEBI compliance guardrails
        
        Args:
            response: Generated response
            
        Returns:
            Filtered response
        """
        if not ChatbotConfig.ENABLE_CONTENT_FILTER:
            return response
        
        # Check for banned phrases
        banned_phrases = [
            "buy now", "sell now", "must buy", "must sell",
            "guaranteed returns", "sure profit", "risk-free",
            "100% returns", "can't lose", "will definitely"
        ]
        
        response_lower = response.lower()
        violations = []
        
        for phrase in banned_phrases:
            if phrase in response_lower:
                violations.append(phrase)
        
        if violations:
            logger.warning(f"SEBI compliance violations detected: {violations}")
            
            # Add disclaimer
            response += ("\n\nDisclaimer: This is educational information only. "
                        "Please consult a SEBI-registered financial advisor for "
                        "personalized investment advice.")
        
        return response
    
    def _calculate_confidence(
        self,
        context_results: List[Dict],
        response: str
    ) -> float:
        """
        Calculate confidence score for response
        
        Args:
            context_results: Retrieved context
            response: Generated response
            
        Returns:
            Confidence score (0-1)
        """
        if not context_results:
            return 0.3  # Low confidence without context
        
        # Base confidence from retrieval scores
        avg_score = sum(r.get('score', 0) for r in context_results) / len(context_results)
        
        # Adjust based on response length (very short = less confident)
        length_factor = min(len(response) / 200, 1.0)
        
        # Adjust based on number of sources
        source_factor = min(len(context_results) / 3, 1.0)
        
        # Combined confidence
        confidence = (avg_score * 0.6 + length_factor * 0.2 + source_factor * 0.2)
        
        return min(confidence, 1.0)
    
    def _format_source(self, result: Dict) -> QAPair:
        """
        Format result as QAPair for response
        
        Args:
            result: Search result
            
        Returns:
            QAPair object
        """
        return QAPair(
            id=result.get('qa_id', 'unknown'),
            question=result.get('question', ''),
            answer=result.get('answer', ''),
            category=result.get('category', 'Unknown'),
            category_number=0,
            question_number=0,
            keywords=result.get('keywords', []),
            metadata={'score': result.get('score', 0)}
        )
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear conversation history for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if cleared
        """
        return self.memory.clear_session(session_id)
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get session information
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session info dictionary
        """
        return self.memory.get_session_info(session_id)


if __name__ == "__main__":
    # Test chat engine
    print("Testing Chat Engine")
    print("=" * 70)
    
    # Initialize
    engine = ChatEngine()
    session_id = "test_session"
    
    # Test conversation
    test_messages = [
        "What is a SIP?",
        "How do I start one?",
        "What are the benefits during market volatility?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*70}")
        print(f"Turn {i}")
        print(f"{'='*70}")
        print(f"User: {message}")
        
        response = engine.chat(message, session_id)
        
        print(f"\nAssistant: {response.ai_reply}")
        print(f"\nConfidence: {response.confidence:.2f}")
        print(f"Sources: {len(response.sources)}")
        
        if response.sources:
            print("\nTop Source:")
            print(f"  Q: {response.sources[0].question[:60]}...")
            print(f"  Category: {response.sources[0].category}")
    
    # Session info
    print(f"\n{'='*70}")
    print("Session Info:")
    info = engine.get_session_info(session_id)
    if info:
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    print(f"\n{'='*70}")

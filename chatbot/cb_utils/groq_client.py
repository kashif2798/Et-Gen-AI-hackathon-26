"""
Groq LLM Client Wrapper

Provides interface to Groq API with retry logic and error handling.
"""
import logging
from typing import List, Dict, Optional
import time
from pathlib import Path
import sys

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Warning: groq not installed. Install with: pip install groq")

from .config import ChatbotConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqClient:
    """
    Wrapper for Groq API with retry logic
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3
    ):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key
            model: Model name
            max_retries: Maximum retry attempts
        """
        self.api_key = api_key or ChatbotConfig.GROQ_API_KEY
        self.model = model or ChatbotConfig.GROQ_MODEL
        self.max_retries = max_retries
        
        if GROQ_AVAILABLE and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info(f"Groq client initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            self.client = None
            if not GROQ_AVAILABLE:
                logger.warning("Groq library not available - running in mock mode")
            else:
                logger.warning("Groq API key not provided - running in mock mode")
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> str:
        """
        Generate response from Groq
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream response
            
        Returns:
            Generated text
        """
        if not self.client:
            return self._mock_response(prompt)
        
        max_tokens = max_tokens or ChatbotConfig.GROQ_MAX_TOKENS
        temperature = temperature or ChatbotConfig.GROQ_TEMPERATURE
        
        for attempt in range(self.max_retries):
            try:
                messages = self._build_messages(prompt)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream
                )
                
                if stream:
                    return response  # Return generator for streaming
                else:
                    return response.choices[0].message.content
                    
            except Exception as e:
                logger.warning(f"Groq API error (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries exceeded, returning mock response")
                    return self._mock_response(prompt)
        
        return self._mock_response(prompt)
    
    def _build_messages(self, prompt: str) -> List[Dict]:
        """
        Build messages array for Groq API
        
        Args:
            prompt: User prompt
            
        Returns:
            Messages array
        """
        return [
            {
                "role": "user",
                "content": prompt
            }
        ]
    
    def _mock_response(self, prompt: str) -> str:
        """
        Generate mock response for testing
        
        Args:
            prompt: Input prompt
            
        Returns:
            Mock response
        """
        logger.info("Generating mock response")
        
        # Simple keyword-based mock responses
        prompt_lower = prompt.lower()
        
        if "sip" in prompt_lower or "systematic investment" in prompt_lower:
            return ("A Systematic Investment Plan (SIP) is a method of investing in mutual funds "
                   "where you invest a fixed amount regularly. It helps in rupee cost averaging and "
                   "is beneficial during market volatility as you buy more units when prices are low.")
        
        elif "rbi" in prompt_lower or "repo rate" in prompt_lower:
            return ("The RBI repo rate is the rate at which the Reserve Bank of India lends money to "
                   "commercial banks. When the repo rate increases, borrowing becomes more expensive, "
                   "which typically leads to higher EMIs on floating rate loans.")
        
        elif "bull" in prompt_lower or "bear" in prompt_lower:
            return ("A bull market is characterized by rising prices and investor optimism, while a "
                   "bear market features falling prices and pessimism. Understanding market cycles "
                   "helps investors make informed decisions.")
        
        else:
            return ("Based on the available information, I can provide you with insights about Indian "
                   "financial markets, investment strategies, and regulatory guidelines. Please feel "
                   "free to ask specific questions about stocks, mutual funds, or market trends.")
    
    def get_model_info(self) -> Dict:
        """
        Get information about the current model
        
        Returns:
            Model information dictionary
        """
        return {
            "model": self.model,
            "api_available": self.client is not None,
            "max_tokens": ChatbotConfig.GROQ_MAX_TOKENS,
            "temperature": ChatbotConfig.GROQ_TEMPERATURE
        }


if __name__ == "__main__":
    # Test Groq client
    client = GroqClient()
    
    print("Testing Groq Client")
    print("=" * 60)
    
    test_prompts = [
        "What is a SIP?",
        "How does RBI repo rate affect loans?",
        "Explain bull and bear markets"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        response = client.generate(prompt, max_tokens=200)
        print(f"Response: {response[:200]}...")
    
    print("\n" + "=" * 60)
    print("Model Info:", client.get_model_info())

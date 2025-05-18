"""
LLM-powered code augmentation for intelligent analysis and summarization
"""
import os
import json
import logging
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import time
from functools import lru_cache

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available"""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self, api_key_env_var: str = "GEMINI_API_KEY"):
        self.api_key = os.environ.get(api_key_env_var)
        self.model_name = "gemini-1.5-flash"
        self._client = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
                self._available = True
            except ImportError:
                logger.warning("google-generativeai package not installed. Install with: pip install google-generativeai")
                self._available = False
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self._available = False
        else:
            self._available = False
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        """Generate a response using Gemini API"""
        if not self._available:
            return ""
        
        try:
            response = self._client.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': max_tokens,
                    'temperature': temperature
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return ""
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using Gemini's tokenizer"""
        if not self._available:
            return len(text.split())  # Fallback to word count
        
        try:
            return self._client.count_tokens(text).total_tokens
        except Exception:
            return len(text.split())  # Fallback to word count
    
    def is_available(self) -> bool:
        """Check if Gemini is configured and available"""
        return self._available


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (stub for future implementation)"""
    
    def __init__(self, api_key_env_var: str = "OPENAI_API_KEY"):
        self.api_key = os.environ.get(api_key_env_var)
        self.model_name = "gpt-3.5-turbo"
        self._available = False  # Stub implementation
        
        if self.api_key:
            # TODO: Implement OpenAI client initialization
            logger.info("OpenAI provider stub - not yet implemented")
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        """Generate a response using OpenAI API (stub)"""
        return ""
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using OpenAI's tokenizer (stub)"""
        return len(text.split())  # Simple word count fallback
    
    def is_available(self) -> bool:
        """Check if OpenAI is configured and available"""
        return self._available


class LLMAugmenter:
    """Main LLM augmentation class for code analysis and summarization"""
    
    def __init__(self, 
                 provider: str = "gemini",
                 api_key_env_var: Optional[str] = None,
                 enable_cache: bool = True):
        """
        Initialize the LLM augmenter
        
        Args:
            provider: LLM provider name ("gemini", "openai")
            api_key_env_var: Environment variable name for API key
            enable_cache: Whether to cache responses
        """
        self.provider_name = provider
        self.enable_cache = enable_cache
        self.token_usage = {
            'input_tokens': 0,
            'output_tokens': 0,
            'api_calls': 0
        }
        
        # Initialize provider
        if provider == "gemini":
            self.provider = GeminiProvider(api_key_env_var or "GEMINI_API_KEY")
        elif provider == "openai":
            self.provider = OpenAIProvider(api_key_env_var or "OPENAI_API_KEY")
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not self.provider.is_available():
            logger.warning(f"{provider} provider is not available. LLM augmentation will be disabled.")
    
    def is_available(self) -> bool:
        """Check if LLM augmentation is available"""
        return self.provider.is_available()
    
    def _track_usage(self, prompt: str, response: str):
        """Track token usage for monitoring"""
        if self.provider.is_available():
            self.token_usage['input_tokens'] += self.provider.count_tokens(prompt)
            self.token_usage['output_tokens'] += self.provider.count_tokens(response)
            self.token_usage['api_calls'] += 1
    
    @lru_cache(maxsize=128)
    def _cached_generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Cached generation to avoid duplicate API calls"""
        return self.provider.generate(prompt, max_tokens, temperature)
    
    def _generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        """Generate response with optional caching"""
        if not self.provider.is_available():
            return ""
        
        if self.enable_cache:
            response = self._cached_generate(prompt, max_tokens, temperature)
        else:
            response = self.provider.generate(prompt, max_tokens, temperature)
        
        self._track_usage(prompt, response)
        return response
    
    def summarize_code_chunk(self, 
                            code: str, 
                            task_context: str = "Summarize this code concisely",
                            max_summary_tokens: int = 150) -> str:
        """
        Generate a concise summary of a code chunk
        
        Args:
            code: The code to summarize
            task_context: Context about what kind of summary is needed
            max_summary_tokens: Maximum tokens for the summary
        
        Returns:
            Concise summary of the code
        """
        prompt = f"""You are analyzing code for another AI coding agent. {task_context}

CODE:
```
{code[:5000]}  # Truncate very long code
```

TASK: Provide a concise summary (max {max_summary_tokens} tokens) that captures:
1. The main purpose/functionality
2. Key algorithms or logic used
3. Important data structures or dependencies
4. Any critical assumptions or constraints

Be direct and technical. Focus on information that would help another AI understand and modify this code.

SUMMARY:"""
        
        return self._generate(prompt, max_summary_tokens, temperature=0.2)
    
    def identify_potential_ambiguities(self, 
                                      code_chunk: str,
                                      task_context: str = "Analyze for ambiguities") -> List[str]:
        """
        Identify potential ambiguities in code that could confuse an AI agent
        
        Args:
            code_chunk: Code to analyze
            task_context: Specific analysis context
        
        Returns:
            List of identified ambiguities
        """
        prompt = f"""You are a code analysis assistant helping another AI coding agent. {task_context}

CODE:
```
{code_chunk[:3000]}  # Truncate very long code
```

TASK: Identify potential ambiguities that could confuse an AI trying to modify this code:
1. Unclear variable or function names
2. Complex control flow without comments
3. Type ambiguities (dynamic typing issues)
4. Implicit dependencies or side effects
5. Magic numbers or hardcoded values without explanation

Return a JSON list of ambiguities, each as a string describing the issue.
Format: ["ambiguity 1", "ambiguity 2", ...]

AMBIGUITIES:"""
        
        response = self._generate(prompt, max_tokens=400, temperature=0.3)
        
        try:
            # Parse JSON response
            ambiguities = json.loads(response)
            if isinstance(ambiguities, list):
                return [str(a) for a in ambiguities]
        except:
            # Fallback to line-based parsing
            lines = response.strip().split('\n')
            return [line.strip('- ') for line in lines if line.strip()]
        
        return []
    
    def infer_implicit_assumptions(self, 
                                  code_chunk: str,
                                  task_context: str = "Analyze implicit assumptions") -> List[str]:
        """
        Infer implicit assumptions in the code
        
        Args:
            code_chunk: Code to analyze
            task_context: Specific analysis context
        
        Returns:
            List of implicit assumptions
        """
        prompt = f"""You are analyzing code to help another AI coding agent understand hidden assumptions. {task_context}

CODE:
```
{code_chunk[:3000]}  # Truncate very long code
```

TASK: Identify implicit assumptions that aren't explicitly documented:
1. Expected input formats or ranges
2. Environmental dependencies (files, APIs, services)
3. State assumptions (initialization, ordering)
4. Performance assumptions (data size, frequency)
5. Platform or library version assumptions

Return a JSON list of assumptions, each as a string.
Format: ["assumption 1", "assumption 2", ...]

ASSUMPTIONS:"""
        
        response = self._generate(prompt, max_tokens=400, temperature=0.3)
        
        try:
            assumptions = json.loads(response)
            if isinstance(assumptions, list):
                return [str(a) for a in assumptions]
        except:
            lines = response.strip().split('\n')
            return [line.strip('- ') for line in lines if line.strip()]
        
        return []
    
    def suggest_clarifying_questions(self, 
                                    code_chunk: str,
                                    task_context: str = "For code modification") -> List[str]:
        """
        Generate clarifying questions for the downstream AI agent
        
        Args:
            code_chunk: Code to analyze
            task_context: Context about the intended modification
        
        Returns:
            List of clarifying questions
        """
        prompt = f"""You are helping another AI coding agent by suggesting questions it should consider before modifying code. {task_context}

CODE:
```
{code_chunk[:3000]}  # Truncate very long code
```

TASK: Generate clarifying questions the AI should consider:
1. Questions about intended behavior changes
2. Questions about edge cases or error handling
3. Questions about performance implications
4. Questions about backward compatibility
5. Questions about testing requirements

Return a JSON list of questions, each as a string.
Format: ["question 1", "question 2", ...]

QUESTIONS:"""
        
        response = self._generate(prompt, max_tokens=400, temperature=0.3)
        
        try:
            questions = json.loads(response)
            if isinstance(questions, list):
                return [str(q) for q in questions]
        except:
            lines = response.strip().split('\n')
            return [line.strip('- ') for line in lines if line.strip()]
        
        return []
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return self.token_usage.copy()
    
    def reset_usage_stats(self):
        """Reset token usage statistics"""
        self.token_usage = {
            'input_tokens': 0,
            'output_tokens': 0,
            'api_calls': 0
        }
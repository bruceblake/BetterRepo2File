"""
Advanced token management for repo2file
"""
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json

# Model configurations with context windows
MODEL_CONFIGS = {
    # OpenAI models
    'gpt-4': {'encoding': 'cl100k_base', 'max_tokens': 128000},
    'gpt-4-turbo': {'encoding': 'cl100k_base', 'max_tokens': 128000},
    'gpt-3.5-turbo': {'encoding': 'cl100k_base', 'max_tokens': 16385},
    'gpt-3.5-turbo-16k': {'encoding': 'cl100k_base', 'max_tokens': 16385},
    
    # Anthropic Claude models
    'claude-3': {'encoding': 'cl100k_base', 'max_tokens': 200000},
    'claude-3-opus': {'encoding': 'cl100k_base', 'max_tokens': 200000},
    'claude-3-sonnet': {'encoding': 'cl100k_base', 'max_tokens': 200000},
    'claude-3-haiku': {'encoding': 'cl100k_base', 'max_tokens': 200000},
    'claude-2': {'encoding': 'cl100k_base', 'max_tokens': 100000},
    'claude-2.1': {'encoding': 'cl100k_base', 'max_tokens': 200000},
    'claude-instant': {'encoding': 'cl100k_base', 'max_tokens': 100000},
    'claude': {'encoding': 'cl100k_base', 'max_tokens': 100000},  # Default Claude
    
    # Google Gemini models
    'gemini-1.5-pro': {'encoding': 'cl100k_base', 'max_tokens': 2000000},
    'gemini-1.5-flash': {'encoding': 'cl100k_base', 'max_tokens': 1000000},
    'gemini-1.0-pro': {'encoding': 'cl100k_base', 'max_tokens': 32000},
    'gemini': {'encoding': 'cl100k_base', 'max_tokens': 1000000},  # Default Gemini
    
    # Meta Llama models
    'llama': {'encoding': 'cl100k_base', 'max_tokens': 32000},
    'llama-2': {'encoding': 'cl100k_base', 'max_tokens': 4096},
    'llama-2-70b': {'encoding': 'cl100k_base', 'max_tokens': 4096},
    'codellama': {'encoding': 'cl100k_base', 'max_tokens': 16384},
}

@dataclass
class TokenAllocation:
    file_path: str
    allocated_tokens: int
    actual_tokens: int
    priority: float
    truncated: bool = False

@dataclass 
class TokenBudget:
    total: int
    used: int = 0
    reserved: Dict[str, int] = field(default_factory=dict)
    allocations: List[TokenAllocation] = field(default_factory=list)
    
    @property
    def remaining(self) -> int:
        return self.total - self.used - sum(self.reserved.values())
    
    def reserve(self, category: str, tokens: int) -> bool:
        if self.remaining >= tokens:
            self.reserved[category] = tokens
            return True
        return False
    
    def allocate(self, file_path: str, tokens: int, priority: float) -> TokenAllocation:
        actual_tokens = min(tokens, self.remaining)
        allocation = TokenAllocation(
            file_path=file_path,
            allocated_tokens=actual_tokens,
            actual_tokens=tokens,
            priority=priority,
            truncated=actual_tokens < tokens
        )
        self.allocations.append(allocation)
        self.used += actual_tokens
        return allocation

class TokenManager:
    def __init__(self, model: str = "gpt-4", budget: int = None):
        self.model = model
        self.encoder = None
        
        # Get model configuration
        model_config = self._get_model_config(model)
        self.model_max_tokens = model_config['max_tokens']
        
        # Set budget based on model if not provided
        if budget is None:
            # Use 50% of model's max tokens as default budget to leave room for prompts
            budget = int(self.model_max_tokens * 0.5)
        
        # Ensure budget doesn't exceed model's max tokens
        if budget > self.model_max_tokens:
            print(f"Warning: Budget {budget} exceeds {model}'s max tokens {self.model_max_tokens}. Adjusting to {self.model_max_tokens * 0.5}")
            budget = int(self.model_max_tokens * 0.5)
        
        if TIKTOKEN_AVAILABLE:
            try:
                # Special case for non-OpenAI models which use the same encoding as GPT-4
                if model.startswith(('gemini', 'claude', 'llama')):
                    self.encoder = tiktoken.get_encoding("cl100k_base")
                else:
                    self.encoder = tiktoken.encoding_for_model(model)
            except:
                # Fallback to cl100k_base encoding
                try:
                    self.encoder = tiktoken.get_encoding("cl100k_base")
                except:
                    self.encoder = None
        
        self.budget = TokenBudget(total=budget)
        self.cache: Dict[str, int] = {}
    
    def _get_model_config(self, model: str) -> Dict:
        """Get model configuration with fallback"""
        # First try exact match
        if model in MODEL_CONFIGS:
            return MODEL_CONFIGS[model]
        
        # Try prefix matching (e.g., 'claude-3-sonnet-20240219' -> 'claude-3-sonnet')
        for key in MODEL_CONFIGS:
            if model.startswith(key):
                return MODEL_CONFIGS[key]
        
        # Try base model name (e.g., 'claude' for 'claude-3-xyz')
        base_model = model.split('-')[0]
        if base_model in MODEL_CONFIGS:
            return MODEL_CONFIGS[base_model]
        
        # Default fallback
        print(f"Warning: Unknown model '{model}', using default configuration")
        return {'encoding': 'cl100k_base', 'max_tokens': 100000}
    
    def count_tokens(self, text: str, cache_key: Optional[str] = None) -> int:
        """Count tokens with caching support"""
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key]
        
        if self.encoder:
            try:
                count = len(self.encoder.encode(text))
                if cache_key:
                    self.cache[cache_key] = count
                return count
            except:
                pass
        
        # Fallback to character-based estimation
        count = len(text) // 3
        if cache_key:
            self.cache[cache_key] = count
        return count
    
    def allocate_for_file(self, file_path: str, content: str, priority: float) -> Tuple[str, bool]:
        """Allocate tokens for a file and return potentially truncated content"""
        tokens_needed = self.count_tokens(content, cache_key=file_path)
        allocation = self.budget.allocate(file_path, tokens_needed, priority)
        
        if allocation.truncated:
            # Smart truncation based on file type
            truncated_content = self._smart_truncate(content, allocation.allocated_tokens, file_path)
            return truncated_content, True
        
        return content, False
    
    def _smart_truncate(self, content: str, max_tokens: int, file_path: str) -> str:
        """Intelligently truncate content to fit token budget"""
        # This is a simplified version - could be enhanced with AST parsing
        lines = content.splitlines()
        
        # For code files, try to preserve structure
        if any(file_path.endswith(ext) for ext in ['.py', '.js', '.ts', '.java']):
            # Keep imports and class definitions
            important_lines = []
            regular_lines = []
            
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in ['import', 'from', 'class', 'def', 'function', 'const', 'export']):
                    important_lines.append((i, line))
                else:
                    regular_lines.append((i, line))
            
            # Reconstruct with priority given to important lines
            result_lines = important_lines[:50] + regular_lines[:50]
            result_lines.sort(key=lambda x: x[0])  # Maintain order
            
            truncated = '\n'.join(line for _, line in result_lines)
            truncation_notice = f"\n[... Truncated to fit {max_tokens} tokens ...]\n"
            
            return truncated + truncation_notice
        
        # For other files, simple truncation
        estimated_chars = max_tokens * 3
        if len(content) > estimated_chars:
            return content[:estimated_chars] + "\n[... Truncated ...]\n"
        
        return content
    
    def get_statistics(self) -> Dict:
        """Get token allocation statistics"""
        return {
            'total_budget': self.budget.total,
            'tokens_used': self.budget.used,
            'tokens_remaining': self.budget.remaining,
            'files_processed': len(self.budget.allocations),
            'files_truncated': sum(1 for a in self.budget.allocations if a.truncated),
            'allocations': [
                {
                    'file': a.file_path,
                    'allocated': a.allocated_tokens,
                    'requested': a.actual_tokens,
                    'truncated': a.truncated,
                    'priority': a.priority
                }
                for a in sorted(self.budget.allocations, key=lambda x: x.priority)
            ]
        }
    
    def save_cache(self, path: Path):
        """Save token cache to disk"""
        with open(path, 'w') as f:
            json.dump(self.cache, f)
    
    def load_cache(self, path: Path):
        """Load token cache from disk"""
        if path.exists():
            with open(path, 'r') as f:
                self.cache = json.load(f)
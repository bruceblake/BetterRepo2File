"""
Advanced token management for repo2file
"""
import tiktoken
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json

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
    def __init__(self, model: str = "gpt-4", budget: int = 500000):
        self.model = model
        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except:
            # Fallback to cl100k_base encoding
            self.encoder = tiktoken.get_encoding("cl100k_base")
        
        self.budget = TokenBudget(total=budget)
        self.cache: Dict[str, int] = {}
    
    def count_tokens(self, text: str, cache_key: Optional[str] = None) -> int:
        """Count tokens with caching support"""
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            count = len(self.encoder.encode(text))
            if cache_key:
                self.cache[cache_key] = count
            return count
        except:
            # Fallback to character-based estimation
            return len(text) // 3
    
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
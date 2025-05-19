"""Context Manager for structured LLM interactions."""
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import tiktoken

from repo2file.token_manager import TokenManager


@dataclass
class LLMContext:
    """Structured context for LLM interactions."""
    task_type: str
    repository_info: Dict[str, Any]
    file_hierarchy: Dict[str, Any]
    selected_files: List[str]
    token_budget: int
    model: str
    additional_metadata: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary format."""
        return {
            'task_type': self.task_type,
            'repository_info': self.repository_info,
            'file_hierarchy': self.file_hierarchy,
            'selected_files': self.selected_files,
            'token_budget': self.token_budget,
            'model': self.model,
            'additional_metadata': self.additional_metadata,
            'constraints': self.constraints,
            'timestamp': self.timestamp.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert context to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ContextManager:
    """Manages context for LLM interactions."""
    
    def __init__(self, token_manager: Optional[TokenManager] = None):
        """Initialize the context manager."""
        self.token_manager = token_manager or TokenManager()
        self.contexts: Dict[str, LLMContext] = {}
    
    def create_context(
        self,
        task_type: str,
        repository_info: Dict[str, Any],
        file_hierarchy: Dict[str, Any],
        selected_files: List[str],
        token_budget: int,
        model: str,
        additional_metadata: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[str]] = None
    ) -> LLMContext:
        """Create a new LLM context."""
        context = LLMContext(
            task_type=task_type,
            repository_info=repository_info,
            file_hierarchy=file_hierarchy,
            selected_files=selected_files,
            token_budget=token_budget,
            model=model,
            additional_metadata=additional_metadata or {},
            constraints=constraints or []
        )
        
        # Store context with a unique ID
        context_id = f"{task_type}_{datetime.now().timestamp()}"
        self.contexts[context_id] = context
        
        return context
    
    def get_context(self, context_id: str) -> Optional[LLMContext]:
        """Retrieve a context by ID."""
        return self.contexts.get(context_id)
    
    def estimate_context_tokens(self, context: LLMContext) -> int:
        """Estimate total tokens in the context."""
        # Convert context to string representation
        context_str = context.to_json()
        
        # Use the appropriate encoding for the model
        encoding_name = self._get_encoding_for_model(context.model)
        
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(context_str))
        except Exception as e:
            # Fallback to approximate counting
            return len(context_str.split()) * 1.3
    
    def optimize_context(
        self,
        context: LLMContext,
        max_tokens: Optional[int] = None
    ) -> LLMContext:
        """Optimize context to fit within token budget."""
        if max_tokens is None:
            max_tokens = context.token_budget
        
        current_tokens = self.estimate_context_tokens(context)
        
        if current_tokens <= max_tokens:
            return context
        
        # Create a copy of the context to optimize
        optimized = LLMContext(
            task_type=context.task_type,
            repository_info=context.repository_info,
            file_hierarchy=context.file_hierarchy,
            selected_files=context.selected_files.copy(),
            token_budget=context.token_budget,
            model=context.model,
            additional_metadata=context.additional_metadata.copy(),
            constraints=context.constraints.copy()
        )
        
        # Remove files until we're under budget
        while (current_tokens > max_tokens and optimized.selected_files):
            optimized.selected_files.pop()
            current_tokens = self.estimate_context_tokens(optimized)
        
        return optimized
    
    def create_summary_context(
        self,
        context: LLMContext,
        focus_areas: List[str]
    ) -> LLMContext:
        """Create a summarized context focusing on specific areas."""
        # Filter file hierarchy based on focus areas
        filtered_hierarchy = self._filter_hierarchy(
            context.file_hierarchy,
            focus_areas
        )
        
        # Only include files relevant to focus areas
        relevant_files = [
            f for f in context.selected_files
            if any(area in f for area in focus_areas)
        ]
        
        return LLMContext(
            task_type=f"{context.task_type}_summary",
            repository_info=context.repository_info,
            file_hierarchy=filtered_hierarchy,
            selected_files=relevant_files,
            token_budget=context.token_budget // 2,  # Use half the budget
            model=context.model,
            additional_metadata={
                **context.additional_metadata,
                'focus_areas': focus_areas,
                'original_context': context.task_type
            },
            constraints=context.constraints
        )
    
    def _get_encoding_for_model(self, model: str) -> str:
        """Get the appropriate tiktoken encoding for a model."""
        model_lower = model.lower()
        
        if 'gpt-4' in model_lower:
            return 'cl100k_base'
        elif 'gpt-3.5' in model_lower:
            return 'cl100k_base'
        elif 'claude' in model_lower:
            # Claude uses the same tokenizer as GPT-4
            return 'cl100k_base'
        else:
            # Default fallback
            return 'cl100k_base'
    
    def _filter_hierarchy(
        self,
        hierarchy: Dict[str, Any],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Filter file hierarchy based on focus areas."""
        filtered = {}
        
        for key, value in hierarchy.items():
            if any(area in key.lower() for area in focus_areas):
                filtered[key] = value
            elif isinstance(value, dict):
                # Recursively filter subdirectories
                sub_filtered = self._filter_hierarchy(value, focus_areas)
                if sub_filtered:
                    filtered[key] = sub_filtered
        
        return filtered
"""AI Action Block generation and formatting for BetterRepo2File"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

class ActionBlockType(Enum):
    CALL_GRAPH_NODE = "CALL_GRAPH_NODE"
    GIT_INSIGHT = "GIT_INSIGHT"
    TODO_ITEM = "TODO_ITEM"
    PCA_NOTE = "PCA_NOTE"
    CODE_QUALITY_METRIC = "CODE_QUALITY_METRIC"

class ActionBlockFormat(Enum):
    INLINE = "inline"
    MANIFEST = "manifest"
    BOTH = "both"

@dataclass
class ActionBlock:
    """Base class for all action blocks"""
    block_type: ActionBlockType
    file: str
    
    def to_string(self) -> str:
        """Convert the action block to string format"""
        raise NotImplementedError("Subclasses must implement to_string")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the action block to dictionary format"""
        raise NotImplementedError("Subclasses must implement to_dict")

@dataclass
class CallGraphNode(ActionBlock):
    """Call graph node action block"""
    entity: str
    entity_type: str
    calls: List[str]
    called_by: List[str]
    
    def __post_init__(self):
        self.block_type = ActionBlockType.CALL_GRAPH_NODE
    
    def to_string(self) -> str:
        return (f'[{self.block_type.value} file="{self.file}" entity="{self.entity}" '
                f'type="{self.entity_type}" calls=\'{json.dumps(self.calls)}\' '
                f'called_by=\'{json.dumps(self.called_by)}\']')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.block_type.value,
            "file": self.file,
            "entity": self.entity,
            "entity_type": self.entity_type,
            "calls": self.calls,
            "called_by": self.called_by
        }

@dataclass
class GitInsight(ActionBlock):
    """Git insight action block"""
    last_mod_date: str
    last_mod_author: str
    last_commit: str
    commit_hash: str
    change_frequency_90d: int
    recent_contributors: List[str]
    
    def __post_init__(self):
        self.block_type = ActionBlockType.GIT_INSIGHT
    
    def to_string(self) -> str:
        return (f'[{self.block_type.value} file="{self.file}" '
                f'last_mod_date="{self.last_mod_date}" '
                f'last_mod_author="{self.last_mod_author}" '
                f'last_commit="{self.last_commit}" '
                f'commit_hash="{self.commit_hash}" '
                f'change_frequency_90d="{self.change_frequency_90d}" '
                f'recent_contributors=\'{json.dumps(self.recent_contributors)}\']')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.block_type.value,
            "file": self.file,
            "last_mod_date": self.last_mod_date,
            "last_mod_author": self.last_mod_author,
            "last_commit": self.last_commit,
            "commit_hash": self.commit_hash,
            "change_frequency_90d": self.change_frequency_90d,
            "recent_contributors": self.recent_contributors
        }

@dataclass
class TodoItem(ActionBlock):
    """TODO item action block"""
    line: int
    todo_type: str  # TODO, FIXME, HACK, NOTE
    text: str
    priority: str  # high, medium, low
    
    def __post_init__(self):
        self.block_type = ActionBlockType.TODO_ITEM
    
    def to_string(self) -> str:
        # Escape quotes in text for proper formatting
        escaped_text = self.text.replace('"', '\\"')
        return (f'[{self.block_type.value} file="{self.file}" line="{self.line}" '
                f'type="{self.todo_type}" text="{escaped_text}" priority="{self.priority}"]')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.block_type.value,
            "file": self.file,
            "line": self.line,
            "todo_type": self.todo_type,
            "text": self.text,
            "priority": self.priority
        }

@dataclass
class PCANote(ActionBlock):
    """Proactive Context Augmentation note action block"""
    note_type: str  # ambiguity, assumption, suggestion, clarification
    lines: str  # e.g., "100-150"
    text: str
    confidence: float
    
    def __post_init__(self):
        self.block_type = ActionBlockType.PCA_NOTE
    
    def to_string(self) -> str:
        # Escape quotes in text for proper formatting
        escaped_text = self.text.replace('"', '\\"')
        return (f'[{self.block_type.value} type="{self.note_type}" file="{self.file}" '
                f'lines="{self.lines}" text="{escaped_text}" confidence="{self.confidence}"]')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.block_type.value,
            "note_type": self.note_type,
            "file": self.file,
            "lines": self.lines,
            "text": self.text,
            "confidence": self.confidence
        }

@dataclass
class CodeQualityMetric(ActionBlock):
    """Code quality metric action block"""
    entity: str
    metric: str  # cyclomatic_complexity, loc, lloc, maintainability_index
    value: float
    threshold: float
    severity: str  # info, warning, error
    
    def __post_init__(self):
        self.block_type = ActionBlockType.CODE_QUALITY_METRIC
    
    def to_string(self) -> str:
        return (f'[{self.block_type.value} file="{self.file}" entity="{self.entity}" '
                f'metric="{self.metric}" value="{self.value}" threshold="{self.threshold}" '
                f'severity="{self.severity}"]')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.block_type.value,
            "file": self.file,
            "entity": self.entity,
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "severity": self.severity
        }

class ActionBlockGenerator:
    """Generates and formats AI action blocks"""
    
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get('enable_action_blocks', False)
        self.format = ActionBlockFormat(config.get('action_block_format', 'inline'))
        self.enabled_types = set(config.get('action_block_types', [
            'CALL_GRAPH_NODE', 'GIT_INSIGHT', 'TODO_ITEM', 'PCA_NOTE', 'CODE_QUALITY_METRIC'
        ]))
        self.filters = config.get('action_block_filters', {})
        self.blocks: List[ActionBlock] = []
    
    def add_block(self, block: ActionBlock) -> None:
        """Add an action block to the collection"""
        if not self.enabled:
            return
        
        if block.block_type.value not in self.enabled_types:
            return
        
        # Apply filters
        if self._should_filter_block(block):
            return
        
        self.blocks.append(block)
    
    def _should_filter_block(self, block: ActionBlock) -> bool:
        """Check if a block should be filtered based on configuration"""
        if isinstance(block, CodeQualityMetric):
            min_complexity = self.filters.get('min_complexity', 0)
            if block.metric == 'cyclomatic_complexity' and block.value < min_complexity:
                return True
        
        if isinstance(block, TodoItem):
            min_priority = self.filters.get('min_priority', 'low')
            priority_levels = {'low': 0, 'medium': 1, 'high': 2}
            if priority_levels.get(block.priority, 0) < priority_levels.get(min_priority, 0):
                return True
        
        if isinstance(block, CallGraphNode):
            if not self.filters.get('include_private_methods', True):
                if block.entity.startswith('_') and not block.entity.startswith('__'):
                    return True
        
        return False
    
    def generate_inline_blocks(self, file_path: str) -> List[str]:
        """Generate inline action blocks for a specific file"""
        if self.format not in [ActionBlockFormat.INLINE, ActionBlockFormat.BOTH]:
            return []
        
        file_blocks = [b for b in self.blocks if b.file == file_path]
        return [block.to_string() for block in file_blocks]
    
    def generate_manifest_section(self) -> str:
        """Generate a manifest section with aggregated action blocks"""
        if self.format not in [ActionBlockFormat.MANIFEST, ActionBlockFormat.BOTH]:
            return ""
        
        sections = []
        
        # High priority items
        high_priority = []
        for block in self.blocks:
            if isinstance(block, TodoItem) and block.priority == 'high':
                high_priority.append(block)
            elif isinstance(block, CodeQualityMetric) and block.severity == 'error':
                high_priority.append(block)
        
        if high_priority:
            sections.append("### High Priority Items")
            for block in high_priority:
                sections.append(block.to_string())
            sections.append("")
        
        # Code quality warnings
        warnings = [b for b in self.blocks 
                   if isinstance(b, CodeQualityMetric) and b.severity == 'warning']
        if warnings:
            sections.append("### Code Quality Warnings")
            for block in warnings:
                sections.append(block.to_string())
            sections.append("")
        
        # Architecture insights
        call_graphs = [b for b in self.blocks if isinstance(b, CallGraphNode)]
        if call_graphs:
            sections.append("### Architecture Insights")
            # Show the most connected nodes
            sorted_nodes = sorted(call_graphs, 
                                key=lambda x: len(x.calls) + len(x.called_by), 
                                reverse=True)[:10]
            for block in sorted_nodes:
                sections.append(block.to_string())
            sections.append("")
        
        # Git insights for frequently changed files
        git_insights = [b for b in self.blocks 
                       if isinstance(b, GitInsight) and b.change_frequency_90d > 10]
        if git_insights:
            sections.append("### Frequently Changed Files")
            for block in sorted(git_insights, key=lambda x: x.change_frequency_90d, reverse=True):
                sections.append(block.to_string())
            sections.append("")
        
        return "\n".join(sections) if sections else ""
    
    def generate_structured_output(self) -> Dict[str, Any]:
        """Generate structured JSON output for all action blocks"""
        output = {
            "action_blocks": {
                "summary": {
                    "total_blocks": len(self.blocks),
                    "by_type": {}
                },
                "blocks": []
            }
        }
        
        # Count by type
        for block_type in ActionBlockType:
            count = len([b for b in self.blocks if b.block_type == block_type])
            if count > 0:
                output["action_blocks"]["summary"]["by_type"][block_type.value] = count
        
        # Add all blocks
        output["action_blocks"]["blocks"] = [block.to_dict() for block in self.blocks]
        
        # Add high-level insights
        output["action_blocks"]["insights"] = {
            "high_priority_count": len([b for b in self.blocks 
                                       if (isinstance(b, TodoItem) and b.priority == 'high') or
                                          (isinstance(b, CodeQualityMetric) and b.severity == 'error')]),
            "most_connected_entities": self._get_most_connected_entities(),
            "most_changed_files": self._get_most_changed_files()
        }
        
        return output
    
    def _get_most_connected_entities(self) -> List[Dict[str, Any]]:
        """Get the most connected entities from call graph"""
        call_graphs = [b for b in self.blocks if isinstance(b, CallGraphNode)]
        sorted_nodes = sorted(call_graphs, 
                            key=lambda x: len(x.calls) + len(x.called_by), 
                            reverse=True)[:5]
        return [{
            "entity": node.entity,
            "file": node.file,
            "connections": len(node.calls) + len(node.called_by),
            "calls": len(node.calls),
            "called_by": len(node.called_by)
        } for node in sorted_nodes]
    
    def _get_most_changed_files(self) -> List[Dict[str, Any]]:
        """Get the most frequently changed files"""
        git_insights = [b for b in self.blocks if isinstance(b, GitInsight)]
        sorted_insights = sorted(git_insights, 
                               key=lambda x: x.change_frequency_90d, 
                               reverse=True)[:5]
        return [{
            "file": insight.file,
            "changes_90d": insight.change_frequency_90d,
            "last_author": insight.last_mod_author,
            "last_date": insight.last_mod_date
        } for insight in sorted_insights]
    
    def clear(self) -> None:
        """Clear all collected action blocks"""
        self.blocks.clear()
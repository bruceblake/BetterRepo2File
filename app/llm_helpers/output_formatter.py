"""Output formatters for LLM-specific formats."""
import json
import yaml
from enum import Enum
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET
from datetime import datetime


class FormatType(Enum):
    """Supported output format types."""
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    MARKDOWN = "markdown"
    PLAINTEXT = "plaintext"
    STRUCTURED_TEXT = "structured_text"
    CODE_BLOCKS = "code_blocks"


class OutputFormatter:
    """Formats output for different LLM consumption patterns."""
    
    def __init__(self):
        """Initialize the output formatter."""
        self.formatters = {
            FormatType.JSON: self._format_json,
            FormatType.YAML: self._format_yaml,
            FormatType.XML: self._format_xml,
            FormatType.MARKDOWN: self._format_markdown,
            FormatType.PLAINTEXT: self._format_plaintext,
            FormatType.STRUCTURED_TEXT: self._format_structured_text,
            FormatType.CODE_BLOCKS: self._format_code_blocks
        }
    
    def format_output(
        self,
        content: Dict[str, Any],
        format_type: FormatType,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format content according to specified format type."""
        formatter = self.formatters.get(format_type, self._format_plaintext)
        return formatter(content, options or {})
    
    def _format_json(self, content: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as JSON."""
        indent = options.get('indent', 2)
        ensure_ascii = options.get('ensure_ascii', False)
        
        return json.dumps(
            content,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=str
        )
    
    def _format_yaml(self, content: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as YAML."""
        default_flow_style = options.get('default_flow_style', False)
        
        return yaml.dump(
            content,
            default_flow_style=default_flow_style,
            sort_keys=False
        )
    
    def _format_xml(self, content: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as XML."""
        root_name = options.get('root_name', 'repository_context')
        
        root = ET.Element(root_name)
        self._dict_to_xml(content, root)
        
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def _dict_to_xml(self, data: Any, parent: ET.Element) -> None:
        """Convert dictionary to XML elements recursively."""
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(parent, key)
                self._dict_to_xml(value, child)
        elif isinstance(data, list):
            for item in data:
                self._dict_to_xml(item, parent)
        else:
            parent.text = str(data)
    
    def _format_markdown(self, content: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as Markdown."""
        sections = []
        
        # Title
        title = content.get('repository_name', 'Repository Context')
        sections.append(f"# {title}")
        
        # Metadata
        if 'metadata' in content:
            sections.append("\n## Metadata")
            for key, value in content['metadata'].items():
                sections.append(f"- **{key}**: {value}")
        
        # File Structure
        if 'file_hierarchy' in content:
            sections.append("\n## File Structure")
            sections.append("```")
            sections.append(self._format_hierarchy(content['file_hierarchy']))
            sections.append("```")
        
        # Files
        if 'files' in content:
            sections.append("\n## Files")
            for file_info in content['files']:
                sections.append(f"\n### {file_info['path']}")
                if 'content' in file_info:
                    sections.append(f"```{file_info.get('language', '')}")
                    sections.append(file_info['content'])
                    sections.append("```")
        
        # Summary
        if 'summary' in content:
            sections.append("\n## Summary")
            sections.append(content['summary'])
        
        return "\n".join(sections)
    
    def _format_plaintext(self, content: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as plain text."""
        lines = []
        
        # Header
        lines.append("=" * 50)
        lines.append(f"Repository: {content.get('repository_name', 'Unknown')}")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append("=" * 50)
        
        # Metadata section
        if 'metadata' in content:
            lines.append("\nMETADATA:")
            for key, value in content['metadata'].items():
                lines.append(f"  {key}: {value}")
        
        # File structure
        if 'file_hierarchy' in content:
            lines.append("\nFILE STRUCTURE:")
            lines.append(self._format_hierarchy(content['file_hierarchy'], indent="  "))
        
        # Files content
        if 'files' in content:
            lines.append("\nFILES:")
            for file_info in content['files']:
                lines.append(f"\n--- {file_info['path']} ---")
                if 'content' in file_info:
                    lines.append(file_info['content'])
                lines.append("--- END FILE ---")
        
        return "\n".join(lines)
    
    def _format_structured_text(self, content: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as structured text with clear sections."""
        sections = []
        use_separators = options.get('use_separators', True)
        
        # Repository info
        sections.append(f"REPOSITORY: {content.get('repository_name', 'Unknown')}")
        sections.append(f"TIMESTAMP: {datetime.now().isoformat()}")
        
        if use_separators:
            sections.append("-" * 40)
        
        # Task context
        if 'task_type' in content:
            sections.append(f"TASK: {content['task_type']}")
            if 'task_description' in content:
                sections.append(f"DESCRIPTION: {content['task_description']}")
        
        if use_separators:
            sections.append("-" * 40)
        
        # File listing
        if 'files' in content:
            sections.append("FILES INCLUDED:")
            for i, file_info in enumerate(content['files'], 1):
                sections.append(f"{i}. {file_info['path']} ({file_info.get('size', 0)} bytes)")
        
        if use_separators:
            sections.append("-" * 40)
        
        # Content sections
        if 'files' in content:
            for file_info in content['files']:
                sections.append(f"FILE: {file_info['path']}")
                sections.append(f"TYPE: {file_info.get('type', 'unknown')}")
                if 'content' in file_info:
                    sections.append("CONTENT:")
                    sections.append(file_info['content'])
                if use_separators:
                    sections.append("-" * 40)
        
        return "\n".join(sections)
    
    def _format_code_blocks(self, content: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as code blocks with language hints."""
        blocks = []
        
        # Header comment
        comment_style = options.get('comment_style', '#')
        blocks.append(f"{comment_style} Repository: {content.get('repository_name', 'Unknown')}")
        blocks.append(f"{comment_style} Generated: {datetime.now().isoformat()}")
        blocks.append("")
        
        # Files as code blocks
        if 'files' in content:
            for file_info in content['files']:
                # File header
                blocks.append(f"{comment_style} File: {file_info['path']}")
                
                # Language detection
                language = self._detect_language(file_info['path'])
                
                # Content block
                if 'content' in file_info:
                    blocks.append(f"```{language}")
                    blocks.append(file_info['content'])
                    blocks.append("```")
                    blocks.append("")
        
        return "\n".join(blocks)
    
    def _format_hierarchy(
        self,
        hierarchy: Dict[str, Any],
        indent: str = "",
        is_last: bool = True
    ) -> str:
        """Format file hierarchy as tree structure."""
        lines = []
        items = list(hierarchy.items())
        
        for i, (name, value) in enumerate(items):
            is_last_item = i == len(items) - 1
            
            # Tree characters
            prefix = "└── " if is_last_item else "├── "
            lines.append(f"{indent}{prefix}{name}")
            
            # Recurse for directories
            if isinstance(value, dict) and value:
                extension = "    " if is_last_item else "│   "
                sub_tree = self._format_hierarchy(
                    value,
                    indent + extension,
                    is_last_item
                )
                lines.append(sub_tree)
        
        return "\n".join(lines)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file path."""
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'objc',
            '.mm': 'objcpp',
            '.pl': 'perl',
            '.sh': 'bash',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.md': 'markdown',
            '.rst': 'rst',
            '.tex': 'latex'
        }
        
        import os
        _, ext = os.path.splitext(file_path)
        return extensions.get(ext.lower(), '')
    
    def create_llm_context(
        self,
        repository_info: Dict[str, Any],
        file_contents: List[Dict[str, Any]],
        task_context: Optional[Dict[str, Any]] = None,
        format_type: FormatType = FormatType.STRUCTURED_TEXT
    ) -> str:
        """Create a complete LLM context from repository data."""
        context = {
            'repository_name': repository_info.get('name', 'Unknown'),
            'metadata': repository_info.get('metadata', {}),
            'file_hierarchy': repository_info.get('hierarchy', {}),
            'files': file_contents
        }
        
        if task_context:
            context.update(task_context)
        
        return self.format_output(context, format_type)
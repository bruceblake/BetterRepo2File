"""
Semantic code analyzer for intelligent content selection
"""
import ast
import re
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
import json
import string

@dataclass
class CodeEntity:
    name: str
    type: str  # 'class', 'function', 'method', 'variable'
    line_start: int
    line_end: int
    dependencies: Set[str] = None
    importance_score: float = 0.0
    calls: List[str] = None  # Functions/methods this entity calls
    called_by: List[str] = None  # Functions/methods that call this entity
    docstring: str = None  # Entity's docstring if available
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = set()
        if self.calls is None:
            self.calls = []
        if self.called_by is None:
            self.called_by = []

class CodeAnalyzer:
    def __init__(self):
        self.language_parsers = {
            '.py': self._analyze_python,
            '.js': self._analyze_javascript,
            '.ts': self._analyze_typescript,
            '.java': self._analyze_java,
        }
        
    def analyze_file(self, file_path: Path, content: str) -> Dict:
        """Analyze a code file and extract semantic information"""
        suffix = file_path.suffix.lower()
        
        if suffix in self.language_parsers:
            return self.language_parsers[suffix](content)
        
        return self._generic_analysis(content)
    
    def _analyze_python(self, content: str) -> Dict:
        """Analyze Python code using AST"""
        entities = []
        imports = []
        
        try:
            tree = ast.parse(content)
            
            # First pass: collect all entities
            entity_map = {}  # name -> entity mapping
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    entity = CodeEntity(
                        name=node.name,
                        type='class',
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        importance_score=0.8
                    )
                    # Extract docstring
                    entity.docstring = ast.get_docstring(node)
                    
                    # Find methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_entity = CodeEntity(
                                name=f"{node.name}.{item.name}",
                                type='method',
                                line_start=item.lineno,
                                line_end=item.end_lineno or item.lineno,
                                importance_score=0.6
                            )
                            method_entity.docstring = ast.get_docstring(item)
                            if item.name in ['__init__', '__call__']:
                                method_entity.importance_score = 0.8
                            entities.append(method_entity)
                            entity_map[method_entity.name] = method_entity
                            
                            # Find calls within this method
                            self._extract_calls(item, method_entity, entity_map)
                    
                    entities.append(entity)
                    entity_map[entity.name] = entity
                    
                elif isinstance(node, ast.FunctionDef):
                    if node.col_offset == 0:  # Top-level function
                        entity = CodeEntity(
                            name=node.name,
                            type='function',
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            importance_score=0.7
                        )
                        entity.docstring = ast.get_docstring(node)
                        entities.append(entity)
                        entity_map[entity.name] = entity
                        
                        # Find calls within this function
                        self._extract_calls(node, entity, entity_map)
                        
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        # Track specific imports for better call resolution
                        for alias in node.names:
                            imports.append(f"{node.module}.{alias.name}")
            
            # Analyze dependencies
            for entity in entities:
                entity.dependencies = self._find_dependencies(
                    content[entity.line_start:entity.line_end], 
                    imports
                )
            
        except SyntaxError:
            # Fallback to regex-based analysis
            return self._python_regex_analysis(content)
        
        return {
            'entities': entities,
            'imports': imports,
            'language': 'python',
            'metrics': self._calculate_metrics(entities, content)
        }
    
    def _extract_calls(self, node: ast.AST, entity: CodeEntity, entity_map: Dict[str, CodeEntity]) -> None:
        """Extract function/method calls within an AST node"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Function call
                call_name = None
                
                # Direct function call
                if isinstance(child.func, ast.Name):
                    call_name = child.func.id
                # Method call
                elif isinstance(child.func, ast.Attribute):
                    # Try to reconstruct the full name
                    if isinstance(child.func.value, ast.Name):
                        call_name = f"{child.func.value.id}.{child.func.attr}"
                    elif (hasattr(ast, 'Self') and isinstance(child.func.value, ast.Self)) or \
                         (hasattr(child.func.value, 'id') and child.func.value.id == 'self'):
                        call_name = f"self.{child.func.attr}"
                    else:
                        call_name = child.func.attr
                
                if call_name:
                    entity.calls.append(call_name)
                    
                    # If this is a call to an entity we know about, update its called_by
                    if call_name in entity_map:
                        entity_map[call_name].called_by.append(entity.name)
    
    def _find_dependencies(self, code_block: str, known_imports: List[str]) -> Set[str]:
        """Find dependencies within a code block"""
        dependencies = set()
        
        # Look for function calls and class instantiations
        pattern = r'(\w+)\s*\('
        for match in re.finditer(pattern, code_block):
            name = match.group(1)
            if name in known_imports:
                dependencies.add(name)
        
        return dependencies
    
    def _calculate_metrics(self, entities: List[CodeEntity], content: str) -> Dict:
        """Calculate code metrics"""
        lines = content.splitlines()
        total_lines = len(lines)
        
        # Calculate code density (non-empty, non-comment lines)
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'entities_count': len(entities),
            'avg_entity_size': sum(e.line_end - e.line_start for e in entities) / len(entities) if entities else 0,
            'complexity_score': len(entities) / total_lines if total_lines > 0 else 0
        }
    
    def _analyze_javascript(self, content: str) -> Dict:
        """Analyze JavaScript/TypeScript code"""
        # Simplified regex-based analysis
        entities = []
        
        # Find classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*{'
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            entities.append(CodeEntity(
                name=match.group(1),
                type='class',
                line_start=line_num,
                line_end=line_num,  # Would need more parsing for accurate end
                importance_score=0.8
            ))
        
        # Find functions
        func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)'
        for match in re.finditer(func_pattern, content):
            name = match.group(1) or match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            entities.append(CodeEntity(
                name=name,
                type='function',
                line_start=line_num,
                line_end=line_num,
                importance_score=0.7
            ))
        
        # Find imports
        import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
        imports = re.findall(import_pattern, content)
        
        return {
            'entities': entities,
            'imports': imports,
            'language': 'javascript',
            'metrics': self._calculate_metrics(entities, content)
        }
    
    def _analyze_typescript(self, content: str) -> Dict:
        """Analyze TypeScript code"""
        # Use JavaScript analyzer with additional TypeScript patterns
        result = self._analyze_javascript(content)
        
        # Find interfaces
        interface_pattern = r'interface\s+(\w+)\s*{'
        for match in re.finditer(interface_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            result['entities'].append(CodeEntity(
                name=match.group(1),
                type='interface',
                line_start=line_num,
                line_end=line_num,
                importance_score=0.6
            ))
        
        # Find type definitions
        type_pattern = r'type\s+(\w+)\s*='
        for match in re.finditer(type_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            result['entities'].append(CodeEntity(
                name=match.group(1),
                type='type',
                line_start=line_num,
                line_end=line_num,
                importance_score=0.5
            ))
        
        result['language'] = 'typescript'
        return result
    
    def _analyze_java(self, content: str) -> Dict:
        """Analyze Java code"""
        entities = []
        imports = []
        
        # Find package
        package_match = re.search(r'package\s+([\w.]+);', content)
        package = package_match.group(1) if package_match else None
        
        # Find imports
        import_pattern = r'import\s+([\w.]+);'
        imports = re.findall(import_pattern, content)
        
        # Find classes
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?\s*{'
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            entities.append(CodeEntity(
                name=match.group(1),
                type='class',
                line_start=line_num,
                line_end=line_num,
                importance_score=0.8
            ))
        
        # Find methods
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*{'
        for match in re.finditer(method_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            entities.append(CodeEntity(
                name=match.group(1),
                type='method',
                line_start=line_num,
                line_end=line_num,
                importance_score=0.6
            ))
        
        return {
            'entities': entities,
            'imports': imports,
            'package': package,
            'language': 'java',
            'metrics': self._calculate_metrics(entities, content)
        }
    
    def _generic_analysis(self, content: str) -> Dict:
        """Generic analysis for unknown file types"""
        lines = content.splitlines()
        
        # Look for common patterns
        entities = []
        
        # Function-like patterns
        func_patterns = [
            r'def\s+(\w+)',  # Python
            r'function\s+(\w+)',  # JavaScript
            r'func\s+(\w+)',  # Go
            r'fn\s+(\w+)',  # Rust
        ]
        
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                entities.append(CodeEntity(
                    name=match.group(1),
                    type='function',
                    line_start=line_num,
                    line_end=line_num,
                    importance_score=0.5
                ))
        
        return {
            'entities': entities,
            'imports': [],
            'language': 'unknown',
            'metrics': {
                'total_lines': len(lines),
                'entities_count': len(entities)
            }
        }
    
    def calculate_file_importance(self, analysis: Dict, file_path: Path) -> float:
        """Calculate overall file importance based on analysis"""
        score = 0.0
        
        # Base score from file name
        if file_path.name in ['main.py', 'index.js', 'app.py', 'server.js']:
            score += 0.3
        elif file_path.name.startswith('test_') or '_test' in file_path.name:
            score -= 0.2
        
        # Score from entities
        if 'entities' in analysis:
            entity_score = sum(e.importance_score for e in analysis['entities'])
            score += min(entity_score / 10, 0.5)  # Cap at 0.5
        
        # Score from metrics
        if 'metrics' in analysis:
            metrics = analysis['metrics']
            if metrics.get('complexity_score', 0) > 0.1:
                score += 0.2
        
        # Score from imports (indicates interconnection)
        if 'imports' in analysis and len(analysis['imports']) > 5:
            score += 0.1
        
        return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
    
    def calculate_query_relevance(self, query: str, file_path: Path, content: str, analysis: Dict) -> float:
        """Calculate how relevant a file is to the intended query"""
        if not query:
            return 0.0
        
        # Normalize query for comparison
        query_lower = query.lower()
        query_words = set(word for word in query_lower.split() 
                         if len(word) > 2 and word not in {'the', 'and', 'for', 'with', 'that'})
        
        relevance_score = 0.0
        
        # Check file path relevance
        path_str = str(file_path).lower()
        for word in query_words:
            if word in path_str:
                relevance_score += 0.3
        
        # Check file name relevance
        filename = file_path.name.lower()
        for word in query_words:
            if word in filename:
                relevance_score += 0.4
        
        # Check content relevance (sample for performance)
        content_lower = content[:5000].lower()  # Only check first 5000 chars for performance
        content_words = set(content_lower.split())
        
        # Count query word occurrences
        matches = sum(1 for word in query_words if word in content_words)
        if matches > 0:
            relevance_score += min(matches * 0.1, 0.3)
        
        # Check entity names (classes, functions)
        if 'entities' in analysis:
            entity_names = {entity.name.lower() for entity in analysis['entities']}
            for word in query_words:
                for entity_name in entity_names:
                    if word in entity_name or entity_name in word:
                        relevance_score += 0.2
                        break
        
        # Bonus for specific patterns
        if any(pattern in query_lower for pattern in ['refactor', 'modify', 'change', 'update']):
            # User wants to modify code - boost files with complex logic
            if analysis.get('metrics', {}).get('complexity_score', 0) > 0.1:
                relevance_score += 0.1
        
        if any(pattern in query_lower for pattern in ['test', 'testing', 'unit test']):
            # User wants tests - boost test files
            if 'test' in filename or 'spec' in filename:
                relevance_score += 0.5
        
        if any(pattern in query_lower for pattern in ['api', 'endpoint', 'route']):
            # User interested in APIs
            if any(word in filename for word in ['api', 'route', 'controller', 'view']):
                relevance_score += 0.3
        
        return min(relevance_score, 1.0)  # Cap at 1.0
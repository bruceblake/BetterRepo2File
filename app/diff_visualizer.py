import difflib
from typing import List, Tuple, Dict, Optional
import json
from pathlib import Path
import git

class DiffVisualizer:
    """Visualize code changes and diffs for iteration workflows"""
    
    def __init__(self, repo_path: str = '.'):
        self.repo_path = Path(repo_path)
        try:
            self.repo = git.Repo(repo_path)
        except:
            self.repo = None
    
    def get_file_diff(self, file_path: str, original_content: str, modified_content: str) -> Dict:
        """Generate diff between original and modified content"""
        original_lines = original_content.splitlines(keepends=True)
        modified_lines = modified_content.splitlines(keepends=True)
        
        # Generate unified diff
        diff = list(difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f'original/{file_path}',
            tofile=f'modified/{file_path}',
            lineterm=''
        ))
        
        # Generate side-by-side comparison
        html_diff = difflib.HtmlDiff()
        html_table = html_diff.make_table(
            original_lines,
            modified_lines,
            fromdesc='Original',
            todesc='Modified',
            context=True,
            numlines=3
        )
        
        # Calculate statistics
        additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        return {
            'file_path': file_path,
            'unified_diff': '\n'.join(diff),
            'html_diff': html_table,
            'statistics': {
                'additions': additions,
                'deletions': deletions,
                'total_changes': additions + deletions
            },
            'chunks': self._parse_diff_chunks(diff)
        }
    
    def _parse_diff_chunks(self, diff_lines: List[str]) -> List[Dict]:
        """Parse diff into chunks for better visualization"""
        chunks = []
        current_chunk = None
        
        for line in diff_lines:
            if line.startswith('@@'):
                # New chunk
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Parse chunk header
                parts = line.split('@@')
                if len(parts) >= 2:
                    ranges = parts[1].strip()
                    current_chunk = {
                        'header': line,
                        'ranges': ranges,
                        'lines': []
                    }
            elif current_chunk:
                current_chunk['lines'].append(line)
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def get_git_diff(self, commit1: Optional[str] = None, commit2: Optional[str] = None) -> Dict:
        """Get diff between two commits or working directory"""
        if not self.repo:
            return {'error': 'Not a git repository'}
        
        try:
            if commit1 and commit2:
                diff_index = self.repo.tree(commit1).diff(commit2)
            elif commit1:
                diff_index = self.repo.tree(commit1).diff(None)  # Compare with working directory
            else:
                diff_index = self.repo.head.commit.diff(None)  # Compare HEAD with working directory
            
            diffs = []
            for diff_item in diff_index:
                # Get file contents
                if diff_item.a_blob:
                    a_content = diff_item.a_blob.data_stream.read().decode('utf-8', errors='ignore')
                else:
                    a_content = ''
                
                if diff_item.b_blob:
                    b_content = diff_item.b_blob.data_stream.read().decode('utf-8', errors='ignore')
                else:
                    b_content = ''
                
                file_diff = self.get_file_diff(
                    diff_item.a_path or diff_item.b_path,
                    a_content,
                    b_content
                )
                
                file_diff['change_type'] = diff_item.change_type
                diffs.append(file_diff)
            
            return {
                'commit1': commit1 or 'HEAD',
                'commit2': commit2 or 'Working Directory',
                'files': diffs,
                'summary': {
                    'files_changed': len(diffs),
                    'total_additions': sum(d['statistics']['additions'] for d in diffs),
                    'total_deletions': sum(d['statistics']['deletions'] for d in diffs)
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_staged_diff(self) -> Dict:
        """Get diff of staged changes"""
        if not self.repo:
            return {'error': 'Not a git repository'}
        
        try:
            staged_diff = self.repo.index.diff('HEAD')
            diffs = []
            
            for diff_item in staged_diff:
                if diff_item.a_blob:
                    a_content = diff_item.a_blob.data_stream.read().decode('utf-8', errors='ignore')
                else:
                    a_content = ''
                
                if diff_item.b_blob:
                    b_content = diff_item.b_blob.data_stream.read().decode('utf-8', errors='ignore')
                else:
                    b_content = ''
                
                file_diff = self.get_file_diff(
                    diff_item.a_path or diff_item.b_path,
                    a_content,
                    b_content
                )
                
                file_diff['change_type'] = diff_item.change_type
                diffs.append(file_diff)
            
            return {
                'type': 'staged',
                'files': diffs,
                'summary': {
                    'files_changed': len(diffs),
                    'total_additions': sum(d['statistics']['additions'] for d in diffs),
                    'total_deletions': sum(d['statistics']['deletions'] for d in diffs)
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_diff_for_display(self, diff_data: Dict) -> str:
        """Format diff data for console display"""
        output = []
        
        if 'error' in diff_data:
            return f"Error: {diff_data['error']}"
        
        # Summary
        summary = diff_data.get('summary', {})
        output.append(f"Files changed: {summary.get('files_changed', 0)}")
        output.append(f"Additions: +{summary.get('total_additions', 0)}")
        output.append(f"Deletions: -{summary.get('total_deletions', 0)}")
        output.append("")
        
        # Files
        for file_diff in diff_data.get('files', []):
            output.append(f"=== {file_diff['file_path']} ===")
            output.append(f"Changes: +{file_diff['statistics']['additions']} "
                         f"-{file_diff['statistics']['deletions']}")
            output.append("")
            output.append(file_diff['unified_diff'])
            output.append("")
        
        return '\n'.join(output)


# Global diff visualizer instance
diff_visualizer = DiffVisualizer()

# Convenience functions
def get_file_diff(file_path: str, original_content: str, modified_content: str) -> Dict:
    return diff_visualizer.get_file_diff(file_path, original_content, modified_content)

def get_git_diff(commit1: Optional[str] = None, commit2: Optional[str] = None) -> Dict:
    return diff_visualizer.get_git_diff(commit1, commit2)

def get_staged_diff() -> Dict:
    return diff_visualizer.get_staged_diff()

def format_diff_for_display(diff_data: Dict) -> str:
    return diff_visualizer.format_diff_for_display(diff_data)
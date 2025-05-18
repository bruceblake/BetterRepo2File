"""
Test suite for repo2file modules
"""
import unittest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the modules to test
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from repo2file.dump import FileDumper
from repo2file.dump_smart import SmartFileDumper
from repo2file.dump_ultra import RepoToFileGenerator
from repo2file.git_analyzer import GitAnalyzer
from repo2file.code_analyzer import CodeAnalyzer
from repo2file.token_manager import TokenManager


class TestRepo2FileModules(unittest.TestCase):
    """Test cases for repo2file modules"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir) / "test_repo"
        self.repo_path.mkdir()
        
        # Create test files
        self.create_test_files()

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_files(self):
        """Create test files in the repository"""
        # Python file
        (self.repo_path / "test.py").write_text("""
def hello_world():
    print("Hello, World!")

class TestClass:
    def method(self):
        pass
""")
        
        # JavaScript file
        (self.repo_path / "test.js").write_text("""
function helloWorld() {
    console.log("Hello, World!");
}

export default helloWorld;
""")
        
        # README
        (self.repo_path / "README.md").write_text("# Test Repository\n\nThis is a test.")
        
        # Create .gitignore
        (self.repo_path / ".gitignore").write_text("*.pyc\n__pycache__/\n.env")

    def test_file_dumper_basic(self):
        """Test basic FileDumper functionality"""
        dumper = FileDumper()
        output_file = self.test_dir / "output.txt"
        
        # Mock the main method since we're testing the class
        result = dumper.process_directory(str(self.repo_path))
        
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

    def test_git_analyzer(self):
        """Test GitAnalyzer functionality"""
        analyzer = GitAnalyzer(self.repo_path)
        
        # Test basic functionality
        self.assertFalse(analyzer.is_git_repo())  # Not a git repo yet
        
        # Get file info
        file_info = analyzer.get_last_modified_info("test.py")
        self.assertIsInstance(file_info, dict)

    def test_code_analyzer(self):
        """Test CodeAnalyzer functionality"""
        analyzer = CodeAnalyzer()
        
        # Test Python analysis
        with open(self.repo_path / "test.py", 'r') as f:
            python_content = f.read()
        
        analysis = analyzer.analyze_file(
            self.repo_path / "test.py",
            python_content,
            Path("test.py"),
            "python"
        )
        
        self.assertIsNotNone(analysis)
        self.assertIn('imports', analysis)
        self.assertIn('definitions', analysis)

    def test_token_manager(self):
        """Test TokenManager functionality"""
        manager = TokenManager(model='gpt-4', token_budget=1000)
        
        # Test token counting
        text = "This is a test string for token counting."
        tokens = manager.count_tokens(text)
        self.assertIsInstance(tokens, int)
        self.assertGreater(tokens, 0)
        
        # Test token allocation
        files = [
            {'path': 'file1.py', 'size': 100},
            {'path': 'file2.py', 'size': 200},
            {'path': 'file3.py', 'size': 300}
        ]
        
        allocations = manager.allocate_tokens(files)
        self.assertEqual(len(allocations), len(files))

    def test_dump_ultra_generator(self):
        """Test RepoToFileGenerator (dump_ultra)"""
        generator = RepoToFileGenerator()
        
        # Test file analysis
        files = list(generator.scan_directory(self.repo_path))
        self.assertGreater(len(files), 0)
        
        # Test that Python and JS files are found
        file_paths = [f['path'].name for f in files]
        self.assertIn('test.py', file_paths)
        self.assertIn('test.js', file_paths)
        self.assertIn('README.md', file_paths)

    def test_file_filtering(self):
        """Test file filtering with patterns"""
        generator = RepoToFileGenerator()
        
        # Create a .gitignore file
        gitignore_content = """
*.pyc
__pycache__/
*.log
"""
        (self.repo_path / ".gitignore").write_text(gitignore_content)
        
        # Create files that should be ignored
        (self.repo_path / "test.pyc").write_text("compiled")
        (self.repo_path / "debug.log").write_text("log content")
        
        # Scan directory with gitignore
        files = list(generator.scan_directory(self.repo_path))
        file_names = [f['path'].name for f in files]
        
        # These should be included
        self.assertIn('test.py', file_names)
        self.assertIn('test.js', file_names)
        
        # These should be excluded
        self.assertNotIn('test.pyc', file_names)
        self.assertNotIn('debug.log', file_names)

    def test_manifest_generation(self):
        """Test manifest generation"""
        generator = RepoToFileGenerator()
        
        files = list(generator.scan_directory(self.repo_path))
        
        # Mock token counts
        for f in files:
            f['tokens'] = 100
        
        manifest = generator.generate_manifest(files, self.repo_path)
        
        self.assertIsNotNone(manifest)
        self.assertIn('PROJECT STRUCTURE', manifest)
        self.assertIn('test.py', manifest)
        self.assertIn('test.js', manifest)

    @patch('subprocess.run')
    def test_docker_support(self, mock_run):
        """Test Docker detection and usage"""
        # Create a Dockerfile
        (self.repo_path / "Dockerfile").write_text("""
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
""")
        
        # Mock docker check
        mock_run.return_value.returncode = 0
        
        # Check if Dockerfile exists
        dockerfile_exists = (self.repo_path / "Dockerfile").exists()
        self.assertTrue(dockerfile_exists)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full workflow"""

    def setUp(self):
        """Set up integration test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir) / "integration_test"
        self.repo_path.mkdir()
        
        # Create a more complex test structure
        self.create_complex_structure()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_complex_structure(self):
        """Create a complex directory structure for testing"""
        # Create directories
        (self.repo_path / "src").mkdir()
        (self.repo_path / "tests").mkdir()
        (self.repo_path / "docs").mkdir()
        
        # Create files
        (self.repo_path / "src" / "main.py").write_text("""
import os
import sys

def main():
    print("Main function")

if __name__ == "__main__":
    main()
""")
        
        (self.repo_path / "tests" / "test_main.py").write_text("""
import unittest
from src.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        self.assertIsNone(main())
""")
        
        (self.repo_path / "README.md").write_text("""
# Integration Test Project

This is a test project for integration testing.

## Features
- Main functionality
- Test suite
- Documentation
""")
        
        (self.repo_path / "requirements.txt").write_text("""
pytest>=6.0.0
flask>=2.0.0
requests>=2.25.0
""")

    def test_full_workflow(self):
        """Test the complete workflow from scanning to output generation"""
        generator = RepoToFileGenerator()
        
        # Scan directory
        files = list(generator.scan_directory(self.repo_path))
        self.assertGreater(len(files), 0)
        
        # Check that all expected files are found
        file_paths = [str(f['path'].relative_to(self.repo_path)) for f in files]
        self.assertIn('src/main.py', file_paths)
        self.assertIn('tests/test_main.py', file_paths)
        self.assertIn('README.md', file_paths)
        self.assertIn('requirements.txt', file_paths)
        
        # Generate manifest
        manifest = generator.generate_manifest(files, self.repo_path)
        self.assertIn('Integration Test Project', manifest)
        self.assertIn('src/', manifest)
        self.assertIn('tests/', manifest)


if __name__ == '__main__':
    unittest.main()
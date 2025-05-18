#!/usr/bin/env python3
"""
Test script for Docker test runner functionality
"""
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from repo2file.test_runner import (
    check_docker_available,
    build_test_docker_image,
    run_tests_in_docker,
    parse_docker_test_results,
    run_project_tests
)


class TestDockerRunner(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    @patch('subprocess.run')
    def test_check_docker_available(self, mock_run):
        # Test when Docker is available
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(check_docker_available())
        
        # Test when Docker is not available
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(check_docker_available())
        
        # Test when Docker command not found
        mock_run.side_effect = FileNotFoundError()
        self.assertFalse(check_docker_available())
    
    @patch('subprocess.run')
    def test_build_docker_image(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = build_test_docker_image(self.test_path)
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    @patch('tempfile.TemporaryDirectory')
    def test_run_tests_in_docker(self, mock_tempdir, mock_run):
        # Mock temporary directory
        mock_temp = MagicMock()
        mock_temp.__enter__.return_value = self.test_dir
        mock_temp.__exit__.return_value = None
        mock_tempdir.return_value = mock_temp
        
        # Mock Docker run
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Test output",
            stderr=""
        )
        
        result = run_tests_in_docker(self.test_path, 'pytest')
        
        self.assertTrue(result['passed'])
        self.assertEqual(result['docker'], True)
        self.assertEqual(result['framework'], 'pytest')
        mock_run.assert_called_once()
    
    def test_parse_docker_test_results(self):
        # Create test results directory
        results_dir = Path(self.test_dir) / 'results'
        results_dir.mkdir()
        
        # Create mock pytest report
        pytest_report = {
            "summary": {
                "total": 5,
                "passed": 4,
                "failed": 1,
                "error": 0
            },
            "tests": [
                {
                    "nodeid": "test_example.py::test_function",
                    "outcome": "passed",
                    "duration": 0.123
                }
            ]
        }
        
        import json
        with open(results_dir / 'pytest_report.json', 'w') as f:
            json.dump(pytest_report, f)
        
        results = parse_docker_test_results(results_dir, 'pytest')
        
        self.assertEqual(results['tests_run'], 5)
        self.assertEqual(results['tests_passed'], 4)
        self.assertEqual(results['tests_failed'], 1)
        self.assertEqual(len(results['details']), 1)
    
    @patch('repo2file.test_runner.check_docker_available')
    @patch('repo2file.test_runner.run_tests_in_docker')
    def test_run_project_tests_docker_mode(self, mock_docker_run, mock_docker_check):
        mock_docker_check.return_value = True
        mock_docker_run.return_value = {
            'passed': True,
            'docker': True,
            'framework': 'pytest'
        }
        
        result = run_project_tests(
            self.test_path,
            use_docker=True
        )
        
        self.assertTrue(result['passed'])
        self.assertTrue(result['docker'])
        mock_docker_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_project_tests_local_mode(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="1 passed",
            stderr=""
        )
        
        result = run_project_tests(
            self.test_path,
            test_command="pytest",
            use_docker=False
        )
        
        self.assertTrue(result['passed'])
        self.assertFalse(result['docker'])
        self.assertEqual(result['command'], 'pytest')


if __name__ == '__main__':
    unittest.main()
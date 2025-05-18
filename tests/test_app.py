"""
Test suite for BetterRepo2File Flask application
"""
import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from app.app import app, jobs, job_queues
import queue


class TestBetterRepo2FileApp(unittest.TestCase):
    """Test cases for the Flask application"""

    def setUp(self):
        """Set up test client and temporary directories"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Create temporary directories
        self.temp_upload = tempfile.mkdtemp()
        self.temp_jobs = tempfile.mkdtemp()
        
        self.app.config['UPLOAD_FOLDER'] = self.temp_upload
        self.app.config['JOBS_FOLDER'] = self.temp_jobs
        
        # Clear jobs and queues
        jobs.clear()
        job_queues.clear()

    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.temp_upload, ignore_errors=True)
        shutil.rmtree(self.temp_jobs, ignore_errors=True)
        jobs.clear()
        job_queues.clear()

    def test_index_route(self):
        """Test the main index page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BetterRepo2File', response.data)

    def test_analyze_endpoint(self):
        """Test the /api/analyze endpoint"""
        data = {
            'vibe': 'Test feature implementation',
            'stage': 'A',
            'repo_url': 'https://github.com/test/repo',
            'repo_branch': 'main'
        }
        
        response = self.client.post('/api/analyze', data=data)
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertIn('job_id', result)
        self.assertIn('session_id', result)
        self.assertTrue(result['session_id'] in str(jobs))

    def test_generate_context_endpoint(self):
        """Test the /api/generate_context endpoint"""
        data = {
            'repo_url': 'https://github.com/test/repo',
            'vibe': 'Test vibe',
            'stage': 'A'
        }
        
        response = self.client.post('/api/generate_context',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertIn('job_id', result)

    def test_get_commits_endpoint(self):
        """Test the /api/get-commits endpoint"""
        data = {
            'repo_path': 'https://github.com/test/repo',
            'session_id': 'test-session'
        }
        
        response = self.client.post('/api/get-commits',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        # Should return 404 since no repo exists for this session
        self.assertEqual(response.status_code, 404)

    @patch('subprocess.run')
    def test_run_tests_endpoint(self, mock_run):
        """Test the /api/run-tests endpoint"""
        # Mock subprocess response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "5 passed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        data = {
            'repo_path': '.',
            'session_id': 'test-session',
            'framework': 'auto',
            'use_docker': False
        }
        
        response = self.client.post('/api/run-tests',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])

    def test_check_docker_endpoint(self):
        """Test the /api/check-docker endpoint"""
        response = self.client.get('/api/check-docker')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertIn('can_use_docker', result)

    def test_detect_docker_endpoint(self):
        """Test the /api/detect-docker endpoint"""
        data = {
            'repo_path': '.',
            'session_id': 'test-session'
        }
        
        response = self.client.post('/api/detect-docker',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('docker_available', result)
        self.assertIn('has_dockerfile', result)
        self.assertIn('has_compose', result)

    def test_status_endpoint(self):
        """Test the /api/status/<job_id> SSE endpoint"""
        job_id = 'test-job-123'
        job_queues[job_id] = queue.Queue()
        
        # Test with invalid job ID
        response = self.client.get('/api/status/invalid-job')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/event-stream')

    def test_result_endpoint(self):
        """Test the /api/result/<job_id> endpoint"""
        job_id = 'test-job-123'
        
        # Test with invalid job ID
        response = self.client.get(f'/api/result/{job_id}')
        self.assertEqual(response.status_code, 404)
        
        # Test with valid job that's still processing
        jobs[job_id] = {'status': 'processing'}
        response = self.client.get(f'/api/result/{job_id}')
        self.assertEqual(response.status_code, 202)
        
        # Test with completed job
        jobs[job_id] = {
            'status': 'completed',
            'result': {'data': 'test'}
        }
        response = self.client.get(f'/api/result/{job_id}')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['data'], 'test')

    def test_check_llm_status_endpoint(self):
        """Test the /api/check-llm-status endpoint"""
        response = self.client.get('/api/check-llm-status')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertIn('env_vars', result)
        self.assertIn('providers', result)

    def test_job_status_stream(self):
        """Test the job status streaming endpoint"""
        job_id = 'test-job-123'
        job_queue = queue.Queue()
        job_queues[job_id] = job_queue
        
        # Add a test event
        job_queue.put({'phase': 'processing'})
        job_queue.put('END')
        
        response = self.client.get(f'/api/job_status/{job_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/event-stream')
        
        # Check that data is streamed
        data = b''
        for chunk in response.response:
            data += chunk
            if b'END' in chunk:
                break
        
        self.assertIn(b'processing', data)

    def test_refine_prompt_endpoint(self):
        """Test the /api/refine_prompt_v2 endpoint"""
        data = {
            'prompt': 'Add a button to the page',
            'repo_url': 'https://github.com/test/repo'
        }
        
        response = self.client.post('/api/refine_prompt_v2',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertIn('refined_prompt', result)

    def test_session_management(self):
        """Test session creation and management"""
        data = {
            'vibe': 'Test feature',
            'stage': 'A',
            'repo_url': 'https://github.com/test/repo'
        }
        
        response = self.client.post('/api/analyze', data=data)
        result = json.loads(response.data)
        
        session_id = result.get('session_id')
        self.assertIsNotNone(session_id)
        
        # Verify session was created
        job_id = result.get('job_id')
        self.assertIn(job_id, jobs)
        self.assertEqual(jobs[job_id]['session_id'], session_id)


if __name__ == '__main__':
    unittest.main()
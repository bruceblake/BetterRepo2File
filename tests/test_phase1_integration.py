"""Integration tests for Phase 1: Redis and Session Management"""
import unittest
import tempfile
import shutil
import os
import json
from app.config import get_config
from app.session_manager import SessionManager
from app.storage_manager import StorageManager
import redis
from minio import Minio

class TestPhase1Integration(unittest.TestCase):
    """Test Redis, Session Management, and MinIO integration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.config = get_config()
        cls.config.TESTING = True
        
        # Initialize Redis client
        cls.redis_client = redis.Redis.from_url(cls.config.REDIS_URL, decode_responses=True)
        
        # Initialize session manager
        cls.session_manager = SessionManager(cls.redis_client, prefix="test_session:")
        
        # Initialize storage manager
        cls.storage_manager = StorageManager(cls.config)
        
        # Create test bucket
        cls.test_bucket = "test-betterrepo2file"
        cls.storage_manager.bucket_name = cls.test_bucket
        cls.storage_manager._ensure_bucket_exists()
    
    def setUp(self):
        """Set up each test"""
        # Clear test sessions
        for key in self.redis_client.keys("test_session:*"):
            self.redis_client.delete(key)
    
    def test_redis_connection(self):
        """Test Redis connectivity"""
        # Test basic operations
        self.redis_client.set("test_key", "test_value")
        value = self.redis_client.get("test_key")
        self.assertEqual(value, "test_value")
        
        # Clean up
        self.redis_client.delete("test_key")
    
    def test_session_management(self):
        """Test session manager functionality"""
        # Create session
        session_id = self.session_manager.create_session()
        self.assertIsNotNone(session_id)
        
        # Get session
        session_data = self.session_manager.get_session(session_id)
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data['id'], session_id)
        
        # Update session
        test_data = {"key": "value", "count": 42}
        self.session_manager.update_session(session_id, test_data)
        
        # Verify update
        retrieved_data = self.session_manager.get_session_data(session_id, "key")
        self.assertEqual(retrieved_data, "value")
        
        retrieved_count = self.session_manager.get_session_data(session_id, "count")
        self.assertEqual(retrieved_count, 42)
        
        # Test session deletion
        self.session_manager.delete_session(session_id)
        session_data = self.session_manager.get_session(session_id)
        self.assertIsNone(session_data)
    
    def test_session_expiration(self):
        """Test session expiration functionality"""
        session_id = self.session_manager.create_session()
        
        # Verify session exists
        self.assertTrue(self.session_manager.is_session_active(session_id))
        
        # Manually expire the session
        key = f"{self.session_manager.prefix}{session_id}"
        self.redis_client.expire(key, 1)  # 1 second TTL
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # Verify session expired
        self.assertFalse(self.session_manager.is_session_active(session_id))
    
    def test_minio_connectivity(self):
        """Test MinIO/S3 connectivity"""
        # Upload test data
        test_data = b"Hello, MinIO!"
        object_name = "test/hello.txt"
        
        self.storage_manager.upload_data(test_data, object_name)
        
        # Download and verify
        downloaded_data = self.storage_manager.download_data(object_name)
        self.assertEqual(downloaded_data, test_data)
        
        # Test object existence
        self.assertTrue(self.storage_manager.object_exists(object_name))
        
        # Clean up
        self.storage_manager.delete_object(object_name)
        self.assertFalse(self.storage_manager.object_exists(object_name))
    
    def test_minio_directory_operations(self):
        """Test MinIO directory-like operations"""
        # Create test directory structure
        test_dir = tempfile.mkdtemp()
        
        # Create test files
        for i in range(3):
            file_path = os.path.join(test_dir, f"file_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Content {i}")
        
        # Upload directory
        prefix = "test/upload_dir/"
        self.storage_manager.upload_directory(test_dir, prefix)
        
        # List objects
        objects = self.storage_manager.list_objects(prefix)
        self.assertEqual(len(objects), 3)
        
        # Download directory
        download_dir = tempfile.mkdtemp()
        self.storage_manager.download_directory(prefix, download_dir)
        
        # Verify downloaded files
        for i in range(3):
            file_path = os.path.join(download_dir, f"file_{i}.txt")
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, 'r') as f:
                content = f.read()
                self.assertEqual(content, f"Content {i}")
        
        # Clean up
        shutil.rmtree(test_dir)
        shutil.rmtree(download_dir)
        self.storage_manager.delete_directory(prefix)
    
    def test_json_storage(self):
        """Test JSON data storage and retrieval"""
        test_data = {
            "name": "Test Project",
            "version": "1.0.0",
            "features": ["redis", "minio", "celery"],
            "config": {
                "debug": True,
                "workers": 4
            }
        }
        
        object_name = "test/config.json"
        
        # Upload JSON
        self.storage_manager.upload_json(test_data, object_name)
        
        # Download JSON
        retrieved_data = self.storage_manager.download_json(object_name)
        
        # Verify
        self.assertEqual(retrieved_data, test_data)
        
        # Clean up
        self.storage_manager.delete_object(object_name)
    
    def test_presigned_urls(self):
        """Test presigned URL generation"""
        # Upload test file
        test_data = b"Test content for presigned URL"
        object_name = "test/presigned.txt"
        
        self.storage_manager.upload_data(test_data, object_name)
        
        # Generate presigned URL
        url = self.storage_manager.get_file_url(object_name, expires=3600)
        self.assertIsNotNone(url)
        self.assertIn(object_name, url)
        
        # Clean up
        self.storage_manager.delete_object(object_name)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Clean up test bucket
        try:
            objects = cls.storage_manager.list_objects("")
            for obj in objects:
                cls.storage_manager.delete_object(obj)
            
            # Remove test bucket
            cls.storage_manager.client.remove_bucket(cls.test_bucket)
        except:
            pass


if __name__ == '__main__':
    unittest.main()
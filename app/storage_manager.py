"""Storage management module for MinIO/S3 operations"""
import os
import json
import tempfile
import logging
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List, Optional, Any
from minio import Minio
from minio.error import S3Error
from flask import current_app

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages object storage operations using MinIO/S3"""
    
    def __init__(self, config=None):
        """Initialize storage manager with configuration"""
        self._config = config
        self._client = None
        self._bucket_name = None
        
    @property
    def config(self):
        """Get config, using Flask app's config if available"""
        if self._config is None and current_app:
            self._config = current_app.config
        return self._config
    
    @property
    def client(self):
        """Get MinIO client, initializing if needed"""
        if self._client is None:
            config = self.config
            self._client = Minio(
                config['MINIO_ENDPOINT'],
                access_key=config['MINIO_ACCESS_KEY'],
                secret_key=config['MINIO_SECRET_KEY'],
                secure=config['MINIO_SECURE']
            )
            self._ensure_bucket_exists()
        return self._client
    
    @property
    def bucket_name(self):
        """Get bucket name from config"""
        if self._bucket_name is None:
            self._bucket_name = self.config['MINIO_BUCKET_NAME']
        return self._bucket_name
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if not"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error checking/creating bucket: {e}")
            raise
    
    def upload_file(self, file_path: str, object_name: str) -> str:
        """Upload a file to storage"""
        try:
            self.client.fput_object(
                self.bucket_name,
                object_name,
                file_path
            )
            logger.info(f"Uploaded file: {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def upload_data(self, data: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
        """Upload raw data to storage"""
        try:
            data_stream = BytesIO(data)
            self.client.put_object(
                self.bucket_name,
                object_name,
                data_stream,
                length=len(data),
                content_type=content_type
            )
            logger.info(f"Uploaded data: {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Failed to upload data: {e}")
            raise
    
    def upload_data_stream(self, object_name: str, data_stream, length: int, content_type: str = "application/octet-stream") -> str:
        """Upload a data stream to storage"""
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                data_stream,
                length=length,
                content_type=content_type
            )
            logger.info(f"Uploaded stream: {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Failed to upload stream: {e}")
            raise
    
    def download_file(self, object_name: str, file_path: str):
        """Download a file from storage"""
        try:
            self.client.fget_object(
                self.bucket_name,
                object_name,
                file_path
            )
            logger.info(f"Downloaded file: {object_name} to {file_path}")
        except S3Error as e:
            logger.error(f"Failed to download file: {e}")
            raise
    
    def download_data(self, object_name: str) -> bytes:
        """Download raw data from storage"""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            logger.info(f"Downloaded data: {object_name}")
            return data
        except S3Error as e:
            logger.error(f"Failed to download data: {e}")
            raise
    
    def download_stream(self, object_name: str, chunk_size: int = 1024*1024):
        """Download data from storage as a stream"""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            
            def generate():
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                response.close()
                response.release_conn()
            
            return generate()
        except S3Error as e:
            logger.error(f"Failed to download stream: {e}")
            raise
    
    def get_file_url(self, object_name: str, expires: Optional[int] = None) -> str:
        """Get a public URL for an object"""
        try:
            if expires is None:
                expires = self.config.get('PRESIGNED_URL_EXPIRATION', 3600)
                
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            logger.error(f"Failed to get file URL: {e}")
            raise
    
    def generate_presigned_url(self, object_name: str, expires_in: Optional[int] = None) -> str:
        """Generate a presigned URL for downloading a file (alias for get_file_url)"""
        return self.get_file_url(object_name, expires=expires_in)
    
    def list_objects(self, prefix: str = "", recursive: bool = True) -> List[str]:
        """List objects in storage with optional prefix"""
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=recursive
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Failed to list objects: {e}")
            raise
    
    def list_prefixes(self, prefix: str = "") -> List[str]:
        """List directory-like prefixes in storage"""
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=False
            )
            prefixes = set()
            for obj in objects:
                if obj.is_dir:
                    prefixes.add(obj.object_name)
            return list(prefixes)
        except S3Error as e:
            raise Exception(f"Failed to list prefixes: {e}")
    
    def delete_object(self, object_name: str):
        """Delete an object from storage"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            raise Exception(f"Failed to delete object: {e}")
    
    def delete_directory(self, prefix: str):
        """Delete all objects with a given prefix (directory-like deletion)"""
        try:
            objects = self.list_objects(prefix=prefix)
            for obj in objects:
                self.delete_object(obj)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete directory: {e}")
    
    def object_exists(self, object_name: str) -> bool:
        """Check if an object exists in storage"""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            raise Exception(f"Failed to check object existence: {e}")
    
    def copy_object(self, source_name: str, dest_name: str):
        """Copy an object within storage"""
        try:
            self.client.copy_object(
                self.bucket_name,
                dest_name,
                f"{self.bucket_name}/{source_name}"
            )
            return True
        except S3Error as e:
            raise Exception(f"Failed to copy object: {e}")
    
    def move_object(self, source_name: str, dest_name: str):
        """Move an object within storage (copy then delete)"""
        self.copy_object(source_name, dest_name)
        self.delete_object(source_name)
        return True
    
    def download_directory(self, prefix: str, local_path: str):
        """Download all objects with a prefix to a local directory"""
        os.makedirs(local_path, exist_ok=True)
        objects = self.list_objects(prefix=prefix)
        
        for obj_name in objects:
            # Calculate relative path
            relative_path = obj_name[len(prefix):].lstrip('/')
            local_file_path = os.path.join(local_path, relative_path)
            
            # Create local directory if needed
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            # Download file
            self.download_file(obj_name, local_file_path)
    
    def upload_directory(self, local_path: str, prefix: str):
        """Upload a local directory to storage"""
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file_path = os.path.join(root, file)
                # Calculate relative path
                relative_path = os.path.relpath(local_file_path, local_path)
                object_name = os.path.join(prefix, relative_path).replace('\\', '/')
                
                # Upload file
                self.upload_file(local_file_path, object_name)
    
    def get_object_metadata(self, object_name: str) -> Dict[str, Any]:
        """Get metadata for an object"""
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return {
                'size': stat.size,
                'etag': stat.etag,
                'content_type': stat.content_type,
                'last_modified': stat.last_modified.isoformat() if stat.last_modified else None,
                'metadata': stat.metadata
            }
        except S3Error as e:
            logger.error(f"Failed to get object metadata: {e}")
            raise
    
    def cleanup_old_objects(self, prefix: str = "", days: int = 7):
        """Clean up objects older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)
        
        deleted_count = 0
        for obj in objects:
            if obj.last_modified < cutoff_date:
                try:
                    self.delete_object(obj.object_name)
                    deleted_count += 1
                    logger.info(f"Deleted old object: {obj.object_name}")
                except Exception as e:
                    logger.error(f"Failed to delete {obj.object_name}: {e}")
        
        return deleted_count
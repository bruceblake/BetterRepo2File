"""
Job Manager for RobustRepo v2.0 - Manages Celery task submission and tracking
"""
import uuid
from typing import Optional, Dict, Any
from .celery_app import celery_app
from .logger import logger
from celery.result import AsyncResult

class JobManager:
    """Manages asynchronous job submission and tracking via Celery"""
    
    def __init__(self):
        self.celery_app = celery_app
    
    def submit_repo_processing_job(
        self,
        input_repo_type: str,
        input_repo_ref: str,
        github_branch: Optional[str] = None,
        processing_mode: str = 'standard',
        output_format: str = 'text',
        additional_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a repository processing job to Celery
        
        Args:
            input_repo_type: Type of input ('github_url', 'local_path', 'minio_file')
            input_repo_ref: Reference to the input (URL, path, or MinIO key)
            github_branch: GitHub branch to use (if input is GitHub URL)
            processing_mode: Processing mode ('standard', 'smart', 'token', 'ultra', 'context_generation')
            output_format: Output format ('text', 'json', 'markdown')
            additional_options: Additional processing options
            
        Returns:
            str: Job ID for tracking
        """
        try:
            # Generate unique job ID
            job_id = str(uuid.uuid4())
            
            # Submit task to Celery
            task = self.celery_app.send_task(
                'process_repository_task',
                args=[
                    input_repo_type,
                    input_repo_ref,
                    github_branch,
                    processing_mode,
                    output_format,
                    additional_options or {}
                ],
                task_id=job_id,
                queue='celery'
            )
            
            logger.info(f"Submitted job {job_id} for processing")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to submit job: {e}")
            raise
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a job
        
        Args:
            job_id: Job ID to check
            
        Returns:
            dict: Job status information
        """
        try:
            result = AsyncResult(job_id, app=self.celery_app)
            
            # Catch the error if accessing state fails
            try:
                state = result.state
                info = result.info if result.info else {}
            except ValueError as e:
                if "Exception information must include" in str(e):
                    # This is the Celery serialization error
                    logger.warning(f"Celery backend error for job {job_id}, working around it")
                    state = 'PENDING'
                    info = {}
                else:
                    raise
            
            status = {
                'id': job_id,
                'state': state,
                'info': info
            }
            
            # Add progress information if available
            if state == 'PROGRESS':
                status['current'] = info.get('current', 0)
                status['total'] = info.get('total', 0)
                status['phase'] = info.get('phase', 'unknown')
                status['message'] = info.get('message', '')
            elif state == 'SUCCESS':
                # If successful, check if our task returned a result dict
                if isinstance(info, dict) and 'success' in info:
                    status['state'] = 'SUCCESS' if info.get('success') else 'FAILURE'
                    status['result'] = info
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return {
                'id': job_id,
                'state': 'ERROR',
                'info': {'error': str(e)}
            }
    
    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of a completed job
        
        Args:
            job_id: Job ID to get result for
            
        Returns:
            dict: Job result or None if not complete
        """
        try:
            result = AsyncResult(job_id, app=self.celery_app)
            
            if result.state == 'SUCCESS':
                return result.result
            elif result.state == 'FAILURE':
                return {
                    'error': str(result.info),
                    'traceback': result.traceback
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get job result for {job_id}: {e}")
            return {'error': str(e)}
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            bool: True if successfully cancelled
        """
        try:
            result = AsyncResult(job_id, app=self.celery_app)
            result.revoke(terminate=True)
            logger.info(f"Cancelled job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    def cleanup_job(self, job_id: str) -> None:
        """
        Cleanup a job's data
        
        Args:
            job_id: Job ID to cleanup
        """
        try:
            # Remove result from backend
            result = AsyncResult(job_id, app=self.celery_app)
            result.forget()
            
            logger.info(f"Cleaned up job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup job {job_id}: {e}")
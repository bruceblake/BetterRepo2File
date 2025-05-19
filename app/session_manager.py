"""Session management module using Redis backend"""
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import session, current_app
import redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions with Redis backend"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, prefix: str = "session:"):
        self._redis = redis_client
        self.prefix = prefix
        self.ttl = timedelta(hours=24)  # Session TTL
    
    @property
    def redis(self):
        """Get Redis client, using Flask app's Redis if available"""
        if self._redis is None and current_app:
            self._redis = redis.from_url(current_app.config['REDIS_URL'])
        return self._redis
        
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new session"""
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
                
            session_data = {
                'id': session_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'data': {}
            }
            
            key = f"{self.prefix}{session_id}"
            self.redis.setex(
                key, 
                self.ttl, 
                json.dumps(session_data)
            )
            
            logger.info(f"Created session: {session_id}")
            return session_id
            
        except ConnectionError as e:
            logger.error(f"Redis connection error creating session: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        key = f"{self.prefix}{session_id}"
        data = self.redis.get(key)
        
        if data:
            session_data = json.loads(data)
            # Update TTL on access
            self.redis.expire(key, self.ttl)
            return session_data
            
        return None
        
    def update_session(self, session_id: str, data: Dict[str, Any]):
        """Update session data"""
        session_data = self.get_session(session_id)
        
        if not session_data:
            session_data = {
                'id': session_id,
                'created_at': datetime.utcnow().isoformat(),
                'data': {}
            }
            
        session_data['updated_at'] = datetime.utcnow().isoformat()
        session_data['data'].update(data)
        
        key = f"{self.prefix}{session_id}"
        self.redis.setex(
            key,
            self.ttl,
            json.dumps(session_data)
        )
        
    def delete_session(self, session_id: str):
        """Delete a session"""
        key = f"{self.prefix}{session_id}"
        self.redis.delete(key)
        
    def list_sessions(self) -> list:
        """List all active sessions"""
        pattern = f"{self.prefix}*"
        keys = self.redis.keys(pattern)
        
        sessions = []
        for key in keys:
            data = self.redis.get(key)
            if data:
                session_data = json.loads(data)
                sessions.append(session_data)
                
        return sessions
        
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (handled automatically by Redis TTL)"""
        # Redis handles expiration automatically
        pass
        
    def get_session_data(self, session_id: str, key: str, default=None):
        """Get specific data from session"""
        session_data = self.get_session(session_id)
        if session_data and 'data' in session_data:
            return session_data['data'].get(key, default)
        return default
        
    def set_session_data(self, session_id: str, key: str, value: Any):
        """Set specific data in session"""
        self.update_session(session_id, {key: value})
        
    def delete_session_data(self, session_id: str, key: str):
        """Delete specific data from session"""
        session_data = self.get_session(session_id)
        if session_data and 'data' in session_data:
            session_data['data'].pop(key, None)
            self.update_session(session_id, session_data['data'])
            
    def extend_session(self, session_id: str, additional_time: timedelta):
        """Extend session TTL"""
        key = f"{self.prefix}{session_id}"
        self.redis.expire(key, self.ttl + additional_time)
        
    def is_session_active(self, session_id: str) -> bool:
        """Check if session is active"""
        key = f"{self.prefix}{session_id}"
        return self.redis.exists(key) > 0
    
    # Flask-Session integration helpers
    def init_flask_session(self, app):
        """Initialize Flask-Session with Redis backend"""
        from flask_session import Session
        
        app.config['SESSION_REDIS'] = self.redis
        Session(app)
        
    def get_or_create_session_id(self) -> str:
        """Get current session ID or create new one"""
        if 'session_id' not in session:
            session['session_id'] = self.create_session()
        return session['session_id']
        
    def get_current_session_data(self, key: str, default=None):
        """Get data from current Flask session"""
        session_id = self.get_or_create_session_id()
        return self.get_session_data(session_id, key, default)
        
    def set_current_session_data(self, key: str, value: Any):
        """Set data in current Flask session"""
        session_id = self.get_or_create_session_id()
        self.set_session_data(session_id, key, value)
        
    def delete_current_session_data(self, key: str):
        """Delete data from current Flask session"""
        session_id = self.get_or_create_session_id()
        self.delete_session_data(session_id, key)
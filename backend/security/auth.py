"""
STUDX JARVIS - Security Module
Authentication and permission management
"""

import hashlib
import secrets
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from functools import wraps

from ..memory.database import get_database

logger = logging.getLogger('JARVIS.Security')

class PermissionLevel:
    """Permission level definitions"""
    LEVEL_1 = 1  # Basic: Open apps, search, read notes
    LEVEL_2 = 2  # Intermediate: Edit files, upload, draft emails
    LEVEL_3 = 3  # Admin: Delete files, terminal commands, system settings

PERMISSION_GROUPS = {
    PermissionLevel.LEVEL_1: [
        'open_applications',
        'search_web',
        'read_notes',
        'view_dashboard',
        'check_weather',
        'set_reminders'
    ],
    PermissionLevel.LEVEL_2: [
        'edit_files',
        'upload_files',
        'draft_emails',
        'create_tasks',
        'manage_projects',
        'edit_notes'
    ],
    PermissionLevel.LEVEL_3: [
        'delete_files',
        'execute_terminal',
        'modify_settings',
        'manage_users',
        'view_logs',
        'change_permissions'
    ]
}


class SecurityManager:
    """
    JARVIS Security Manager
    Handles authentication, authorization, and audit logging
    """
    
    def __init__(self):
        self.db = get_database()
        self.kill_switch_enabled = True
        self.failed_attempts = {}
        self.lockout_duration = timedelta(minutes=15)
        self.max_attempts = 5
        
        # Ensure default owner exists
        self._ensure_default_user()
        
        logger.info("Security manager initialized")
    
    def _ensure_default_user(self):
        """Ensure default owner user exists"""
        owner = self.db.get_user(email='owner@jarvis.local')
        if not owner:
            # Create default owner with Level 3 permissions
            self.db.create_user(
                name='Owner',
                email='owner@jarvis.local',
                password='jarvis2024',  # Should be changed!
                role='owner'
            )
            logger.info("Default owner user created")
    
    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user
        
        Returns:
            User dict if authenticated, None otherwise
        """
        # Check for lockout
        if email in self.failed_attempts:
            last_attempt = self.failed_attempts[email]['last_attempt']
            if datetime.now() - last_attempt < self.lockout_duration:
                attempts_left = self.max_attempts - self.failed_attempts[email]['attempts']
                if attempts_left <= 0:
                    logger.warning(f"Account locked: {email}")
                    return None
        
        # Authenticate
        user = self.db.authenticate_user(email, password)
        
        if user:
            # Reset failed attempts
            if email in self.failed_attempts:
                del self.failed_attempts[email]
            
            self.db.log_activity('login', f'User {email} logged in')
            logger.info(f"User authenticated: {email}")
            return user
        else:
            # Record failed attempt
            if email not in self.failed_attempts:
                self.failed_attempts[email] = {'attempts': 0, 'last_attempt': None}
            
            self.failed_attempts[email]['attempts'] += 1
            self.failed_attempts[email]['last_attempt'] = datetime.now()
            
            logger.warning(f"Failed login attempt for: {email}")
            return None
    
    def authenticate_face(self, face_embedding) -> Optional[Dict]:
        """Authenticate using face recognition"""
        # This would integrate with the vision module
        # For now, return default user if face auth is enabled
        try:
            from ..vision.face_recognition import recognize_face
            
            recognized = recognize_face(face_embedding)
            if recognized:
                user = self.db.get_user(user_id=recognized['user_id'])
                if user:
                    self.db.log_activity('face_login', f"User {user['email']} logged in via face")
                    return user
        except Exception as e:
            logger.error(f"Face authentication error: {e}")
        
        return None
    
    def check_permission(self, user: Dict, permission: str) -> bool:
        """Check if user has a specific permission"""
        if not user:
            return False
        
        user_level = self._get_user_level(user)
        
        # Owner has all permissions
        if user.get('role') == 'owner':
            return True
        
        # Check if permission exists in any accessible level
        for level in range(1, user_level + 1):
            if permission in PERMISSION_GROUPS.get(level, []):
                return True
        
        return False
    
    def _get_user_level(self, user: Dict) -> int:
        """Get user's permission level based on role"""
        role_levels = {
            'owner': PermissionLevel.LEVEL_3,
            'admin': PermissionLevel.LEVEL_3,
            'manager': PermissionLevel.LEVEL_2,
            'user': PermissionLevel.LEVEL_1,
            'guest': 0
        }
        return role_levels.get(user.get('role', 'guest'), 0)
    
    def require_permission(self, permission: str):
        """Decorator to require a specific permission"""
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                # Get current user from request context
                user = kwargs.get('user') or (args[0] if args and hasattr(args[0], 'user') else None)
                
                if not user:
                    raise PermissionError("Authentication required")
                
                if not self.check_permission(user, permission):
                    logger.warning(f"Permission denied: {permission} for user {user.get('email')}")
                    raise PermissionError(f"Permission denied: {permission}")
                
                return func(self, *args, **kwargs)
            return wrapper
        return decorator
    
    def authorize_action(self, user: Dict, action: str, resource: Dict = None) -> bool:
        """
        Authorize an action
        
        Args:
            user: User dict
            action: Action to perform
            resource: Optional resource context
        
        Returns:
            True if authorized
        """
        # Map actions to permissions
        action_permissions = {
            'read': ['read_notes', 'view_dashboard'],
            'write': ['edit_files', 'edit_notes', 'create_tasks'],
            'delete': ['delete_files'],
            'execute': ['execute_terminal', 'open_applications'],
            'admin': ['manage_users', 'change_permissions', 'modify_settings']
        }
        
        required_permissions = action_permissions.get(action, [])
        
        for perm in required_permissions:
            if self.check_permission(user, perm):
                return True
        
        return False
    
    def trigger_kill_switch(self, reason: str = None):
        """Emergency shutdown"""
        if not self.kill_switch_enabled:
            logger.warning("Kill switch attempted but disabled")
            return False
        
        logger.critical(f"KILL SWITCH ACTIVATED: {reason}")
        
        # Log the event
        self.db.log_activity('kill_switch', f"Activated: {reason}")
        
        # Stop all running processes
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Don't kill essential system processes
                    if proc.info['name'] not in ['systemd', 'init', 'kernel']:
                        proc.terminate()
                except:
                    pass
        except Exception as e:
            logger.error(f"Error during kill switch: {e}")
        
        return True
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent audit log entries"""
        return self.db.get_recent_logs(limit)
    
    def log_security_event(self, event_type: str, details: str):
        """Log a security event"""
        self.db.log_activity(f'security_{event_type}', details)
        logger.info(f"Security event: {event_type} - {details}")


class SessionManager:
    """Manage user sessions"""
    
    def __init__(self):
        self.db = get_database()
        self.sessions = {}  # session_id -> session_data
    
    def create_session(self, user_id: int) -> str:
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_active': datetime.now(),
            'ip_address': None
        }
        
        logger.info(f"Session created for user {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str):
        """Update session last active time"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_active'] = datetime.now()
    
    def destroy_session(self, session_id: str):
        """Destroy a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session destroyed: {session_id}")
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Remove expired sessions"""
        now = datetime.now()
        expired = [
            sid for sid, data in self.sessions.items()
            if (now - data['last_active']).total_seconds() > max_age_hours * 3600
        ]
        
        for sid in expired:
            self.destroy_session(sid)
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")


# Global instances
_security_manager = None
_session_manager = None

def get_security_manager() -> SecurityManager:
    """Get security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager

def get_session_manager() -> SessionManager:
    """Get session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
"""
STUDX JARVIS - Database Module
SQLite database with encryption support
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
import logging

logger = logging.getLogger('JARVIS.Database')

class JarvisDatabase:
    """Main database handler for JARVIS"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = Path(__file__).parent.parent.parent
            db_path = base_dir / 'database' / 'jarvis_db.sqlite'
        
        self.db_path = str(db_path)
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        self._init_db()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = Path(self.db_path).parent / '.db_key'
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            return key
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT,
                role TEXT DEFAULT 'user',
                permissions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                importance INTEGER DEFAULT 5,
                embedding BLOB,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                progress INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 5,
                tags TEXT DEFAULT '[]',
                start_date TIMESTAMP,
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                description TEXT,
                project_id INTEGER,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                completed BOOLEAN DEFAULT 0,
                completed_at TIMESTAMP,
                due_date TIMESTAMP,
                tags TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        
        # Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                user_id INTEGER,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                jarvis_response TEXT NOT NULL,
                intent TEXT,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        result = cursor.execute(query, params)
        conn.commit()
        return result
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Fetch one result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[tuple]:
        """Fetch all results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetch_all()
    
    # User Management
    def create_user(self, name: str, email: str, password: str = None, role: str = 'user') -> int:
        """Create a new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest() if password else None
        cursor = self.execute(
            'INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
            (name, email, password_hash, role)
        )
        return cursor.lastrowid
    
    def get_user(self, user_id: int = None, email: str = None) -> Optional[Dict]:
        """Get user by ID or email"""
        if user_id:
            result = self.fetch_one('SELECT * FROM users WHERE id = ?', (user_id,))
        elif email:
            result = self.fetch_one('SELECT * FROM users WHERE email = ?', (email,))
        else:
            return None
        
        if result:
            return {
                'id': result[0], 'name': result[1], 'email': result[2],
                'password_hash': result[3], 'role': result[4],
                'permissions': json.loads(result[5]),
                'created_at': result[6], 'last_login': result[7],
                'is_active': result[8]
            }
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        result = self.fetch_one(
            'SELECT * FROM users WHERE email = ? AND password_hash = ?',
            (email, password_hash)
        )
        if result:
            self.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (result[0],)
            )
            return self.get_user(user_id=result[0])
        return None
    
    # Memory Management
    def add_memory(self, content: str, category: str = 'general', importance: int = 5) -> int:
        """Add a memory"""
        encrypted_content = self.cipher.encrypt(content.encode()).decode()
        cursor = self.execute(
            'INSERT INTO memories (content, category, importance) VALUES (?, ?, ?)',
            (encrypted_content, category, importance)
        )
        return cursor.lastrowid
    
    def get_memory(self, memory_id: int) -> Optional[str]:
        """Get and decrypt memory"""
        result = self.fetch_one('SELECT content, access_count FROM memories WHERE id = ?', (memory_id,))
        if result:
            decrypted = self.cipher.decrypt(result[0].encode()).decode()
            self.execute(
                'UPDATE memories SET accessed_at = CURRENT_TIMESTAMP, access_count = ? WHERE id = ?',
                (result[1] + 1, memory_id)
            )
            return decrypted
        return None
    
    def search_memories(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Search memories"""
        if category:
            results = self.fetch_all(
                '''SELECT id, content, category, importance, access_count 
                   FROM memories WHERE category = ? ORDER BY importance DESC LIMIT ?''',
                (category, limit)
            )
        else:
            results = self.fetch_all(
                '''SELECT id, content, category, importance, access_count 
                   FROM memories ORDER BY importance DESC LIMIT ?''',
                (limit,)
            )
        
        memories = []
        for r in results:
            try:
                decrypted = self.cipher.decrypt(r[1].encode()).decode()
                memories.append({
                    'id': r[0], 'content': decrypted, 'category': r[2],
                    'importance': r[3], 'access_count': r[4]
                })
            except:
                pass
        return memories
    
    # Project Management
    def create_project(self, name: str, description: str = None, status: str = 'active') -> int:
        """Create a new project"""
        cursor = self.execute(
            'INSERT INTO projects (name, description, status, start_date) VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
            (name, description, status)
        )
        return cursor.lastrowid
    
    def get_projects(self, status: str = None) -> List[Dict]:
        """Get all projects"""
        if status:
            results = self.fetch_all('SELECT * FROM projects WHERE status = ?', (status,))
        else:
            results = self.fetch_all('SELECT * FROM projects')
        
        return [{
            'id': r[0], 'name': r[1], 'description': r[2], 'status': r[3],
            'progress': r[4], 'priority': r[5], 'tags': json.loads(r[6]),
            'start_date': r[7], 'due_date': r[8], 'created_at': r[9], 'updated_at': r[10]
        } for r in results]
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """Update project fields"""
        allowed_fields = ['name', 'description', 'status', 'progress', 'priority', 'tags', 'due_date']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        if 'tags' in updates and isinstance(updates['tags'], list):
            updates['tags'] = json.dumps(updates['tags'])
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        self.execute(
            f'UPDATE projects SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (*updates.values(), project_id)
        )
        return True
    
    # Task Management
    def create_task(self, task: str, project_id: int = None, priority: int = 5) -> int:
        """Create a new task"""
        cursor = self.execute(
            'INSERT INTO tasks (task, project_id, priority) VALUES (?, ?, ?)',
            (task, project_id, priority)
        )
        return cursor.lastrowid
    
    def get_tasks(self, project_id: int = None, status: str = None, completed: bool = None) -> List[Dict]:
        """Get tasks with filters"""
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if project_id:
            query += ' AND project_id = ?'
            params.append(project_id)
        if status:
            query += ' AND status = ?'
            params.append(status)
        if completed is not None:
            query += ' AND completed = ?'
            params.append(1 if completed else 0)
        
        query += ' ORDER BY priority DESC, created_at DESC'
        results = self.fetch_all(query, tuple(params))
        
        return [{
            'id': r[0], 'task': r[1], 'description': r[2], 'project_id': r[3],
            'priority': r[4], 'status': r[5], 'completed': bool(r[6]),
            'completed_at': r[7], 'due_date': r[8], 'tags': json.loads(r[9]),
            'created_at': r[10]
        } for r in results]
    
    def complete_task(self, task_id: int) -> bool:
        """Mark task as completed"""
        self.execute(
            'UPDATE tasks SET completed = 1, completed_at = CURRENT_TIMESTAMP, status = "completed" WHERE id = ?',
            (task_id,)
        )
        return True
    
    # Activity Logging
    def log_activity(self, action: str, details: str = None, user_id: int = None) -> int:
        """Log an activity"""
        cursor = self.execute(
            'INSERT INTO logs (action, details, user_id) VALUES (?, ?, ?)',
            (action, details, user_id)
        )
        return cursor.lastrowid
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent activity logs"""
        results = self.fetch_all(
            'SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        return [{
            'id': r[0], 'action': r[1], 'details': r[2],
            'user_id': r[3], 'timestamp': r[6]
        } for r in results]
    
    # Conversation History
    def save_conversation(self, user_input: str, jarvis_response: str, intent: str = None, context: dict = None) -> int:
        """Save a conversation"""
        cursor = self.execute(
            'INSERT INTO conversations (user_input, jarvis_response, intent, context) VALUES (?, ?, ?, ?)',
            (user_input, jarvis_response, intent, json.dumps(context) if context else None)
        )
        return cursor.lastrowid
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict]:
        """Get conversation history"""
        results = self.fetch_all(
            'SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        return [{
            'id': r[0], 'user_input': r[1], 'jarvis_response': r[2],
            'intent': r[3], 'context': json.loads(r[4]) if r[4] else None,
            'timestamp': r[5]
        } for r in results]
    
    # Settings
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting"""
        self.execute(
            'INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)',
            (key, value)
        )
        return True
    
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get a setting"""
        result = self.fetch_one('SELECT value FROM settings WHERE key = ?', (key,))
        return result[0] if result else default


# Global database instance
_db = None

def get_database() -> JarvisDatabase:
    """Get database instance"""
    global _db
    if _db is None:
        _db = JarvisDatabase()
    return _db

def init_database() -> JarvisDatabase:
    """Initialize database"""
    return get_database()

def log_activity(action: str, details: str = None) -> int:
    """Quick log function"""
    return get_database().log_activity(action, details)
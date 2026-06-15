"""
数据库模块 - SQLite数据库操作

实现用户认证和历史记录功能
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path(__file__).parent.parent / "data" / "emotion_db.sqlite"
        self._init_database()
    
    def _init_database(self):
        """初始化数据库和表"""
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT
                )
            ''')
            
            # 创建历史记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    input_text TEXT NOT NULL,
                    emotion_result TEXT NOT NULL,
                    emotion_intensity REAL NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at)')
            
            conn.commit()
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str, email: str = None) -> bool:
        """注册新用户"""
        try:
            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(password)
            created_at = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (id, username, password_hash, email, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, password_hash, email, created_at))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # 用户名已存在
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """验证用户登录"""
        password_hash = self._hash_password(password)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, created_at FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            result = cursor.fetchone()
            if result:
                # 更新最后登录时间
                cursor.execute('''
                    UPDATE users SET last_login = ? WHERE id = ?
                ''', (datetime.now().isoformat(), result[0]))
                conn.commit()
                
                return {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'created_at': result[3]
                }
        return None
    
    def add_history(self, user_id: str, input_text: str, emotion_result: str, 
                   emotion_intensity: float, confidence: float) -> bool:
        """添加分析历史记录"""
        try:
            history_id = str(uuid.uuid4())
            created_at = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO history (id, user_id, input_text, emotion_result, 
                                        emotion_intensity, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (history_id, user_id, input_text, emotion_result, 
                      emotion_intensity, confidence, created_at))
                conn.commit()
            return True
        except Exception:
            return False
    
    def get_history(self, user_id: str, limit: int = 50) -> list:
        """获取用户分析历史"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT input_text, emotion_result, emotion_intensity, confidence, created_at
                FROM history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            return [{
                'input_text': r[0],
                'emotion_result': r[1],
                'emotion_intensity': r[2],
                'confidence': r[3],
                'created_at': r[4]
            } for r in results]
    
    def get_user_count(self) -> int:
        """获取用户数量"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]
    
    def get_history_count(self, user_id: str) -> int:
        """获取用户历史记录数量"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM history WHERE user_id = ?', (user_id,))
            return cursor.fetchone()[0]
    
    def delete_history(self, user_id: str) -> bool:
        """清空用户历史记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM history WHERE user_id = ?', (user_id,))
                conn.commit()
            return True
        except Exception:
            return False

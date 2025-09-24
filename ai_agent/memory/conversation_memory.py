"""
对话记忆系统 - 管理短期和长期记忆
支持对话历史存储、相关记忆检索、用户偏好学习等功能
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import os


class ConversationMemory:
    """对话记忆管理器"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化记忆系统
        
        Args:
            db_path: 数据库文件路径
        """
        if db_path is None:
            # 在ai_agent目录下创建数据库
            db_dir = Path(__file__).parent.parent / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "conversations.db")
        
        self.db_path = db_path
        self._init_database()
        
        # 短期记忆缓存（在内存中）
        self.short_term_memory: Dict[str, List[Dict]] = {}
        
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 对话历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    character_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    intent TEXT,
                    emotion TEXT,
                    context TEXT,  -- JSON格式的上下文信息
                    timestamp TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 用户偏好表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, preference_key)
                )
            """)
            
            # 角色状态表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS character_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    character_id TEXT NOT NULL,
                    state_data TEXT NOT NULL,  -- JSON格式的状态数据
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, character_id)
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_character 
                ON conversations(user_id, character_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp)
            """)
            
            conn.commit()
    
    def store_conversation(
        self, 
        user_id: str, 
        character_id: str, 
        conversation: Dict[str, Any]
    ):
        """
        存储对话到长期记忆
        
        Args:
            user_id: 用户ID
            character_id: 角色ID
            conversation: 对话数据
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO conversations 
                    (user_id, character_id, user_message, assistant_response, 
                     intent, emotion, context, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    character_id,
                    conversation.get("user_message", ""),
                    conversation.get("assistant_response", ""),
                    conversation.get("intent", ""),
                    conversation.get("emotion", ""),
                    json.dumps(conversation.get("context", {}), ensure_ascii=False),
                    conversation.get("timestamp", datetime.now().isoformat())
                ))
                
                conn.commit()
                
            # 同时存储到短期记忆
            self._store_to_short_term(user_id, character_id, conversation)
            
        except Exception as e:
            print(f"❌ 存储对话记忆失败: {e}")
    
    def _store_to_short_term(
        self, 
        user_id: str, 
        character_id: str, 
        conversation: Dict[str, Any]
    ):
        """存储到短期记忆（内存缓存）"""
        key = f"{user_id}:{character_id}"
        
        if key not in self.short_term_memory:
            self.short_term_memory[key] = []
        
        self.short_term_memory[key].append(conversation)
        
        # 限制短期记忆大小（最近20条）
        if len(self.short_term_memory[key]) > 20:
            self.short_term_memory[key] = self.short_term_memory[key][-20:]
    
    def get_conversation_history(
        self, 
        user_id: str, 
        character_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史
        
        Args:
            user_id: 用户ID
            character_id: 角色ID
            limit: 返回条数限制
            
        Returns:
            对话历史列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_message, assistant_response, intent, emotion, 
                           context, timestamp, created_at
                    FROM conversations 
                    WHERE user_id = ? AND character_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, character_id, limit))
                
                rows = cursor.fetchall()
                
                conversations = []
                for row in rows:
                    conversations.append({
                        "user_message": row[0],
                        "assistant_response": row[1],
                        "intent": row[2],
                        "emotion": row[3],
                        "context": json.loads(row[4]) if row[4] else {},
                        "timestamp": row[5],
                        "created_at": row[6]
                    })
                
                # 按时间正序返回（最早的在前）
                return list(reversed(conversations))
                
        except Exception as e:
            print(f"❌ 获取对话历史失败: {e}")
            return []
    
    def get_relevant_memory(
        self, 
        user_id: str, 
        character_id: str, 
        query: str, 
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        获取相关记忆
        
        Args:
            user_id: 用户ID
            character_id: 角色ID
            query: 查询文本
            days_back: 回溯天数
            
        Returns:
            相关记忆数据
        """
        try:
            # 计算时间范围
            cutoff_time = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 搜索相关对话（简单关键词匹配）
                keywords = query.split()
                where_conditions = []
                params = [user_id, character_id, cutoff_time]
                
                for keyword in keywords[:3]:  # 最多使用3个关键词
                    where_conditions.append(
                        "(user_message LIKE ? OR assistant_response LIKE ?)"
                    )
                    params.extend([f"%{keyword}%", f"%{keyword}%"])
                
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                
                query_sql = f"""
                    SELECT user_message, assistant_response, intent, emotion, 
                           context, timestamp
                    FROM conversations 
                    WHERE user_id = ? AND character_id = ? AND timestamp > ? 
                    AND ({where_clause})
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                
                cursor.execute(query_sql, params)
                rows = cursor.fetchall()
                
                relevant_conversations = []
                for row in rows:
                    relevant_conversations.append({
                        "user_message": row[0],
                        "assistant_response": row[1],
                        "intent": row[2],
                        "emotion": row[3],
                        "context": json.loads(row[4]) if row[4] else {},
                        "timestamp": row[5]
                    })
                
                return {
                    "conversations": relevant_conversations,
                    "query": query,
                    "timeframe": f"最近{days_back}天"
                }
                
        except Exception as e:
            print(f"❌ 获取相关记忆失败: {e}")
            return {"conversations": [], "query": query, "timeframe": f"最近{days_back}天"}
    
    def get_user_preferences(self, user_id: str) -> Dict[str, str]:
        """
        获取用户偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户偏好字典
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT preference_key, preference_value
                    FROM user_preferences 
                    WHERE user_id = ?
                """, (user_id,))
                
                rows = cursor.fetchall()
                return {row[0]: row[1] for row in rows}
                
        except Exception as e:
            print(f"❌ 获取用户偏好失败: {e}")
            return {}
    
    def update_user_preference(
        self, 
        user_id: str, 
        preference_key: str, 
        preference_value: str
    ):
        """
        更新用户偏好
        
        Args:
            user_id: 用户ID
            preference_key: 偏好键
            preference_value: 偏好值
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, preference_key, preference_value, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (user_id, preference_key, preference_value))
                
                conn.commit()
                
        except Exception as e:
            print(f"❌ 更新用户偏好失败: {e}")
    
    def get_character_state(self, user_id: str, character_id: str) -> Dict[str, Any]:
        """
        获取角色状态
        
        Args:
            user_id: 用户ID
            character_id: 角色ID
            
        Returns:
            角色状态数据
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT state_data
                    FROM character_states 
                    WHERE user_id = ? AND character_id = ?
                """, (user_id, character_id))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                
                return {}
                
        except Exception as e:
            print(f"❌ 获取角色状态失败: {e}")
            return {}
    
    def update_character_state(
        self, 
        user_id: str, 
        character_id: str, 
        state_data: Dict[str, Any]
    ):
        """
        更新角色状态
        
        Args:
            user_id: 用户ID
            character_id: 角色ID
            state_data: 状态数据
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO character_states 
                    (user_id, character_id, state_data, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (user_id, character_id, json.dumps(state_data, ensure_ascii=False)))
                
                conn.commit()
                
        except Exception as e:
            print(f"❌ 更新角色状态失败: {e}")
    
    def clear_old_conversations(self, days_to_keep: int = 30):
        """
        清理旧对话记录
        
        Args:
            days_to_keep: 保留天数
        """
        try:
            cutoff_time = (datetime.now() - timedelta(days=days_to_keep))
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM conversations 
                    WHERE created_at < ?
                """, (cutoff_time,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"🗑️ 清理了 {deleted_count} 条旧对话记录")
                
        except Exception as e:
            print(f"❌ 清理对话记录失败: {e}")
    
    def get_conversation_stats(self, user_id: str) -> Dict[str, Any]:
        """
        获取对话统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总对话数
                cursor.execute("""
                    SELECT COUNT(*) FROM conversations WHERE user_id = ?
                """, (user_id,))
                total_conversations = cursor.fetchone()[0]
                
                # 按角色分组统计
                cursor.execute("""
                    SELECT character_id, COUNT(*) 
                    FROM conversations 
                    WHERE user_id = ?
                    GROUP BY character_id
                """, (user_id,))
                character_stats = dict(cursor.fetchall())
                
                # 最近7天对话数
                recent_cutoff = (datetime.now() - timedelta(days=7)).isoformat()
                cursor.execute("""
                    SELECT COUNT(*) FROM conversations 
                    WHERE user_id = ? AND timestamp > ?
                """, (user_id, recent_cutoff))
                recent_conversations = cursor.fetchone()[0]
                
                return {
                    "total_conversations": total_conversations,
                    "character_stats": character_stats,
                    "recent_conversations": recent_conversations,
                    "user_id": user_id
                }
                
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {
                "total_conversations": 0,
                "character_stats": {},
                "recent_conversations": 0,
                "user_id": user_id
            }

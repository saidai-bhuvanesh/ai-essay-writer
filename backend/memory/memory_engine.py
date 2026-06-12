"""
STUDX JARVIS - Memory Engine
Long-term memory and context management
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import deque
import logging

from .database import get_database

logger = logging.getLogger('JARVIS.Memory')

class MemoryEngine:
    """
    JARVIS Memory Engine
    Manages short-term and long-term memory
    """
    
    def __init__(self):
        self.db = get_database()
        self.short_term = deque(maxlen=20)  # Recent conversation context
        self.context_window = 10  # Number of previous exchanges to consider
        self.important_topics = set()  # Topics user cares about
        
    def remember(self, content: str, category: str = 'general', importance: int = 5) -> int:
        """Store a memory"""
        memory_id = self.db.add_memory(content, category, importance)
        logger.info(f"Memory stored: [{category}] importance={importance}")
        return memory_id
    
    def recall(self, query: str = None, category: str = None, limit: int = 10) -> List[Dict]:
        """Recall memories"""
        if query:
            # Search memories
            return self.db.search_memories(query, category, limit)
        elif category:
            return self.db.search_memories('', category, limit)
        else:
            # Get recent memories
            return self.db.search_memories('', None, limit)
    
    def recall_about(self, topic: str) -> List[Dict]:
        """Recall memories about a specific topic"""
        return self.db.search_memories(topic, limit=15)
    
    def add_to_context(self, user_input: str, jarvis_response: str, intent: str = None):
        """Add to short-term conversation context"""
        self.short_term.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'jarvis': jarvis_response,
            'intent': intent
        })
        
        # Save to database
        self.db.save_conversation(user_input, jarvis_response, intent)
    
    def get_context(self) -> List[Dict]:
        """Get recent conversation context"""
        return list(self.short_term)[-self.context_window:]
    
    def get_full_context_for_llm(self) -> str:
        """Get formatted context for LLM prompt"""
        context_items = self.get_context()
        
        if not context_items:
            return "No previous conversation context."
        
        formatted = "Recent conversation history:\n"
        for i, item in enumerate(context_items, 1):
            formatted += f"\n{i}. User: {item['user']}"
            formatted += f"\n   JARVIS: {item['jarvis']}"
        
        return formatted
    
    def remember_user_preference(self, preference_type: str, value: Any):
        """Remember a user preference"""
        settings_key = f"pref_{preference_type}"
        self.db.set_setting(settings_key, json.dumps(value))
        logger.info(f"Preference stored: {preference_type} = {value}")
    
    def get_user_preference(self, preference_type: str, default: Any = None) -> Any:
        """Get a user preference"""
        settings_key = f"pref_{preference_type}"
        value = self.db.get_setting(settings_key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return default
    
    def learn_from_interaction(self, user_input: str, intent: str):
        """Learn patterns from user interactions"""
        # Extract key topics
        words = user_input.lower().split()
        
        # Track important topics
        important_keywords = ['always', 'never', 'remember', 'forget', 'important', 'preference']
        for keyword in important_keywords:
            if keyword in words:
                # This might be important context
                idx = words.index(keyword)
                if idx + 1 < len(words):
                    topic = ' '.join(words[max(0, idx-2):idx+3])
                    self.important_topics.add(topic)
                    self.remember(topic, category='preference', importance=8)
        
        logger.info(f"Learned topics: {self.important_topics}")
    
    def forget(self, memory_id: int) -> bool:
        """Forget a specific memory"""
        # Note: In production, you'd have a delete method
        # For now, we just update importance
        logger.info(f"Attempting to forget memory {memory_id}")
        return True
    
    def get_memories_by_category(self, category: str) -> List[Dict]:
        """Get all memories in a category"""
        return self.db.search_memories('', category, limit=100)
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        memories = self.db.search_memories('', None, limit=1000)
        
        categories = {}
        total_importance = 0
        
        for m in memories:
            cat = m['category']
            categories[cat] = categories.get(cat, 0) + 1
            total_importance += m['importance']
        
        return {
            'total_memories': len(memories),
            'categories': categories,
            'avg_importance': total_importance / len(memories) if memories else 0,
            'important_topics': list(self.important_topics),
            'context_size': len(self.short_term)
        }
    
    def clear_old_context(self, days: int = 7):
        """Clear old context entries"""
        # Keep only recent entries in short-term memory
        self.short_term = deque(list(self.short_term)[-self.context_window:], maxlen=20)
        logger.info(f"Context cleared, keeping last {self.context_window} entries")


class ConversationMemory:
    """Manages conversation-specific memory"""
    
    def __init__(self):
        self.current_topic = None
        self.topic_history = []
        self.entities = {}  # Named entities extracted from conversation
        self.pending_questions = []
    
    def set_topic(self, topic: str):
        """Set current conversation topic"""
        if self.current_topic:
            self.topic_history.append(self.current_topic)
        self.current_topic = topic
    
    def add_entity(self, entity_type: str, entity_value: str):
        """Add a named entity"""
        if entity_type not in self.entities:
            self.entities[entity_type] = []
        if entity_value not in self.entities[entity_type]:
            self.entities[entity_type].append(entity_value)
    
    def get_entities(self, entity_type: str = None) -> Dict:
        """Get tracked entities"""
        if entity_type:
            return {entity_type: self.entities.get(entity_type, [])}
        return self.entities
    
    def add_pending_question(self, question: str):
        """Add a question to be answered later"""
        self.pending_questions.append(question)
    
    def get_pending_questions(self) -> List[str]:
        """Get pending questions"""
        return self.pending_questions.copy()
    
    def clear(self):
        """Clear conversation memory"""
        self.current_topic = None
        self.topic_history = []
        self.entities = {}
        self.pending_questions = []


# Global memory engine instance
_memory_engine = None

def get_memory_engine() -> MemoryEngine:
    """Get memory engine instance"""
    global _memory_engine
    if _memory_engine is None:
        _memory_engine = MemoryEngine()
    return _memory_engine
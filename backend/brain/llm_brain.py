"""
STUDX JARVIS - LLM Brain
AI reasoning and command generation with Ollama
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..memory.memory_engine import get_memory_engine

logger = logging.getLogger('JARVIS.Brain')

class LLMBrain:
    """
    JARVIS AI Brain
    Handles LLM integration, intent detection, and reasoning
    """
    
    def __init__(self):
        self.llm_provider = os.getenv('LLM_PROVIDER', 'ollama')
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.llm_model = os.getenv('LLM_MODEL', 'llama3')
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2048'))
        
        self.memory = get_memory_engine()
        self.is_connected = False
        
        self._check_connection()
        
        logger.info(f"LLM Brain initialized: provider={self.llm_provider}, model={self.llm_model}")
    
    def _check_connection(self):
        """Check if LLM service is available"""
        try:
            if self.llm_provider == 'ollama':
                import requests
                response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
                if response.status_code == 200:
                    self.is_connected = True
                    logger.info("Ollama connection established")
                else:
                    logger.warning(f"Ollama returned status: {response.status_code}")
        except Exception as e:
            logger.warning(f"LLM service not available: {e}")
            self.is_connected = False
    
    def process(self, user_input: str) -> str:
        """
        Process user input and generate response
        
        Args:
            user_input: User's text or voice input
        
        Returns:
            JARVIS response
        """
        logger.info(f"Processing: {user_input}")
        
        # Detect intent
        intent = self.detect_intent(user_input)
        logger.info(f"Detected intent: {intent}")
        
        # Get conversation context
        context = self.memory.get_full_context_for_llm()
        
        # Generate response
        if self.is_connected:
            response = self._generate_with_llm(user_input, intent, context)
        else:
            response = self._generate_fallback(user_input, intent)
        
        # Save to memory
        self.memory.add_to_context(user_input, response, intent)
        self.memory.learn_from_interaction(user_input, intent)
        
        return response
    
    def detect_intent(self, user_input: str) -> str:
        """
        Detect user intent from input
        
        Returns:
            Intent category
        """
        user_lower = user_input.lower()
        
        # Intent patterns
        intents = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
            'farewell': ['bye', 'goodbye', 'see you', 'talk later', 'stop'],
            'task': ['do', 'create', 'make', 'build', 'write', 'open', 'start'],
            'question': ['what', 'how', 'why', 'when', 'where', 'which', 'who', 'explain'],
            'search': ['search', 'find', 'look up', 'google', 'browse'],
            'control': ['turn on', 'turn off', 'open', 'close', 'start', 'stop', 'restart'],
            'memory': ['remember', 'forget', 'remind', 'tell me about', 'what do you know'],
            'project': ['project', 'task', 'deadline', 'milestone', 'progress'],
            'code': ['code', 'programming', 'function', 'class', 'debug', 'refactor'],
            'help': ['help', 'assist', 'support', 'guide', 'explain'],
            'settings': ['setting', 'preference', 'configure', 'change', 'option'],
        }
        
        for intent_name, keywords in intents.items():
            for keyword in keywords:
                if keyword in user_lower:
                    return intent_name
        
        return 'general'
    
    def _generate_with_llm(self, user_input: str, intent: str, context: str) -> str:
        """Generate response using LLM"""
        try:
            import requests
            
            # Build prompt
            prompt = self._build_prompt(user_input, intent, context)
            
            # Call Ollama
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    'model': self.llm_model,
                    'prompt': prompt,
                    'temperature': self.temperature,
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"LLM error: {response.status_code}")
                return self._generate_fallback(user_input, intent)
                
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return self._generate_fallback(user_input, intent)
    
    def _build_prompt(self, user_input: str, intent: str, context: str) -> str:
        """Build prompt for LLM"""
        memories = self.memory.recall_about(user_input)
        memory_context = ""
        
        if memories:
            memory_context = "\n\nRelevant memories:\n"
            for m in memories[:5]:
                memory_context += f"- {m['content']} (importance: {m['importance']})\n"
        
        prompt = f"""You are JARVIS, a helpful AI assistant. You are intelligent, witty, and always ready to help.

Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Detected intent: {intent}

{context}
{memory_context}

User: {user_input}

JARVIS: """
        
        return prompt
    
    def _generate_fallback(self, user_input: str, intent: str) -> str:
        """Fallback response when LLM is unavailable"""
        user_lower = user_input.lower()
        
        # Basic response patterns
        if intent == 'greeting':
            return "Hello! I'm JARVIS, your AI assistant. How can I help you today?"
        
        elif intent == 'farewell':
            return "Goodbye! Feel free to return whenever you need assistance."
        
        elif intent == 'task':
            return "I understand you want me to perform a task. Let me help you with that. Could you provide more details?"
        
        elif intent == 'question':
            return "That's an interesting question. "
        
        elif intent == 'search':
            return "I can help you search for information. What would you like to find?"
        
        elif intent == 'control':
            return "I can help you control your system. What would you like me to do?"
        
        elif intent == 'memory':
            if 'remember' in user_lower:
                return "I'll remember that for you. Is there anything specific you'd like me to store?"
            elif 'forget' in user_lower:
                return "I can try to forget that information. What would you like me to remove?"
            else:
                return "Let me recall what I know about that..."
        
        elif intent == 'project':
            return "I can help you manage your projects. What would you like to know?"
        
        elif intent == 'code':
            return "I can help you with coding tasks. What are you working on?"
        
        elif intent == 'help':
            return "I'm here to help! I can assist with voice commands, tasks, information search, project management, and more. What would you like help with?"
        
        elif intent == 'settings':
            return "I can help you adjust settings. What would you like to configure?"
        
        else:
            return "I understand. Let me think about how to help you with that."
    
    def chat(self, message: str, system_prompt: str = None) -> str:
        """
        Chat completion
        
        Args:
            message: User message
            system_prompt: Optional system prompt override
        
        Returns:
            Assistant response
        """
        context = self.memory.get_full_context_for_llm()
        intent = self.detect_intent(message)
        
        if system_prompt:
            prompt = f"""{system_prompt}

Conversation history:
{context}

User: {message}

Assistant: """
        else:
            prompt = self._build_prompt(message, intent, context)
        
        if self.is_connected:
            return self._generate_with_llm(message, intent, context)
        else:
            return self._generate_fallback(message, intent)
    
    def generate_code(self, description: str, language: str = 'python') -> str:
        """Generate code based on description"""
        prompt = f"""You are an expert {language} programmer. Write clean, well-documented code based on the following description:

Task: {description}

Requirements:
- Write idiomatic {language} code
- Include comments explaining key sections
- Handle errors gracefully
- Follow best practices

Code:"""
        
        try:
            import requests
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    'model': self.llm_model,
                    'prompt': prompt,
                    'temperature': 0.3,  # Lower temperature for code
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
        except Exception as e:
            logger.error(f"Code generation error: {e}")
        
        return "# Code generation unavailable - LLM not connected"
    
    def summarize(self, text: str, max_length: int = 100) -> str:
        """Summarize text"""
        prompt = f"""Summarize the following text in no more than {max_length} words:

{text}

Summary:"""
        
        try:
            import requests
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    'model': self.llm_model,
                    'prompt': prompt,
                    'temperature': 0.3,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
        except Exception as e:
            logger.error(f"Summarization error: {e}")
        
        return text[:max_length] + "..." if len(text) > max_length else text


class IntentClassifier:
    """Advanced intent classification"""
    
    def __init__(self, llm_brain: LLMBrain):
        self.brain = llm_brain
    
    def classify(self, text: str) -> Dict[str, Any]:
        """Classify intent with confidence"""
        intent = self.brain.detect_intent(text)
        
        # Calculate simple confidence based on keyword matching
        confidence = 0.5  # Default confidence
        
        keywords_map = {
            'greeting': ['hello', 'hi', 'hey', 'greetings'],
            'farewell': ['bye', 'goodbye', 'exit', 'quit'],
            'task': ['do', 'create', 'make', 'build', 'execute', 'run'],
            'question': ['what', 'how', 'why', 'when', 'where', '?'],
            'search': ['search', 'find', 'look', 'google'],
            'control': ['open', 'close', 'start', 'stop', 'turn'],
        }
        
        text_lower = text.lower()
        for intent_name, keywords in keywords_map.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                confidence = min(0.9, 0.5 + (matches * 0.15))
                if intent == intent_name:
                    break
        
        return {
            'intent': intent,
            'confidence': confidence,
            'text': text
        }


# Global brain instance
_brain = None

def get_brain() -> LLMBrain:
    """Get brain instance"""
    global _brain
    if _brain is None:
        _brain = LLMBrain()
    return _brain
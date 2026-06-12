"""
STUDX JARVIS - Multi-Agent System
"""

import os
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger('JARVIS.Agents')

class AgentType(Enum):
    PLANNER = "planner"
    CODER = "coder"
    RESEARCHER = "researcher"
    MEMORY = "memory"
    SECURITY = "security"
    COMMUNICATION = "communication"
    TASK = "task"


class Agent(ABC):
    """Base agent class"""
    
    def __init__(self, name: str, agent_type: AgentType):
        self.name = name
        self.agent_type = agent_type
        self.is_active = False
        
    @abstractmethod
    def process(self, task: Dict) -> Dict:
        """Process a task"""
        pass
    
    @abstractmethod
    def can_handle(self, task: Dict) -> bool:
        """Check if agent can handle this task"""
        pass
    
    def activate(self):
        """Activate the agent"""
        self.is_active = True
        logger.info(f"Agent {self.name} activated")
    
    def deactivate(self):
        """Deactivate the agent"""
        self.is_active = False
        logger.info(f"Agent {self.name} deactivated")


class PlannerAgent(Agent):
    """Planner Agent - Breaks down complex tasks into subtasks"""
    
    def __init__(self):
        super().__init__("Planner", AgentType.PLANNER)
    
    def can_handle(self, task: Dict) -> bool:
        return task.get('type') in ['complex', 'multi-step', 'planning']
    
    def process(self, task: Dict) -> Dict:
        """Break down a complex task"""
        description = task.get('description', '')
        
        try:
            from ..brain.llm_brain import get_brain
            brain = get_brain()
            
            prompt = f"""Break down this task into smaller, actionable steps:

Task: {description}

Provide the steps as a numbered list. Be specific about each step."""
            
            response = brain.chat(prompt)
            steps = self._parse_steps(response)
            
            return {
                'success': True,
                'original_task': description,
                'subtasks': steps,
                'estimated_steps': len(steps)
            }
            
        except Exception as e:
            logger.error(f"Planner error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_steps(self, response: str) -> List[str]:
        """Parse steps from LLM response"""
        steps = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                step = line.lstrip('0123456789.-) ')
                if step:
                    steps.append(step)
        return steps


class CoderAgent(Agent):
    """Coder Agent - Writes and reviews code"""
    
    def __init__(self):
        super().__init__("Coder", AgentType.CODER)
        self.supported_languages = ['python', 'javascript', 'typescript', 'java', 'c++', 'go', 'rust']
    
    def can_handle(self, task: Dict) -> bool:
        task_type = task.get('type', '')
        return task_type in ['code', 'programming', 'debug', 'refactor', 'review']
    
    def process(self, task: Dict) -> Dict:
        """Generate code"""
        description = task.get('description', '')
        language = task.get('language', 'python')
        
        if language.lower() not in self.supported_languages:
            return {'success': False, 'error': f'Unsupported language: {language}'}
        
        try:
            from ..brain.llm_brain import get_brain
            brain = get_brain()
            code = brain.generate_code(description, language)
            
            return {
                'success': True,
                'code': code,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Coder error: {e}")
            return {'success': False, 'error': str(e)}


class ResearcherAgent(Agent):
    """Researcher Agent - Searches and summarizes information"""
    
    def __init__(self):
        super().__init__("Researcher", AgentType.RESEARCHER)
    
    def can_handle(self, task: Dict) -> bool:
        return task.get('type') in ['research', 'search', 'information', 'learn']
    
    def process(self, task: Dict) -> Dict:
        """Research a topic"""
        query = task.get('query', task.get('description', ''))
        
        try:
            from ..brain.llm_brain import get_brain
            brain = get_brain()
            
            summary = brain.summarize(f"Information about: {query}", max_length=200)
            
            return {
                'success': True,
                'query': query,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Researcher error: {e}")
            return {'success': False, 'error': str(e)}


class MemoryAgent(Agent):
    """Memory Agent - Manages and retrieves memories"""
    
    def __init__(self):
        super().__init__("Memory", AgentType.MEMORY)
    
    def can_handle(self, task: Dict) -> bool:
        return task.get('type') in ['memory', 'remember', 'recall', 'forget']
    
    def process(self, task: Dict) -> Dict:
        """Manage memory"""
        action = task.get('action', 'remember')
        
        try:
            from ..memory.memory_engine import get_memory_engine
            memory = get_memory_engine()
            
            if action == 'remember':
                content = task.get('content', task.get('description', ''))
                category = task.get('category', 'general')
                importance = task.get('importance', 5)
                memory_id = memory.remember(content, category, importance)
                
                return {
                    'success': True,
                    'action': 'remembered',
                    'memory_id': memory_id
                }
                
            elif action == 'recall':
                topic = task.get('query', task.get('description', ''))
                memories = memory.recall_about(topic)
                
                return {
                    'success': True,
                    'action': 'recalled',
                    'memories': memories
                }
            
            return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            logger.error(f"Memory agent error: {e}")
            return {'success': False, 'error': str(e)}


class SecurityAgent(Agent):
    """Security Agent - Handles security and authentication"""
    
    def __init__(self):
        super().__init__("Security", AgentType.SECURITY)
    
    def can_handle(self, task: Dict) -> bool:
        return task.get('type') in ['security', 'auth', 'permission', 'access']
    
    def process(self, task: Dict) -> Dict:
        """Handle security tasks"""
        action = task.get('action', '')
        
        try:
            from ..security.auth import get_security_manager
            
            if action == 'check_permission':
                user = task.get('user', {})
                permission = task.get('permission', '')
                security = get_security_manager()
                has_permission = security.check_permission(user, permission)
                
                return {
                    'success': True,
                    'has_permission': has_permission
                }
                
            elif action == 'authenticate':
                email = task.get('email')
                password = task.get('password')
                security = get_security_manager()
                user = security.authenticate(email, password)
                
                return {
                    'success': user is not None,
                    'user': user
                }
            
            return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            logger.error(f"Security agent error: {e}")
            return {'success': False, 'error': str(e)}


class TaskAgent(Agent):
    """Task Agent - Manages tasks and projects"""
    
    def __init__(self):
        super().__init__("Task", AgentType.TASK)
    
    def can_handle(self, task: Dict) -> bool:
        return task.get('type') in ['task', 'project', 'todo', 'manage']
    
    def process(self, task: Dict) -> Dict:
        """Handle task management"""
        action = task.get('action', '')
        
        try:
            from ..memory.database import get_database
            
            if action == 'create_task':
                task_text = task.get('description', '')
                project_id = task.get('project_id')
                priority = task.get('priority', 5)
                db = get_database()
                task_id = db.create_task(task_text, project_id, priority)
                
                return {
                    'success': True,
                    'action': 'task_created',
                    'task_id': task_id
                }
                
            elif action == 'complete_task':
                task_id = task.get('task_id')
                db = get_database()
                db.complete_task(task_id)
                
                return {
                    'success': True,
                    'action': 'task_completed'
                }
                
            elif action == 'create_project':
                name = task.get('name', '')
                description = task.get('description', '')
                db = get_database()
                project_id = db.create_project(name, description)
                
                return {
                    'success': True,
                    'action': 'project_created',
                    'project_id': project_id
                }
            
            return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            logger.error(f"Task agent error: {e}")
            return {'success': False, 'error': str(e)}


class MultiAgentSystem:
    """JARVIS Multi-Agent System"""
    
    def __init__(self):
        self.agents: Dict[AgentType, Agent] = {}
        self._register_agents()
        logger.info(f"Multi-agent system initialized with {len(self.agents)} agents")
    
    def _register_agents(self):
        """Register all available agents"""
        self.agents[AgentType.PLANNER] = PlannerAgent()
        self.agents[AgentType.CODER] = CoderAgent()
        self.agents[AgentType.RESEARCHER] = ResearcherAgent()
        self.agents[AgentType.MEMORY] = MemoryAgent()
        self.agents[AgentType.SECURITY] = SecurityAgent()
        self.agents[AgentType.TASK] = TaskAgent()
        
        for agent in self.agents.values():
            agent.activate()
    
    def route_task(self, task: Dict) -> Dict:
        """Route task to appropriate agent"""
        for agent_type, agent in self.agents.items():
            if agent.can_handle(task):
                result = agent.process(task)
                result['agent'] = agent.name
                return result
        
        return {'success': False, 'error': 'No agent available for this task'}
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        return {
            agent_type.value: {
                'name': agent.name,
                'active': agent.is_active
            }
            for agent_type, agent in self.agents.items()
        }


_multi_agent_system = None

def get_multi_agent_system() -> MultiAgentSystem:
    """Get multi-agent system instance"""
    global _multi_agent_system
    if _multi_agent_system is None:
        _multi_agent_system = MultiAgentSystem()
    return _multi_agent_system
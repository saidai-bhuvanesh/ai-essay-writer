"""
STUDX JARVIS - Backend Package
"""

from .memory import get_database, init_database, get_memory_engine
from .brain import get_brain
from .security import get_security_manager
from .voice import get_voice_processor
from .automation import get_system_controller
from .vision import get_vision_manager
from .agents import get_multi_agent_system

__version__ = "1.0"

__all__ = [
    'get_database', 'init_database', 'get_memory_engine',
    'get_brain', 'get_security_manager', 'get_voice_processor',
    'get_system_controller', 'get_vision_manager', 'get_multi_agent_system'
]
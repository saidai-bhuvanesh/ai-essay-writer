"""
STUDX JARVIS - Automation Module
"""

from .system_control import (
    SystemController, BrowserAutomator, TaskAutomator,
    get_system_controller, get_task_automator
)

__all__ = [
    'SystemController', 'BrowserAutomator', 'TaskAutomator',
    'get_system_controller', 'get_task_automator'
]
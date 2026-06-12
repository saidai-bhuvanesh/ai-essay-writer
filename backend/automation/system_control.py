"""
STUDX JARVIS - Automation Module
System and browser automation
"""

import os
import logging
import subprocess
import webbrowser
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger('JARVIS.Automation')

class SystemController:
    """
    JARVIS System Controller
    Handles system-level automation tasks
    """
    
    def __init__(self):
        self.platform = os.name  # 'nt' for Windows, 'posix' for Unix
        self.automations_enabled = True
        
        logger.info(f"System controller initialized (platform: {self.platform})")
    
    # Application Control
    def open_application(self, app_name: str) -> bool:
        """Open an application"""
        try:
            app_lower = app_name.lower()
            
            if self.platform == 'nt':  # Windows
                return self._open_windows(app_lower)
            else:  # Unix/Mac
                return self._open_unix(app_lower)
                
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return False
    
    def _open_windows(self, app_name: str) -> bool:
        """Open application on Windows"""
        apps = {
            'chrome': 'start chrome',
            'browser': 'start chrome',
            'vscode': 'code',
            'code': 'code',
            'notepad': 'notepad',
            'explorer': 'explorer',
            'terminal': 'start cmd',
            'cmd': 'start cmd',
            'powershell': 'start powershell',
            'firefox': 'start firefox',
            'edge': 'start msedge',
            'word': 'start winword',
            'excel': 'start excel',
            'outlook': 'start outlook',
        }
        
        if app_name in apps:
            subprocess.Popen(apps[app_name], shell=True)
            logger.info(f"Opened: {app_name}")
            return True
        
        # Try direct launch
        subprocess.Popen(f'start {app_name}', shell=True)
        return True
    
    def _open_unix(self, app_name: str) -> bool:
        """Open application on Unix/Mac"""
        apps = {
            'chrome': 'google-chrome',
            'browser': 'google-chrome',
            'vscode': 'code',
            'code': 'code',
            'firefox': 'firefox',
            'safari': 'safari',
            'terminal': 'gnome-terminal',
            'finder': 'open .',
        }
        
        if app_name in apps:
            subprocess.Popen([apps[app_name]], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            logger.info(f"Opened: {app_name}")
            return True
        
        # Try xdg-open for unknown apps
        subprocess.Popen(['xdg-open', app_name],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        return True
    
    def close_application(self, app_name: str) -> bool:
        """Close an application"""
        try:
            if self.platform == 'nt':
                subprocess.run(f'taskkill /IM {app_name}.exe /F', shell=True)
            else:
                subprocess.run(['pkill', app_name], shell=True)
            logger.info(f"Closed: {app_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to close {app_name}: {e}")
            return False
    
    # File Operations
    def create_file(self, path: str, content: str = '') -> bool:
        """Create a file"""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            logger.info(f"Created file: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create file: {e}")
            return False
    
    def read_file(self, path: str) -> Optional[str]:
        """Read a file"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return None
    
    def delete_file(self, path: str) -> bool:
        """Delete a file"""
        try:
            p = Path(path)
            if p.exists():
                p.unlink()
                logger.info(f"Deleted file: {path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def list_directory(self, path: str = '.') -> List[str]:
        """List directory contents"""
        try:
            return [str(p) for p in Path(path).iterdir()]
        except Exception as e:
            logger.error(f"Failed to list directory: {e}")
            return []
    
    # System Commands
    def execute_command(self, command: str) -> Dict:
        """Execute a system command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timed out'}
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'battery': psutil.sensors_battery().percent if psutil.sensors_battery() else None,
                'platform': self.platform
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}
    
    # Clipboard
    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard"""
        try:
            import pyperclip
            pyperclip.copy(text)
            logger.info("Text copied to clipboard")
            return True
        except Exception as e:
            logger.error(f"Clipboard copy failed: {e}")
            return False
    
    def paste_from_clipboard(self) -> str:
        """Get text from clipboard"""
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception as e:
            logger.error(f"Clipboard paste failed: {e}")
            return ""


class BrowserAutomator:
    """
    Browser automation using Playwright
    """
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.is_connected = False
        
        self._init_browser()
    
    def _init_browser(self):
        """Initialize browser"""
        try:
            from playwright.sync_api import sync_playwright
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self.is_connected = True
            
            logger.info("Browser automation initialized")
            
        except ImportError:
            logger.warning("Playwright not installed - browser automation unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
    
    def navigate(self, url: str) -> bool:
        """Navigate to URL"""
        if not self.is_connected:
            return False
        
        try:
            self.page.goto(url, wait_until='networkidle')
            logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def click(self, selector: str) -> bool:
        """Click an element"""
        if not self.is_connected:
            return False
        
        try:
            self.page.click(selector)
            return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
    
    def type_text(self, selector: str, text: str) -> bool:
        """Type text into an element"""
        if not self.is_connected:
            return False
        
        try:
            self.page.fill(selector, text)
            return True
        except Exception as e:
            logger.error(f"Type text failed: {e}")
            return False
    
    def get_text(self, selector: str) -> Optional[str]:
        """Get text from element"""
        if not self.is_connected:
            return None
        
        try:
            return self.page.text_content(selector)
        except Exception as e:
            logger.error(f"Get text failed: {e}")
            return None
    
    def screenshot(self, path: str = None) -> Optional[bytes]:
        """Take screenshot"""
        if not self.is_connected:
            return None
        
        try:
            return self.page.screenshot(path=path)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
            self.playwright.stop()
            self.is_connected = False
            logger.info("Browser closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


class TaskAutomator:
    """
    Automate repetitive tasks
    """
    
    def __init__(self):
        self.is_automating = False
        
    def auto_type(self, text: str, delay: float = 0.05):
        """Automatically type text"""
        try:
            import pyautogui
            import time
            
            self.is_automating = True
            pyautogui.write(text, interval=delay)
            self.is_automating = False
            
        except ImportError:
            logger.error("pyautogui not installed")
        except Exception as e:
            logger.error(f"Auto type failed: {e}")
            self.is_automating = False
    
    def auto_click(self, x: int, y: int, clicks: int = 1):
        """Automatically click"""
        try:
            import pyautogui
            pyautogui.click(x, y, clicks=clicks)
        except ImportError:
            logger.error("pyautogui not installed")
    
    def press_key(self, key: str):
        """Press a key"""
        try:
            import pyautogui
            pyautogui.press(key)
        except ImportError:
            logger.error("pyautogui not installed")
    
    def hotkey(self, *keys):
        """Press a hotkey combination"""
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
        except ImportError:
            logger.error("pyautogui not installed")
    
    def scroll(self, clicks: int):
        """Scroll the mouse wheel"""
        try:
            import pyautogui
            pyautogui.scroll(clicks)
        except ImportError:
            logger.error("pyautogui not installed")


# Global instances
_system_controller = None
_task_automator = None

def get_system_controller() -> SystemController:
    """Get system controller instance"""
    global _system_controller
    if _system_controller is None:
        _system_controller = SystemController()
    return _system_controller

def get_task_automator() -> TaskAutomator:
    """Get task automator instance"""
    global _task_automator
    if _task_automator is None:
        _task_automator = TaskAutomator()
    return _task_automator
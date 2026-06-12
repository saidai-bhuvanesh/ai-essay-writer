"""
STUDX JARVIS - Main Entry Point
Local AI-Powered Personal Assistant
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup paths
BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / os.getenv('LOG_PATH', 'logs')
DATABASE_PATH = BASE_DIR / os.getenv('DATABASE_PATH', 'database/jarvis_db.sqlite')

# Ensure directories exist
LOG_PATH.mkdir(parents=True, exist_ok=True)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH / 'jarvis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('JARVIS')

class JarvisCore:
    """Main JARVIS Core Controller"""
    
    def __init__(self):
        self.name = os.getenv('APP_NAME', 'STUDX JARVIS')
        self.version = os.getenv('VERSION', 'v1.0')
        self.owner = os.getenv('OWNER', 'User')
        self.running = False
        
        logger.info(f"Initializing {self.name} v{self.version}")
        logger.info(f"Owner: {self.owner}")
        
    def initialize(self):
        """Initialize all JARVIS subsystems"""
        try:
            # Import and initialize subsystems
            from backend.memory.database import init_database
            from backend.security.auth import SecurityManager
            from backend.voice.processor import VoiceProcessor
            from backend.brain.llm_brain import LLMBrain
            from backend.automation.system_control import SystemController
            
            # Initialize database
            logger.info("Initializing database...")
            init_database()
            
            # Initialize security
            logger.info("Initializing security layer...")
            self.security = SecurityManager()
            
            # Initialize voice processor
            logger.info("Initializing voice processor...")
            self.voice = VoiceProcessor()
            
            # Initialize LLM brain
            logger.info("Initializing AI brain...")
            self.brain = LLMBrain()
            
            # Initialize system controller
            logger.info("Initializing system controller...")
            self.controller = SystemController()
            
            self.running = True
            logger.info(f"{self.name} initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def start(self):
        """Start JARVIS assistant"""
        if not self.running:
            if not self.initialize():
                logger.error("Cannot start - initialization failed")
                return False
        
        logger.info(f"{self.name} is now running!")
        logger.info(f"Owner: {self.owner}")
        logger.info("Say '{wake_word}' to activate...".format(
            wake_word=os.getenv('WAKE_WORD', 'jarvis')
        ))
        return True
    
    def stop(self):
        """Stop JARVIS assistant"""
        logger.info("Shutting down JARVIS...")
        self.running = False
        logger.info("JARVIS stopped.")
    
    def process_command(self, command: str) -> str:
        """Process a command through JARVIS"""
        logger.info(f"Processing command: {command}")
        
        # Route through brain for intent detection
        response = self.brain.process(command)
        
        # Log the interaction
        from backend.memory.database import log_activity
        log_activity("command", command)
        
        return response
    
    def get_status(self) -> dict:
        """Get current JARVIS status"""
        return {
            "name": self.name,
            "version": self.version,
            "owner": self.owner,
            "running": self.running,
            "components": {
                "security": hasattr(self, 'security'),
                "voice": hasattr(self, 'voice'),
                "brain": hasattr(self, 'brain'),
                "controller": hasattr(self, 'controller')
            }
        }


# Global instance
jarvis = None

def get_jarvis():
    """Get or create global JARVIS instance"""
    global jarvis
    if jarvis is None:
        jarvis = JarvisCore()
    return jarvis


if __name__ == "__main__":
    print("=" * 50)
    print("  STUDX JARVIS - Local AI Assistant")
    print("  Version: v1.0")
    print("  Owner: Bhuvi")
    print("=" * 50)
    
    j = get_jarvis()
    if j.start():
        print("\nJARVIS is ready to serve!")
        print("Type 'exit' to stop, or use voice command 'jarvis'")
        
        # Simple CLI loop
        while j.running:
            try:
                cmd = input("\nYou: ").strip()
                if cmd.lower() in ['exit', 'quit', 'stop']:
                    j.stop()
                    break
                elif cmd:
                    response = j.process_command(cmd)
                    print(f"\nJARVIS: {response}")
            except KeyboardInterrupt:
                j.stop()
                break
            except Exception as e:
                logger.error(f"Error: {e}")
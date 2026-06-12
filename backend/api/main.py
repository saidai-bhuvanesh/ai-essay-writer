"""
STUDX JARVIS - FastAPI REST API
"""

import os
import logging
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('JARVIS.API')

# Import backend modules
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.memory.database import get_database, init_database
from backend.memory.memory_engine import get_memory_engine
from backend.brain.llm_brain import get_brain
from backend.security.auth import get_security_manager, get_session_manager
from backend.automation.system_control import get_system_controller
from backend.vision.computer_vision import get_vision_manager

# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    session_id: str

class MemoryRequest(BaseModel):
    content: str
    category: str = "general"
    importance: int = 5

class ProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    priority: int = 5

class TaskRequest(BaseModel):
    task: str
    project_id: Optional[int] = None
    priority: int = 5

class LoginRequest(BaseModel):
    email: str
    password: str

class CommandRequest(BaseModel):
    command: str
    params: Optional[dict] = {}


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JARVIS API...")
    
    # Initialize database
    init_database()
    
    # Initialize modules
    get_database()
    get_memory_engine()
    get_brain()
    get_security_manager()
    
    logger.info("JARVIS API started successfully")
    
    yield
    
    logger.info("Shutting down JARVIS API...")


# Create FastAPI app
app = FastAPI(
    title="STUDX JARVIS API",
    description="Local AI Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "STUDX JARVIS",
        "version": os.getenv("VERSION", "v1.0"),
        "timestamp": datetime.now().isoformat()
    }


# ===== Authentication Endpoints =====

@app.post("/api/auth/login", response_model=dict)
async def login(request: LoginRequest):
    """User login"""
    security = get_security_manager()
    session_mgr = get_session_manager()
    
    user = security.authenticate(request.email, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_id = session_mgr.create_session(user['id'])
    
    return {
        "success": True,
        "session_id": session_id,
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "role": user['role']
        }
    }


@app.post("/api/auth/logout")
async def logout(session_id: str):
    """User logout"""
    session_mgr = get_session_manager()
    session_mgr.destroy_session(session_id)
    return {"success": True, "message": "Logged out successfully"}


# ===== Chat Endpoints =====

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with JARVIS"""
    brain = get_brain()
    memory = get_memory_engine()
    session_mgr = get_session_manager()
    
    # Update session if provided
    if request.session_id:
        session_mgr.update_session(request.session_id)
    
    # Process message
    response = brain.process(request.message)
    
    # Detect intent for response
    intent = brain.detect_intent(request.message)
    
    # Generate new session ID if needed
    session_id = request.session_id or "default"
    
    return ChatResponse(
        response=response,
        intent=intent,
        session_id=session_id
    )


@app.post("/api/chat/voice")
async def voice_chat(audio_data: bytes, background_tasks: BackgroundTasks):
    """Process voice input"""
    from backend.voice.processor import get_voice_processor
    
    voice = get_voice_processor()
    
    # Transcribe audio
    text = voice.transcribe(audio_data)
    
    if not text:
        raise HTTPException(status_code=400, detail="Could not transcribe audio")
    
    # Process text
    brain = get_brain()
    response = brain.process(text)
    
    # Speak response
    background_tasks.add_task(voice.speak, response)
    
    return {
        "transcribed": text,
        "response": response
    }


# ===== Memory Endpoints =====

@app.get("/api/memory")
async def get_memories(category: Optional[str] = None, limit: int = 20):
    """Get memories"""
    memory = get_memory_engine()
    return memory.recall(category=category, limit=limit)


@app.post("/api/memory")
async def add_memory(request: MemoryRequest):
    """Add a memory"""
    memory = get_memory_engine()
    memory_id = memory.remember(request.content, request.category, request.importance)
    return {"success": True, "memory_id": memory_id}


@app.get("/api/memory/stats")
async def get_memory_stats():
    """Get memory statistics"""
    memory = get_memory_engine()
    return memory.get_memory_stats()


@app.get("/api/memory/context")
async def get_context():
    """Get conversation context"""
    memory = get_memory_engine()
    return memory.get_context()


# ===== Project Endpoints =====

@app.get("/api/projects")
async def get_projects(status: Optional[str] = None):
    """Get all projects"""
    db = get_database()
    return db.get_projects(status)


@app.post("/api/projects")
async def create_project(request: ProjectRequest):
    """Create a new project"""
    db = get_database()
    project_id = db.create_project(request.name, request.description, request.status)
    return {"success": True, "project_id": project_id}


@app.patch("/api/projects/{project_id}")
async def update_project(project_id: int, updates: dict):
    """Update a project"""
    db = get_database()
    db.update_project(project_id, **updates)
    return {"success": True}


@app.get("/api/projects/{project_id}/tasks")
async def get_project_tasks(project_id: int):
    """Get tasks for a project"""
    db = get_database()
    return db.get_tasks(project_id=project_id)


# ===== Task Endpoints =====

@app.get("/api/tasks")
async def get_tasks(project_id: Optional[int] = None, completed: Optional[bool] = None):
    """Get tasks"""
    db = get_database()
    return db.get_tasks(project_id=project_id, completed=completed)


@app.post("/api/tasks")
async def create_task(request: TaskRequest):
    """Create a new task"""
    db = get_database()
    task_id = db.create_task(request.task, request.project_id, request.priority)
    return {"success": True, "task_id": task_id}


@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: int):
    """Mark task as completed"""
    db = get_database()
    db.complete_task(task_id)
    return {"success": True}


# ===== System Control Endpoints =====

@app.post("/api/system/open")
async def open_application(app_name: str):
    """Open an application"""
    controller = get_system_controller()
    success = controller.open_application(app_name)
    return {"success": success, "action": f"opened {app_name}"}


@app.post("/api/system/command")
async def execute_command(request: CommandRequest):
    """Execute a system command"""
    controller = get_system_controller()
    result = controller.execute_command(request.command)
    return result


@app.get("/api/system/info")
async def get_system_info():
    """Get system information"""
    controller = get_system_controller()
    return controller.get_system_info()


# ===== Vision Endpoints =====

@app.post("/api/vision/analyze")
async def analyze_image(image_data: bytes):
    """Analyze an image"""
    import cv2
    import numpy as np
    
    # Decode image
    nparr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image data")
    
    vision = get_vision_manager()
    results = vision.analyze_frame(frame)
    
    return results


@app.post("/api/vision/face/enroll")
async def enroll_face(user_id: int, name: str, image_data: bytes):
    """Enroll a new face"""
    import tempfile
    import cv2
    import numpy as np
    
    # Save image temporarily
    temp_path = tempfile.mktemp(suffix='.jpg')
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite(temp_path, img)
    
    vision = get_vision_manager()
    success = vision.add_user_face(user_id, name, temp_path)
    
    return {"success": success}


# ===== Logs Endpoints =====

@app.get("/api/logs")
async def get_logs(limit: int = 50):
    """Get activity logs"""
    db = get_database()
    return db.get_recent_logs(limit)


@app.get("/api/logs/audit")
async def get_audit_logs(limit: int = 100):
    """Get audit logs"""
    security = get_security_manager()
    return security.get_audit_log(limit)


# ===== Settings Endpoints =====

@app.get("/api/settings")
async def get_settings():
    """Get all settings"""
    db = get_database()
    
    # Get all settings from database
    settings = {}
    rows = db.fetch_all('SELECT key, value FROM settings')
    for key, value in rows:
        settings[key] = value
    
    return settings


@app.post("/api/settings")
async def update_setting(key: str, value: str):
    """Update a setting"""
    db = get_database()
    db.set_setting(key, value)
    return {"success": True}


# ===== Dashboard Stats =====

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    db = get_database()
    
    # Project stats
    projects = db.get_projects()
    active_projects = [p for p in projects if p['status'] == 'active']
    
    # Task stats
    all_tasks = db.get_tasks()
    pending_tasks = [t for t in all_tasks if not t['completed']]
    completed_tasks = [t for t in all_tasks if t['completed']]
    
    # Memory stats
    memory = get_memory_engine()
    memory_stats = memory.get_memory_stats()
    
    # System info
    controller = get_system_controller()
    system_info = controller.get_system_info()
    
    return {
        "projects": {
            "total": len(projects),
            "active": len(active_projects)
        },
        "tasks": {
            "total": len(all_tasks),
            "pending": len(pending_tasks),
            "completed": len(completed_tasks)
        },
        "memory": memory_stats,
        "system": system_info
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# Create app instance for uvicorn
def get_app():
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
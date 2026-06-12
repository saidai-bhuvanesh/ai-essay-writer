# STUDX JARVIS

> Local AI-Powered Personal Assistant

A comprehensive AI assistant system with voice interaction, memory, automation, browser control, computer vision, gesture control, face authentication, project management, and AI task execution.

## Features

- 🎤 **Voice Control** - Natural voice commands using Whisper STT
- 🧠 **AI Brain** - Local LLM reasoning with Ollama/Llama3
- 💾 **Memory Engine** - Long-term memory and user preferences
- 🔐 **Security** - Face recognition, permissions, audit logging
- 👁️ **Vision** - Object detection, gesture recognition
- ⚡ **Automation** - System control, browser automation
- 📊 **Dashboard** - React-based web interface
- 🤖 **Multi-Agent** - Specialized agents for different tasks

## Quick Start

### Backend Setup

```bash
cd AI-Jarvis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run the API server
python -m backend.api.main
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Ollama Setup (for LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3
ollama pull llama3

# Start Ollama server
ollama serve
```

## Architecture

```
STUDX JARVIS
├── backend/
│   ├── api/          # FastAPI REST endpoints
│   ├── voice/        # STT/TTS processing
│   ├── brain/        # LLM integration
│   ├── memory/       # Database & memory engine
│   ├── security/     # Authentication & permissions
│   ├── vision/       # Computer vision
│   ├── automation/   # System & browser control
│   └── agents/       # Multi-agent system
├── frontend/         # React dashboard
├── database/         # SQLite storage
├── logs/            # Activity logs
└── models/          # AI models
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Chat
- `POST /api/chat` - Chat with JARVIS
- `POST /api/chat/voice` - Voice input

### Memory
- `GET /api/memory` - Get memories
- `POST /api/memory` - Add memory
- `GET /api/memory/stats` - Memory statistics

### Projects & Tasks
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `POST /api/tasks/{id}/complete` - Complete task

### System
- `POST /api/system/open` - Open application
- `POST /api/system/command` - Execute command
- `GET /api/system/info` - System information

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/logs` - Activity logs

## Security

Three permission levels:
- **Level 1**: Open apps, search, read notes
- **Level 2**: Edit files, upload, draft emails
- **Level 3**: Delete files, terminal commands, system settings

Default credentials: `owner@jarvis.local` / `jarvis2024`

## Development Phases

1. ✅ Core Assistant - Basic commands
2. ✅ AI Brain - Llama3 integration
3. ✅ Voice Assistant - Whisper STT
4. ✅ Memory Engine - Long-term memory
5. 🔄 Browser Agent - Web automation
6. 📋 Vision System - Face & gesture
7. 📋 Multi-Agent System
8. 📋 React Dashboard
9. 📋 Personal Assistants
10. 📋 Secure OS Features

## License

MIT License - Bhuvi 2024
#!/bin/bash

# STUDX JARVIS Setup Script
# ==========================

set -e

echo "==================================="
echo "  STUDX JARVIS Setup"
echo "  v1.0 - Local AI Assistant"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
check_python() {
    echo -e "${YELLOW}Checking Python version...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        echo -e "${GREEN}Python $PYTHON_VERSION found${NC}"
    else
        echo -e "${RED}Python 3 not found. Please install Python 3.8+${NC}"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    if [ -d "venv" ]; then
        echo -e "${GREEN}Virtual environment already exists${NC}"
    else
        python3 -m venv venv
        echo -e "${GREEN}Virtual environment created${NC}"
    fi
}

# Activate virtual environment
activate_venv() {
    echo -e "\n${YELLOW}Activating virtual environment...${NC}"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo -e "${GREEN}Virtual environment activated${NC}"
    else
        echo -e "${RED}Virtual environment not found${NC}"
        exit 1
    fi
}

# Install Python dependencies
install_deps() {
    echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}Dependencies installed${NC}"
}

# Create environment file
setup_env() {
    echo -e "\n${YELLOW}Setting up environment file...${NC}"
    if [ -f ".env" ]; then
        echo -e "${GREEN}.env already exists${NC}"
    else
        cp .env.example .env
        echo -e "${GREEN}.env created from .env.example${NC}"
        echo -e "${YELLOW}Please edit .env with your settings${NC}"
    fi
}

# Create directories
setup_dirs() {
    echo -e "\n${YELLOW}Creating directories...${NC}"
    mkdir -p database logs models/whisper models/llama3 models/vision_models
    echo -e "${GREEN}Directories created${NC}"
}

# Setup frontend
setup_frontend() {
    echo -e "\n${YELLOW}Setting up frontend...${NC}"
    if [ -d "frontend" ]; then
        cd frontend
        if [ -f "package.json" ]; then
            npm install
            echo -e "${GREEN}Frontend dependencies installed${NC}"
        else
            echo -e "${YELLOW}Frontend package.json not found${NC}"
        fi
        cd ..
    fi
}

# Ollama setup check
check_ollama() {
    echo -e "\n${YELLOW}Checking Ollama...${NC}"
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}Ollama is installed${NC}"
        echo -e "${YELLOW}Make sure to pull the Llama3 model:${NC}"
        echo "  ollama pull llama3"
    else
        echo -e "${YELLOW}Ollama not found. Install from: https://ollama.com${NC}"
    fi
}

# Main setup
main() {
    check_python
    create_venv
    activate_venv
    install_deps
    setup_env
    setup_dirs
    setup_frontend
    check_ollama

    echo -e "\n==================================="
    echo -e "${GREEN}Setup complete!${NC}"
    echo "==================================="
    echo ""
    echo "To start JARVIS:"
    echo "  1. Activate venv: source venv/bin/activate"
    echo "  2. Start API: python -m backend.api.main"
    echo "  3. Start frontend: cd frontend && npm run dev"
    echo ""
    echo "Or use the combined command:"
    echo "  source venv/bin/activate && python -m backend.api.main"
    echo ""
}

main "$@"
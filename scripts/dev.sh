#!/bin/bash
# =============================================================================
# Morado Development Environment Startup Script
# =============================================================================
# This script starts the development environment for Morado.
# It can start frontend, backend, or both services.
#
# Usage: ./scripts/dev.sh [options]
#   Options:
#     --backend         Start only the backend
#     --frontend        Start only the frontend
#     --docker          Use Docker Compose for development
#     --help            Show this help message
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default options
START_BACKEND=true
START_FRONTEND=true
USE_DOCKER=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            START_FRONTEND=false
            shift
            ;;
        --frontend)
            START_BACKEND=false
            shift
            ;;
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --help)
            echo "Usage: ./scripts/dev.sh [options]"
            echo "Options:"
            echo "  --backend         Start only the backend"
            echo "  --frontend        Start only the frontend"
            echo "  --docker          Use Docker Compose for development"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Print banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              Morado Development Environment                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Stop Docker if used
    if $USE_DOCKER; then
        docker-compose -f "$PROJECT_ROOT/deployment/docker-compose.dev.yml" down 2>/dev/null || true
    fi
    
    echo -e "${GREEN}Services stopped.${NC}"
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Docker mode
if $USE_DOCKER; then
    echo -e "${BLUE}Starting development environment with Docker...${NC}"
    
    if ! command_exists docker-compose && ! command_exists docker; then
        echo -e "${RED}Docker is required but not installed${NC}"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    # Use docker compose (v2) or docker-compose (v1)
    if command_exists docker && docker compose version >/dev/null 2>&1; then
        docker compose -f deployment/docker-compose.dev.yml up
    else
        docker-compose -f deployment/docker-compose.dev.yml up
    fi
    
    exit 0
fi

# Local development mode
echo -e "${BLUE}Starting local development environment...${NC}"

# Check for uv or pip
if command_exists uv; then
    USE_UV=true
else
    USE_UV=false
fi

# Check for bun or npm
if command_exists bun; then
    USE_BUN=true
else
    USE_BUN=false
fi

# Start Backend
if $START_BACKEND; then
    echo -e "\n${BLUE}Starting backend server...${NC}"
    cd "$PROJECT_ROOT"
    
    # Set environment variables
    export PYTHONPATH="$PROJECT_ROOT/backend/src"
    export APP_ENV=development
    
    if $USE_UV; then
        echo -e "${GREEN}Backend starting at http://localhost:8000${NC}"
        uv run uvicorn morado.app:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
    else
        # Activate virtual environment if it exists
        if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
            source "$PROJECT_ROOT/.venv/bin/activate"
        fi
        echo -e "${GREEN}Backend starting at http://localhost:8000${NC}"
        uvicorn morado.app:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
    fi
    
    # Wait for backend to start
    sleep 2
fi

# Start Frontend
if $START_FRONTEND; then
    echo -e "\n${BLUE}Starting frontend server...${NC}"
    cd "$PROJECT_ROOT/frontend"
    
    if $USE_BUN; then
        echo -e "${GREEN}Frontend starting at http://localhost:5173${NC}"
        bun run dev &
        FRONTEND_PID=$!
    else
        echo -e "${GREEN}Frontend starting at http://localhost:5173${NC}"
        npm run dev &
        FRONTEND_PID=$!
    fi
fi

# Print status
echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              Development servers are running!                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if $START_BACKEND; then
    echo -e "  Backend:  ${BLUE}http://localhost:8000${NC}"
    echo -e "  API Docs: ${BLUE}http://localhost:8000/docs${NC}"
fi

if $START_FRONTEND; then
    echo -e "  Frontend: ${BLUE}http://localhost:5173${NC}"
fi

echo -e "\nPress ${YELLOW}Ctrl+C${NC} to stop all services."

# Wait for processes
wait

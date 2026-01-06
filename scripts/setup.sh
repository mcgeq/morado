#!/bin/bash
# =============================================================================
# Morado Project Setup Script
# =============================================================================
# This script initializes the Morado project for development.
# It sets up both frontend and backend environments.
#
# Usage: ./scripts/setup.sh [options]
#   Options:
#     --backend-only    Setup only the backend
#     --frontend-only   Setup only the frontend
#     --skip-db         Skip database initialization
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
SETUP_BACKEND=true
SETUP_FRONTEND=true
SKIP_DB=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            SETUP_FRONTEND=false
            shift
            ;;
        --frontend-only)
            SETUP_BACKEND=false
            shift
            ;;
        --skip-db)
            SKIP_DB=true
            shift
            ;;
        --help)
            echo "Usage: ./scripts/setup.sh [options]"
            echo "Options:"
            echo "  --backend-only    Setup only the backend"
            echo "  --frontend-only   Setup only the frontend"
            echo "  --skip-db         Skip database initialization"
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
echo "║                    Morado Project Setup                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Check prerequisites
echo -e "\n${BLUE}Checking prerequisites...${NC}"

if $SETUP_BACKEND; then
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python found: $PYTHON_VERSION"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi

    if command_exists uv; then
        print_status "uv package manager found"
        USE_UV=true
    else
        print_warning "uv not found, will use pip"
        USE_UV=false
    fi
fi

if $SETUP_FRONTEND; then
    if command_exists bun; then
        BUN_VERSION=$(bun --version 2>&1)
        print_status "Bun found: $BUN_VERSION"
        USE_BUN=true
    elif command_exists npm; then
        NPM_VERSION=$(npm --version 2>&1)
        print_warning "Bun not found, using npm: $NPM_VERSION"
        USE_BUN=false
    else
        print_error "Bun or npm is required but not installed"
        exit 1
    fi
fi

# Setup Backend
if $SETUP_BACKEND; then
    echo -e "\n${BLUE}Setting up backend...${NC}"
    cd "$PROJECT_ROOT"

    # Create virtual environment and install dependencies
    if $USE_UV; then
        print_info "Installing backend dependencies with uv..."
        uv sync
        print_status "Backend dependencies installed"
    else
        print_info "Creating virtual environment..."
        python3 -m venv .venv
        source .venv/bin/activate
        print_info "Installing backend dependencies with pip..."
        pip install -e ".[dev,test]"
        print_status "Backend dependencies installed"
    fi

    # Setup database
    if ! $SKIP_DB; then
        print_info "Checking database configuration..."
        
        # Check if PostgreSQL is available
        if command_exists psql; then
            print_status "PostgreSQL client found"
        else
            print_warning "PostgreSQL client not found. Make sure database is accessible."
        fi

        # Run database migrations
        print_info "Running database migrations..."
        if $USE_UV; then
            uv run alembic -c backend/alembic.ini upgrade head 2>/dev/null || print_warning "Database migration skipped (database may not be running)"
        else
            alembic -c backend/alembic.ini upgrade head 2>/dev/null || print_warning "Database migration skipped (database may not be running)"
        fi
    fi

    print_status "Backend setup complete"
fi

# Setup Frontend
if $SETUP_FRONTEND; then
    echo -e "\n${BLUE}Setting up frontend...${NC}"
    cd "$PROJECT_ROOT/frontend"

    # Install dependencies
    if $USE_BUN; then
        print_info "Installing frontend dependencies with bun..."
        bun install
    else
        print_info "Installing frontend dependencies with npm..."
        npm install
    fi

    print_status "Frontend setup complete"
fi

# Create environment files if they don't exist
echo -e "\n${BLUE}Checking environment files...${NC}"

if [ ! -f "$PROJECT_ROOT/backend/config/development.toml" ]; then
    print_warning "Backend development config not found. Please configure backend/config/development.toml"
fi

if [ ! -f "$PROJECT_ROOT/frontend/.env.development" ]; then
    print_warning "Frontend development env not found. Please configure frontend/.env.development"
fi

# Print completion message
echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "Next steps:"
echo -e "  1. Configure your database connection in backend/config/development.toml"
echo -e "  2. Start the development environment: ${BLUE}./scripts/dev.sh${NC}"
echo -e "  3. Or use Docker: ${BLUE}docker-compose -f deployment/docker-compose.dev.yml up${NC}"
echo ""

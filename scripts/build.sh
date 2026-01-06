#!/bin/bash
# =============================================================================
# Morado Build Script
# =============================================================================
# This script builds the Morado project for production deployment.
# It can build Docker images, frontend assets, or both.
#
# Usage: ./scripts/build.sh [options]
#   Options:
#     --backend         Build only the backend
#     --frontend        Build only the frontend
#     --docker          Build Docker images
#     --push            Push Docker images to registry
#     --tag TAG         Docker image tag (default: latest)
#     --registry REG    Docker registry (default: none)
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
BUILD_BACKEND=true
BUILD_FRONTEND=true
BUILD_DOCKER=false
PUSH_IMAGES=false
IMAGE_TAG="latest"
REGISTRY=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            BUILD_FRONTEND=false
            shift
            ;;
        --frontend)
            BUILD_BACKEND=false
            shift
            ;;
        --docker)
            BUILD_DOCKER=true
            shift
            ;;
        --push)
            PUSH_IMAGES=true
            shift
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --registry)
            REGISTRY="$2/"
            shift 2
            ;;
        --help)
            echo "Usage: ./scripts/build.sh [options]"
            echo "Options:"
            echo "  --backend         Build only the backend"
            echo "  --frontend        Build only the frontend"
            echo "  --docker          Build Docker images"
            echo "  --push            Push Docker images to registry"
            echo "  --tag TAG         Docker image tag (default: latest)"
            echo "  --registry REG    Docker registry (default: none)"
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
echo "║                    Morado Build Script                        ║"
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

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Build Docker images
if $BUILD_DOCKER; then
    echo -e "\n${BLUE}Building Docker images...${NC}"
    
    if ! command_exists docker; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    # Build backend image
    if $BUILD_BACKEND; then
        print_info "Building backend Docker image..."
        docker build \
            -f deployment/docker/Dockerfile.backend \
            -t "${REGISTRY}morado-backend:${IMAGE_TAG}" \
            .
        print_status "Backend image built: ${REGISTRY}morado-backend:${IMAGE_TAG}"
    fi
    
    # Build frontend image
    if $BUILD_FRONTEND; then
        print_info "Building frontend Docker image..."
        docker build \
            -f deployment/docker/Dockerfile.frontend \
            -t "${REGISTRY}morado-frontend:${IMAGE_TAG}" \
            .
        print_status "Frontend image built: ${REGISTRY}morado-frontend:${IMAGE_TAG}"
    fi
    
    # Push images if requested
    if $PUSH_IMAGES; then
        echo -e "\n${BLUE}Pushing Docker images...${NC}"
        
        if $BUILD_BACKEND; then
            print_info "Pushing backend image..."
            docker push "${REGISTRY}morado-backend:${IMAGE_TAG}"
            print_status "Backend image pushed"
        fi
        
        if $BUILD_FRONTEND; then
            print_info "Pushing frontend image..."
            docker push "${REGISTRY}morado-frontend:${IMAGE_TAG}"
            print_status "Frontend image pushed"
        fi
    fi
    
    echo -e "\n${GREEN}Docker build complete!${NC}"
    exit 0
fi

# Local build (non-Docker)
echo -e "${BLUE}Building for production...${NC}"

# Build Frontend
if $BUILD_FRONTEND; then
    echo -e "\n${BLUE}Building frontend...${NC}"
    cd "$PROJECT_ROOT/frontend"
    
    # Check for bun or npm
    if command_exists bun; then
        print_info "Installing dependencies with bun..."
        bun install --frozen-lockfile
        
        print_info "Building frontend with bun..."
        bun run build
    elif command_exists npm; then
        print_info "Installing dependencies with npm..."
        npm ci
        
        print_info "Building frontend with npm..."
        npm run build
    else
        print_error "Bun or npm is required but not installed"
        exit 1
    fi
    
    # Check if build was successful
    if [ -d "dist" ]; then
        print_status "Frontend build complete: frontend/dist/"
        
        # Print build size
        BUILD_SIZE=$(du -sh dist | cut -f1)
        print_info "Build size: $BUILD_SIZE"
    else
        print_error "Frontend build failed - dist directory not found"
        exit 1
    fi
fi

# Build Backend (mainly for validation)
if $BUILD_BACKEND; then
    echo -e "\n${BLUE}Validating backend...${NC}"
    cd "$PROJECT_ROOT"
    
    # Check for uv or pip
    if command_exists uv; then
        print_info "Checking backend dependencies with uv..."
        uv sync --frozen
        
        print_info "Running type checks..."
        uv run ty check backend/src/morado || print_info "Type check completed with warnings"
        
        print_info "Running linter..."
        uv run ruff check backend/src/morado || print_info "Lint check completed with warnings"
    else
        print_info "Checking backend dependencies with pip..."
        pip install -e . --quiet
        
        if command_exists ty; then
            print_info "Running type checks..."
            ty check backend/src/morado || print_info "Type check completed with warnings"
        fi
        
        if command_exists ruff; then
            print_info "Running linter..."
            ruff check backend/src/morado || print_info "Lint check completed with warnings"
        fi
    fi
    
    print_status "Backend validation complete"
fi

# Print completion message
echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    Build Complete!                            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if $BUILD_FRONTEND; then
    echo -e "Frontend build output: ${BLUE}frontend/dist/${NC}"
fi

echo -e "\nTo build Docker images, run: ${BLUE}./scripts/build.sh --docker${NC}"
echo -e "To push to registry, run: ${BLUE}./scripts/build.sh --docker --push --registry your-registry.com${NC}"

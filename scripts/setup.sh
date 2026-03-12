#!/bin/bash
# Automated Setup Script for VidyaMitra Career Agent

set -euo pipefail

echo "🚀 VidyaMitra Career Agent - Automated Setup"
echo "=============================================="

# Check prerequisites
check_prereqs() {
    echo "Checking prerequisites..."
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is required but not installed."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Root dependencies setup
setup_root() {
    echo "1. Installing root dependencies..."
    npm install
    echo "✅ Root dependencies installed (concurrently)"
}

# Backend setup
setup_backend() {
    echo "2. Setting up backend..."
    cd backend
    
    if [ ! -d ".venv" ]; then
        if command -v uv &> /dev/null; then
            uv venv .venv
        else
            python3 -m venv .venv
        fi
    fi
    
    source .venv/bin/activate
    if command -v uv &> /dev/null; then
        uv pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "⚠️  Please add your OpenAI API key to backend/.env"
    fi
    
    cd ..
}

# Frontend setup
setup_frontend() {
    echo "3. Setting up frontend..."
    cd frontend
    npm install
    cd ..
}

# Main execution
main() {
    check_prereqs
    setup_root
    setup_backend
    setup_frontend
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Add your OpenAI API key to backend/.env"
    echo "2. Run: npm run dev"
    echo "3. Open http://localhost:3000"
}

main "$@"
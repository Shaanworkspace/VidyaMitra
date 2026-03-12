#!/bin/bash

# Environment Validation Script for VidyaMitra Career Agent

echo "🔍 Validating environment configuration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track validation status
VALIDATION_FAILED=false

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check environment file and variables
check_env_file() {
    local env_file="$1"
    local description="$2"
    
    echo -e "\n${BLUE}📁 Checking $description${NC}"
    
    if [ -f "$env_file" ]; then
        echo -e "${GREEN}✅ $env_file exists${NC}"
        
        # Check for required variables
        if [ "$env_file" = "backend/.env" ]; then
            echo "   Checking required backend environment variables..."
            
            # Check OPENAI_API_KEY
            if grep -q "^OPENAI_API_KEY=" "$env_file" && ! grep -q "^OPENAI_API_KEY=your_openai_api_key_here" "$env_file"; then
                echo -e "   ${GREEN}✅ OPENAI_API_KEY is configured${NC}"
            else
                echo -e "   ${RED}❌ OPENAI_API_KEY is not configured${NC}"
                echo -e "   ${YELLOW}💡 Please add your OpenAI API key to $env_file${NC}"
                VALIDATION_FAILED=true
            fi
            
            # Check other recommended variables
            for var in "MODEL_NAME" "FRONTEND_URL" "API_HOST" "API_PORT"; do
                if grep -q "^$var=" "$env_file"; then
                    echo -e "   ${GREEN}✅ $var is configured${NC}"
                else
                    echo -e "   ${YELLOW}⚠️  $var is not configured (using defaults)${NC}"
                fi
            done
        fi
    else
        echo -e "${YELLOW}⚠️  $env_file not found${NC}"
        echo -e "   ${BLUE}💡 Copy from ${env_file}.example and configure${NC}"
        VALIDATION_FAILED=true
    fi
}

# Function to check system dependencies
check_system_deps() {
    echo -e "\n${BLUE}🔧 Checking system dependencies${NC}"
    
    # Check Python
    if command_exists python3; then
        python_version=$(python3 --version | cut -d ' ' -f 2)
        echo -e "${GREEN}✅ Python 3 installed: $python_version${NC}"
        
        # Check if version is 3.11+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
            echo -e "   ${GREEN}✅ Python version is 3.11+ (recommended)${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Python 3.11+ recommended for best compatibility${NC}"
        fi
    else
        echo -e "${RED}❌ Python 3 not found${NC}"
        VALIDATION_FAILED=true
    fi
    
    # Check Node.js
    if command_exists node; then
        node_version=$(node --version)
        echo -e "${GREEN}✅ Node.js installed: $node_version${NC}"
    else
        echo -e "${RED}❌ Node.js not found${NC}"
        VALIDATION_FAILED=true
    fi
    
    # Check npm
    if command_exists npm; then
        npm_version=$(npm --version)
        echo -e "${GREEN}✅ npm installed: $npm_version${NC}"
    else
        echo -e "${RED}❌ npm not found${NC}"
        VALIDATION_FAILED=true
    fi
}

# Function to check virtual environment
check_venv() {
    echo -e "\n${BLUE}🐍 Checking Python virtual environment${NC}"
    
    if [ -d "backend/.venv" ]; then
        echo -e "${GREEN}✅ Virtual environment exists${NC}"
        
        # Check if virtual environment has required packages
        if [ -f "backend/.venv/lib/python*/site-packages/fastapi/__init__.py" ] || [ -f "backend/.venv/lib/python3.*/site-packages/fastapi/__init__.py" ]; then
            echo -e "${GREEN}✅ FastAPI installed in virtual environment${NC}"
        else
            echo -e "${YELLOW}⚠️  Dependencies may not be installed${NC}"
            echo -e "   ${BLUE}💡 Run: npm run setup${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
        echo -e "   ${BLUE}💡 Run: npm run setup${NC}"
        VALIDATION_FAILED=true
    fi
}

# Function to check frontend dependencies
check_frontend_deps() {
    echo -e "\n${BLUE}⚛️  Checking frontend dependencies${NC}"
    
    if [ -d "frontend/node_modules" ]; then
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend dependencies not installed${NC}"
        echo -e "   ${BLUE}💡 Run: npm run setup${NC}"
        VALIDATION_FAILED=true
    fi
}

# Main validation
echo -e "${BLUE}🎯 VidyaMitra Career Agent - Environment Validation${NC}"
echo "============================================================"

check_system_deps
check_venv
check_frontend_deps
check_env_file "backend/.env" "Backend environment file"

# Summary
echo -e "\n${BLUE}📋 Validation Summary${NC}"
echo "============================================================"

if [ "$VALIDATION_FAILED" = true ]; then
    echo -e "${RED}❌ Environment validation failed${NC}"
    echo -e "${YELLOW}Please address the issues above before running the application${NC}"
    echo -e "\n${BLUE}🚀 Quick setup command: npm run setup${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Environment validation passed${NC}"
    echo -e "${GREEN}🎉 Your environment is ready to run VidyaMitra Career Agent${NC}"
    echo -e "\n${BLUE}🚀 Start development: npm run dev${NC}"
    exit 0
fi
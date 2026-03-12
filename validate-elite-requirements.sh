#!/bin/bash

# Elite Certification Validation Script for VidyaMitra Career Agent
# This script checks if the project meets ReadyTensor Elite certification requirements

echo "🎯 VidyaMitra Career Agent - Elite Certification Validation"
echo "=============================================================="
echo

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
total_checks=0
passed_checks=0

check_item() {
    local description="$1"
    local command="$2"
    local required="$3" # true/false
    
    total_checks=$((total_checks + 1))
    echo -n "Checking: $description... "
    
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        passed_checks=$((passed_checks + 1))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗ FAIL (Required)${NC}"
        else
            echo -e "${YELLOW}! OPTIONAL${NC}"
        fi
        return 1
    fi
}

echo -e "${BLUE}1. PROJECT STRUCTURE${NC}"
echo "---------------------"

check_item "README.md exists and is comprehensive" "test -f README.md && test \$(wc -l < README.md) -gt 400" true
check_item "Package configuration files exist" "test -f package.json && test -f pyproject.toml && test -f setup.py" true
check_item "Requirements and dependencies defined" "test -f requirements.txt && test -f requirements-lock.txt" true
check_item "Proper directory structure" "test -d backend && test -d frontend && test -d notebooks && test -d docs" true
check_item "Docker support available" "test -f Dockerfile && test -f docker-compose.yml" true

echo
echo -e "${BLUE}2. DOCUMENTATION${NC}"
echo "----------------"

check_item "CHANGELOG.md exists" "test -f CHANGELOG.md" true
check_item "LICENSE file exists" "test -f LICENSE" true
check_item "Architecture documentation" "test -f docs/ARCHITECTURE.md" false
check_item "API documentation references" "grep -q 'API documentation' README.md" true
check_item "Installation instructions" "grep -q 'Installation' README.md" true

echo
echo -e "${BLUE}3. CODE QUALITY${NC}"
echo "---------------"

check_item "Custom exception handling" "test -f backend/app/exceptions.py" true
check_item "Comprehensive logging setup" "test -f backend/app/logging_config.py" true
check_item "Monitoring and metrics" "test -f backend/app/monitoring.py" true
check_item "Type hints and validation" "grep -q 'from typing import' backend/app/main.py" true
check_item "Configuration management" "test -f backend/app/config.py" true

echo
echo -e "${BLUE}4. TESTING INFRASTRUCTURE${NC}"
echo "-------------------------"

check_item "Test configuration exists" "test -f backend/pytest.ini" true
check_item "Unit tests present" "test -f backend/tests/test_analysis.py" true
check_item "Integration tests present" "test -f backend/tests/test_integration.py" true
check_item "Performance tests present" "test -f backend/tests/test_performance.py" true
check_item "Frontend tests present" "test -f frontend/src/__tests__/AnalysisForm.test.tsx" true

echo
echo -e "${BLUE}5. NOTEBOOKS AND TUTORIALS${NC}"
echo "---------------------------"

check_item "Educational notebooks exist" "test \$(find notebooks/ -name '*.ipynb' | wc -l) -ge 3" true
check_item "Notebook size optimization" "find notebooks/ -name '*.ipynb' -exec wc -l {} + | tail -1 | awk '{if(\$1 < 2000) exit 0; else exit 1}'" true
check_item "Sample data provided" "test -f data/sample_resume.txt && test -f data/sample_job_description.txt" true

echo
echo -e "${BLUE}6. DEPLOYMENT AND OPERATIONS${NC}"
echo "-----------------------------"

check_item "Docker multi-stage build" "grep -q 'FROM.*as.*builder' Dockerfile" true
check_item "Docker security (non-root user)" "grep -q 'USER.*vidyamitra' Dockerfile" true
check_item "Health checks configured" "grep -q 'HEALTHCHECK' Dockerfile" true
check_item "Environment variable management" "grep -q 'OPENAI_API_KEY' docker-compose.yml" true
check_item "Production logging setup" "test -d backend/app-logs" true

echo
echo -e "${BLUE}7. DEVELOPMENT WORKFLOW${NC}"
echo "-----------------------"

check_item "Setup scripts available" "test -f scripts/setup.sh" true
check_item "Validation scripts available" "test -f scripts/validate-env.sh" true
check_item "Package.json scripts comprehensive" "grep -q '\"test\"' package.json && grep -q '\"lint\"' package.json" true
check_item "Development documentation" "grep -q 'Development' README.md" true

echo
echo -e "${BLUE}8. ADVANCED FEATURES${NC}"
echo "--------------------"

check_item "Advanced error handling system" "grep -q 'VidyaMitraError' backend/app/exceptions.py" true
check_item "Performance monitoring" "grep -q 'PerformanceMonitor' backend/app/monitoring.py" true
check_item "Comprehensive configuration" "wc -l backend/app/config.py | awk '{if(\$1 > 50) exit 0; else exit 1}'" true
check_item "Production-ready logging" "grep -q 'RotatingFileHandler' backend/app/logging_config.py" true

echo
echo "=============================================================="
echo -e "${BLUE}VALIDATION SUMMARY${NC}"
echo "=============================================================="

# Calculate percentage
percentage=$((passed_checks * 100 / total_checks))

echo "Total checks: $total_checks"
echo "Passed checks: $passed_checks"
echo "Success rate: $percentage%"
echo

if [ $percentage -ge 95 ]; then
    echo -e "${GREEN}🏆 ELITE CERTIFICATION READY!${NC}"
    echo -e "${GREEN}Your project meets the requirements for ReadyTensor Elite certification.${NC}"
    exit 0
elif [ $percentage -ge 85 ]; then
    echo -e "${YELLOW}⚠️  PROFESSIONAL LEVEL${NC}"
    echo -e "${YELLOW}Your project meets Professional requirements. A few more items needed for Elite.${NC}"
    exit 1
elif [ $percentage -ge 70 ]; then
    echo -e "${YELLOW}📝 ESSENTIAL LEVEL${NC}"
    echo -e "${YELLOW}Your project meets Essential requirements. More work needed for Elite.${NC}"
    exit 2
else
    echo -e "${RED}❌ NEEDS IMPROVEMENT${NC}"
    echo -e "${RED}Your project needs significant work to reach Elite certification.${NC}"
    exit 3
fi
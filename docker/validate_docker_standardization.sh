#!/bin/bash
# FLEXT Docker Standardization Validation Script
# Version: 1.0.0
# Purpose: Validate that all Docker artifacts are properly centralized

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  FLEXT DOCKER STANDARDIZATION VALIDATION                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# CHECK 1: No docker-compose files outside central location
# ============================================================================
echo -e "${BLUE}[1/8]${NC} Checking for duplicate docker-compose files..."
DUPLICATE_COMPOSE=$(find ~/flext -name "docker-compose*.yml" ! -path "*/docker/*" ! -name "*.bak" 2>/dev/null | wc -l)

if [ "$DUPLICATE_COMPOSE" -gt 0 ]; then
	echo -e "${RED}❌ FAILED${NC}: Found $DUPLICATE_COMPOSE docker-compose files outside central location:"
	find ~/flext -name "docker-compose*.yml" ! -path "*/docker/*" ! -name "*.bak" 2>/dev/null | head -5
	((ERRORS++))
else
	echo -e "${GREEN}✅ PASSED${NC}: No duplicate docker-compose files found"
fi
echo ""

# ============================================================================
# CHECK 2: No Dockerfiles outside images/ directory
# ============================================================================
echo -e "${BLUE}[2/8]${NC} Checking for Dockerfiles outside images/ directory..."
DUPLICATE_DOCKERFILES=$(find ~/flext -name "Dockerfile*" -type f ! -path "*/docker/images/*" ! -name "*.bak" ! -path "*/__pycache__/*" 2>/dev/null | wc -l)

if [ "$DUPLICATE_DOCKERFILES" -gt 0 ]; then
	echo -e "${RED}❌ FAILED${NC}: Found $DUPLICATE_DOCKERFILES Dockerfiles outside images/ directory:"
	find ~/flext -name "Dockerfile*" -type f ! -path "*/docker/images/*" ! -name "*.bak" ! -path "*/__pycache__/*" 2>/dev/null | head -5
	((ERRORS++))
else
	echo -e "${GREEN}✅ PASSED${NC}: No duplicate Dockerfiles found"
fi
echo ""

# ============================================================================
# CHECK 3: No local docker_fixtures.py files
# ============================================================================
echo -e "${BLUE}[3/8]${NC} Checking for duplicate docker_fixtures.py files..."
DUPLICATE_FIXTURES=$(find ~/flext -name "docker_fixtures.py" ! -path "*/flext-core/src/flext_tests/fixtures/*" ! -name "*.bak" 2>/dev/null | wc -l)

if [ "$DUPLICATE_FIXTURES" -gt 0 ]; then
	echo -e "${YELLOW}⚠️  WARNING${NC}: Found $DUPLICATE_FIXTURES local docker_fixtures.py files:"
	find ~/flext -name "docker_fixtures.py" ! -path "*/flext-core/src/flext_tests/fixtures/*" ! -name "*.bak" 2>/dev/null | head -5
	echo -e "    ${YELLOW}These should be using flext_tests.fixtures instead${NC}"
	((WARNINGS++))
else
	echo -e "${GREEN}✅ PASSED${NC}: No duplicate docker fixtures found"
fi
echo ""

# ============================================================================
# CHECK 4: Verify centralized compose files count
# ============================================================================
echo -e "${BLUE}[4/8]${NC} Verifying centralized docker-compose files..."
COMPOSE_COUNT=$(ls ~/flext/docker/docker-compose*.yml 2>/dev/null | wc -l)

if [ "$COMPOSE_COUNT" -lt 15 ]; then
	echo -e "${RED}❌ FAILED${NC}: Expected at least 15 compose files, found $COMPOSE_COUNT"
	((ERRORS++))
else
	echo -e "${GREEN}✅ PASSED${NC}: Found $COMPOSE_COUNT centralized docker-compose files"
fi
echo ""

# ============================================================================
# CHECK 5: Verify centralized Dockerfiles count
# ============================================================================
echo -e "${BLUE}[5/8]${NC} Verifying centralized Dockerfiles..."
DOCKERFILE_COUNT=$(ls ~/flext/docker/images/Dockerfile.* 2>/dev/null | wc -l)

if [ "$DOCKERFILE_COUNT" -lt 20 ]; then
	echo -e "${RED}❌ FAILED${NC}: Expected at least 20 Dockerfiles, found $DOCKERFILE_COUNT"
	((ERRORS++))
else
	echo -e "${GREEN}✅ PASSED${NC}: Found $DOCKERFILE_COUNT centralized Dockerfiles"
fi
echo ""

# ============================================================================
# CHECK 6: Verify FlextTestDocker availability
# ============================================================================
echo -e "${BLUE}[6/8]${NC} Verifying FlextTestDocker availability..."
if python3 -c "from flext_tests import FlextTestDocker; print('OK')" 2>/dev/null | grep -q "OK"; then
	echo -e "${GREEN}✅ PASSED${NC}: FlextTestDocker is importable"
else
	echo -e "${RED}❌ FAILED${NC}: Cannot import FlextTestDocker from flext_tests"
	((ERRORS++))
fi
echo ""

# ============================================================================
# CHECK 7: Verify centralized fixtures availability
# ============================================================================
echo -e "${BLUE}[7/8]${NC} Verifying centralized fixtures availability..."
if python3 -c "from flext_tests.fixtures import flext_docker, client-a_oud_container, ldap_container, oracle_container, postgres_container, redis_container; print('OK')" 2>/dev/null | grep -q "OK"; then
	echo -e "${GREEN}✅ PASSED${NC}: Centralized fixtures are importable (including client-a_oud_container)"
else
	echo -e "${YELLOW}⚠️  WARNING${NC}: Some centralized fixtures may not be available"
	((WARNINGS++))
fi
echo ""

# ============================================================================
# CHECK 8: Check for prohibited Docker script patterns
# ============================================================================
echo -e "${BLUE}[8/8]${NC} Checking for prohibited Docker script patterns..."
DOCKER_SCRIPTS=$(find ~/flext -name "*docker*.sh" ! -path "*/docker/*" ! -name "*.bak" 2>/dev/null | wc -l)

if [ "$DOCKER_SCRIPTS" -gt 0 ]; then
	echo -e "${YELLOW}⚠️  WARNING${NC}: Found $DOCKER_SCRIPTS Docker-related shell scripts:"
	find ~/flext -name "*docker*.sh" ! -path "*/docker/*" ! -name "*.bak" 2>/dev/null | head -5
	echo -e "    ${YELLOW}Consider using FlextTestDocker API instead${NC}"
	((WARNINGS++))
else
	echo -e "${GREEN}✅ PASSED${NC}: No prohibited Docker scripts found"
fi
echo ""

# ============================================================================
# CHECK 9: Check for deprecated parallel_docker usage
# ============================================================================
echo -e "${BLUE}[9/9]${NC} Checking for deprecated parallel_docker usage..."
PARALLEL_DOCKER_USAGE=$(find ~/flext -name "*.py" -type f ! -name "*.bak" -exec grep -l "from flext_tests.parallel_docker\|import.*parallel_docker" {} \; 2>/dev/null | wc -l)

if [ "$PARALLEL_DOCKER_USAGE" -gt 0 ]; then
	echo -e "${YELLOW}⚠️  WARNING${NC}: Found $PARALLEL_DOCKER_USAGE files using deprecated parallel_docker:"
	find ~/flext -name "*.py" -type f ! -name "*.bak" -exec grep -l "from flext_tests.parallel_docker\|import.*parallel_docker" {} \; 2>/dev/null | head -5
	echo -e "    ${YELLOW}Migrate to centralized fixtures from flext_tests.fixtures${NC}"
	echo -e "    ${YELLOW}Use: client-a_oud_container, ldap_container, oracle_container${NC}"
	((WARNINGS++))
else
	echo -e "${GREEN}✅ PASSED${NC}: No deprecated parallel_docker usage found"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  VALIDATION SUMMARY                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
	echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
	echo -e "   Docker standardization is properly implemented"
	exit 0
elif [ "$ERRORS" -eq 0 ]; then
	echo -e "${YELLOW}⚠️  PASSED WITH WARNINGS${NC}"
	echo -e "   Errors: $ERRORS"
	echo -e "   Warnings: $WARNINGS"
	echo -e "   ${YELLOW}Please review warnings above${NC}"
	exit 0
else
	echo -e "${RED}❌ VALIDATION FAILED${NC}"
	echo -e "   Errors: $ERRORS"
	echo -e "   Warnings: $WARNINGS"
	echo -e "   ${RED}Please fix errors above before proceeding${NC}"
	exit 1
fi

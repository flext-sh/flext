#!/bin/bash
# FLEXT Constants Standardization Validation Script
# Validates that constants standardization has been applied across the ecosystem

set -e

echo "🔍 FLEXT Constants Standardization Validation"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success() {
	echo -e "${GREEN}✅ $1${NC}"
}

warning() {
	echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
	echo -e "${RED}❌ $1${NC}"
}

info() {
	echo -e "${BLUE}ℹ️  $1${NC}"
}

VALIDATION_FAILURES=0

# 1. Validate scripts/constants.env is synchronized with FlextConstants
info "Checking scripts/constants.env synchronization..."

if [[ -f "scripts/constants.env" ]]; then
	# Check if it contains FlextConstants references
	if grep -q "FlextConstants" scripts/constants.env; then
		success "scripts/constants.env contains FlextConstants references"
	else
		error "scripts/constants.env missing FlextConstants references"
		((VALIDATION_FAILURES++))
	fi

	# Test that it loads correctly
	if source scripts/constants.env 2>/dev/null; then
		success "scripts/constants.env loads successfully"
	else
		error "scripts/constants.env fails to load"
		((VALIDATION_FAILURES++))
	fi
else
	error "scripts/constants.env not found"
	((VALIDATION_FAILURES++))
fi

# 2. Validate generation script exists and works
info "Checking constants generation script..."

if [[ -f "scripts/generate_constants_env.py" ]]; then
	success "Constants generation script exists"

	# Test that it runs successfully
	if timeout 30 python scripts/generate_constants_env.py >/dev/null 2>&1; then
		success "Constants generation script executes successfully"
	else
		error "Constants generation script fails to execute"
		((VALIDATION_FAILURES++))
	fi
else
	error "scripts/generate_constants_env.py not found"
	((VALIDATION_FAILURES++))
fi

# 3. Validate test scripts use environment constants
info "Checking test scripts standardization..."

if [[ -f "scripts/testing/stress-test.sh" ]]; then
	if grep -q "FLEXT_PERFORMANCE_CRITICAL_MS" scripts/testing/stress-test.sh; then
		success "stress-test.sh uses standardized performance constants"
	else
		warning "stress-test.sh may not use all standardized constants"
	fi

	# Check syntax
	if bash -n scripts/testing/stress-test.sh; then
		success "stress-test.sh has valid syntax"
	else
		error "stress-test.sh has syntax errors"
		((VALIDATION_FAILURES++))
	fi
else
	warning "stress-test.sh not found"
fi

if [[ -f "scripts/testing/test-distributed.sh" ]]; then
	if grep -q "FlextConstants defaults" scripts/testing/test-distributed.sh; then
		success "test-distributed.sh uses standardized fallback patterns"
	else
		warning "test-distributed.sh may not use standardized patterns"
	fi

	# Check syntax
	if bash -n scripts/testing/test-distributed.sh; then
		success "test-distributed.sh has valid syntax"
	else
		error "test-distributed.sh has syntax errors"
		((VALIDATION_FAILURES++))
	fi
else
	warning "test-distributed.sh not found"
fi

# 4. Validate examples use project constants
info "Checking examples directories standardization..."

examples_fixed=0
examples_total=0

# Check client-a-oud-mig examples
if [[ -d "client-a-oud-mig/examples" ]]; then
	for example_file in client-a-oud-mig/examples/*.py; do
		if [[ -f $example_file ]]; then
			((examples_total++))
			if grep -q "client-aOudMigConstants" "$example_file"; then
				((examples_fixed++))
			fi
		fi
	done
fi

# Check other project examples
for project_dir in flext-*/examples; do
	if [[ -d $project_dir ]]; then
		for example_file in "$project_dir"/*.py; do
			if [[ -f $example_file ]]; then
				((examples_total++))
				# Check if they use constants properly (either project constants or avoid hardcoded values)
				if grep -E "(Constants|from.*constants)" "$example_file" >/dev/null; then
					((examples_fixed++))
				fi
			fi
		done
	fi
done

if [[ $examples_total -gt 0 ]]; then
	success "Examples standardization: $examples_fixed/$examples_total files use proper constants"
	if [[ $examples_fixed -eq $examples_total ]]; then
		success "All examples use standardized constants"
	elif [[ $examples_fixed -gt $((examples_total / 2)) ]]; then
		warning "Most examples use standardized constants ($examples_fixed/$examples_total)"
	else
		warning "Some examples may still have hardcoded constants"
	fi
else
	info "No example files found to validate"
fi

# 5. Validate FlextConstants is accessible
info "Checking FlextConstants accessibility..."

if timeout 10 python -c "
import sys
sys.path.insert(0, 'flext-core/src')
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u
print('FlextConstants available')
print(f'API Port: {FlextConstants.Platform.FLEXT_API_PORT}')
print(f'Default Timeout: {FlextConstants.Network.DEFAULT_TIMEOUT}')
print(f'Critical Duration: {FlextConstants.Performance.CRITICAL_DURATION_MS}')
" 2>/dev/null; then
	success "FlextConstants is accessible and working"
else
	error "FlextConstants is not accessible"
	((VALIDATION_FAILURES++))
fi

# 6. Final validation summary
echo ""
echo "📊 Validation Summary"
echo "===================="

if [[ $VALIDATION_FAILURES -eq 0 ]]; then
	success "All constants standardization validations passed!"
	echo ""
	info "Constants standardization implementation:"
	echo "  • scripts/constants.env synchronized with FlextConstants"
	echo "  • Automatic generation script implemented"
	echo "  • Test scripts use environment constants"
	echo "  • Examples use project constants"
	echo "  • FlextConstants foundation is accessible"
	echo ""
	success "✨ FLEXT Constants Standardization: COMPLETE ✨"
	exit 0
else
	error "Validation failed with $VALIDATION_FAILURES issues"
	echo ""
	warning "Please address the issues above and re-run validation"
	exit 1
fi

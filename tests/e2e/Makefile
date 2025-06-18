# E2E Test Makefile

.PHONY: help setup test test-fast test-full test-coverage clean logs shell

# Default target
help:
	@echo "Available targets:"
	@echo "  setup        - Install required Python packages"
	@echo "  test         - Run all E2E tests"
	@echo "  test-fast    - Run tests excluding slow ones"
	@echo "  test-full    - Run full test suite with coverage"
	@echo "  test-coverage- Run tests with coverage report"
	@echo "  clean        - Stop and remove all containers"
	@echo "  logs         - Show container logs"
	@echo "  shell        - Open shell in a container"
	@echo ""
	@echo "Test specific targets:"
	@echo "  test-pipeline    - Run pipeline tests only"
	@echo "  test-migration   - Run migration tests only"
	@echo "  test-edge        - Run edge case tests only"
	@echo ""
	@echo "Container targets:"
	@echo "  up           - Start all containers"
	@echo "  down         - Stop all containers"
	@echo "  restart      - Restart all containers"
	@echo "  status       - Show container status"

# Setup Python environment
setup:
	pip install pytest docker psycopg2-binary ldap3 faker pytest-cov pytest-xdist

# Run all tests
test:
	./run_e2e_tests.py

# Run fast tests (exclude slow)
test-fast:
	./run_e2e_tests.py -m "not slow"

# Run full test suite with coverage
test-full:
	./run_e2e_tests.py --coverage --pytest-args="-v"

# Run tests with coverage
test-coverage:
	./run_e2e_tests.py --coverage

# Test specific components
test-pipeline:
	./run_e2e_tests.py scenarios/test_full_pipeline.py

test-migration:
	./run_e2e_tests.py scenarios/test_migration_scenarios.py

test-edge:
	./run_e2e_tests.py scenarios/test_edge_cases.py

# Container management
up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10

down:
	docker-compose down

restart:
	docker-compose restart

status:
	docker-compose ps

# Clean up everything
clean:
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache htmlcov .coverage
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Show logs
logs:
	docker-compose logs -f --tail=100

logs-source:
	docker-compose logs -f --tail=100 ldap-source

logs-target:
	docker-compose logs -f --tail=100 ldap-target

logs-postgres:
	docker-compose logs -f --tail=100 postgres

# Interactive shells
shell-source:
	docker-compose exec ldap-source /bin/bash

shell-target:
	docker-compose exec ldap-target /bin/bash

shell-postgres:
	docker-compose exec postgres psql -U dbt_user -d dbt_ldap_test

# Debug helpers
debug-source:
	@echo "Searching source LDAP..."
	docker-compose exec ldap-source ldapsearch -x -b "dc=source,dc=example,dc=com" -D "cn=REDACTED_LDAP_BIND_PASSWORD,dc=source,dc=example,dc=com" -w REDACTED_LDAP_BIND_PASSWORD_source_password "(objectClass=*)" dn

debug-target:
	@echo "Searching target LDAP..."
	docker-compose exec ldap-target ldapsearch -x -b "dc=target,dc=example,dc=com" -D "cn=REDACTED_LDAP_BIND_PASSWORD,dc=target,dc=example,dc=com" -w REDACTED_LDAP_BIND_PASSWORD_target_password "(objectClass=*)" dn

# Run specific test with debugging
debug-test:
	./run_e2e_tests.py --keep-containers --pytest-args="--pdb -vv -s" $(TEST)

# ═══════════════════════════════════════════════════════════════════════════
# FLEXT SERVICE PROJECT TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Service-specific targets for API, web, and daemon services
# Usage: include $(FLEXT_ROOT)/templates/makefiles/service/service.mk
# Dependencies: templates/makefiles/python/python.mk
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
#  SERVICE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Service configuration (override in project Makefile)
SERVICE_NAME ?= $(PROJECT_NAME)
SERVICE_HOST ?= 0.0.0.0
SERVICE_PORT ?= 8000
SERVICE_WORKERS ?= 4
SERVICE_LOG_LEVEL ?= info
SERVICE_RELOAD ?= true

# Health check configuration
HEALTH_CHECK_URL ?= http://$(SERVICE_HOST):$(SERVICE_PORT)/health
HEALTH_CHECK_TIMEOUT ?= 30
HEALTH_CHECK_RETRIES ?= 5

# Docker configuration
DOCKER_IMAGE ?= $(SERVICE_NAME)
DOCKER_TAG ?= latest
DOCKER_REGISTRY ?=

# ═══════════════════════════════════════════════════════════════════════════
#  SERVICE MANAGEMENT TARGETS
# ═══════════════════════════════════════════════════════════════════════════

serve: ## Start development server
	$(call log_section,Starting Development Server)
	$(call log_info,Service: $(SERVICE_NAME))
	$(call log_info,Host: $(SERVICE_HOST):$(SERVICE_PORT))
	$(call log_info,Workers: $(SERVICE_WORKERS))
	@$(MAKE) _start_service

serve-prod: ## Start production server
	$(call log_section,Starting Production Server)
	@SERVICE_RELOAD=false $(MAKE) _start_service

serve-debug: ## Start server in debug mode
	$(call log_section,Starting Debug Server)
	@SERVICE_LOG_LEVEL=debug SERVICE_RELOAD=true $(MAKE) _start_service

_start_service: ## Internal: Start service (auto-detects service type)
	@if [ -f "$(PYTHON_SRC_DIR)/main.py" ] && grep -q "FastAPI\|Starlette" "$(PYTHON_SRC_DIR)/main.py" 2>/dev/null; then \
		$(MAKE) _start_fastapi; \
	elif [ -f "$(PYTHON_SRC_DIR)/wsgi.py" ] || [ -f "manage.py" ]; then \
		$(MAKE) _start_django; \
	elif [ -f "$(PYTHON_SRC_DIR)/app.py" ] && grep -q "Flask" "$(PYTHON_SRC_DIR)/app.py" 2>/dev/null; then \
		$(MAKE) _start_flask; \
	else \
		$(MAKE) _start_generic; \
	fi

_start_fastapi: ## Internal: Start FastAPI service
	@if command -v uvicorn >/dev/null 2>&1; then \
		$(call log_info,Starting FastAPI with uvicorn); \
		$(PYTHON) -m uvicorn $(shell echo $(PROJECT_NAME) | tr '-' '_').main:app \
			--host $(SERVICE_HOST) \
			--port $(SERVICE_PORT) \
			--log-level $(SERVICE_LOG_LEVEL) \
			$(if $(filter true,$(SERVICE_RELOAD)),--reload,) \
			$(if $(filter false,$(SERVICE_RELOAD)),--workers $(SERVICE_WORKERS),); \
	else \
		$(call log_warning,uvicorn not found, using generic start); \
		$(MAKE) _start_generic; \
	fi

_start_django: ## Internal: Start Django service
	@if [ -f "manage.py" ]; then \
		$(call log_info,Starting Django development server); \
		$(PYTHON) manage.py runserver $(SERVICE_HOST):$(SERVICE_PORT); \
	else \
		$(call log_info,Starting Django with gunicorn); \
		gunicorn $(shell echo $(PROJECT_NAME) | tr '-' '_').wsgi:application \
			--bind $(SERVICE_HOST):$(SERVICE_PORT) \
			--workers $(SERVICE_WORKERS) \
			--log-level $(SERVICE_LOG_LEVEL); \
	fi

_start_flask: ## Internal: Start Flask service
	@$(call log_info,Starting Flask development server)
	@FLASK_APP=$(shell echo $(PROJECT_NAME) | tr '-' '_').app \
		FLASK_ENV=development \
		$(PYTHON) -m flask run \
		--host $(SERVICE_HOST) \
		--port $(SERVICE_PORT)

_start_generic: ## Internal: Start generic Python service
	@$(call log_info,Starting generic Python service)
	@if [ -f "$(PYTHON_SRC_DIR)/main.py" ]; then \
		$(PYTHON) $(PYTHON_SRC_DIR)/main.py; \
	elif [ -f "$(PYTHON_SRC_DIR)/__main__.py" ]; then \
		$(PYTHON) -m $(shell echo $(PROJECT_NAME) | tr '-' '_'); \
	else \
		$(call log_error,No main.py or __main__.py found); \
		exit 1; \
	fi

stop: ## Stop running service
	$(call log_section,Stopping Service)
	@pkill -f "$(SERVICE_NAME)" 2>/dev/null || true
	@pkill -f "$(SERVICE_PORT)" 2>/dev/null || true
	$(call log_success,Service stopped)

restart: stop serve ## Restart service

# ═══════════════════════════════════════════════════════════════════════════
#  HEALTH CHECK TARGETS
# ═══════════════════════════════════════════════════════════════════════════

health: ## Check service health
	$(call log_section,Checking Service Health)
	@if curl -f -s --connect-timeout 5 $(HEALTH_CHECK_URL) >/dev/null 2>&1; then \
		$(call log_success,Service is healthy); \
		curl -s $(HEALTH_CHECK_URL) | jq . 2>/dev/null || curl -s $(HEALTH_CHECK_URL); \
	else \
		$(call log_error,Service is not healthy or not running); \
		exit 1; \
	fi

health-wait: ## Wait for service to become healthy
	$(call log_section,Waiting for Service Health)
	@for i in $$(seq 1 $(HEALTH_CHECK_RETRIES)); do \
		if curl -f -s --connect-timeout 5 $(HEALTH_CHECK_URL) >/dev/null 2>&1; then \
			$(call log_success,Service is healthy after $$i attempts); \
			exit 0; \
		fi; \
		$(call log_info,Attempt $$i/$(HEALTH_CHECK_RETRIES) failed, waiting...); \
		sleep $(HEALTH_CHECK_TIMEOUT); \
	done; \
	$(call log_error,Service failed to become healthy after $(HEALTH_CHECK_RETRIES) attempts); \
	exit 1

status: ## Show service status
	$(call log_section,Service Status)
	@echo "Service: $(SERVICE_NAME)"
	@echo "URL: http://$(SERVICE_HOST):$(SERVICE_PORT)"
	@echo "Health: $(HEALTH_CHECK_URL)"
	@echo ""
	@if curl -f -s --connect-timeout 2 $(HEALTH_CHECK_URL) >/dev/null 2>&1; then \
		echo "$(GREEN)● Service is running$(RESET)"; \
	else \
		echo "$(RED)● Service is not running$(RESET)"; \
	fi
	@echo ""
	@echo "Process information:"
	@ps aux | grep -E "($(SERVICE_NAME)|$(SERVICE_PORT))" | grep -v grep || echo "No processes found"

# ═══════════════════════════════════════════════════════════════════════════
#  SERVICE TESTING TARGETS
# ═══════════════════════════════════════════════════════════════════════════

test-service: ## Run service-specific tests
	$(call log_section,Running Service Tests)
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -m "service or api or integration" -v; \
	else \
		$(call log_warning,No service tests found); \
	fi

test-api: ## Test API endpoints
	$(call log_section,Testing API Endpoints)
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -m "api" -v; \
	else \
		$(call log_warning,No API tests found); \
	fi

test-load: ## Run load tests
	$(call log_section,Running Load Tests)
	@if command -v locust >/dev/null 2>&1 && [ -f "tests/load/locustfile.py" ]; then \
		$(call log_info,Starting load tests with Locust); \
		locust -f tests/load/locustfile.py --host=http://$(SERVICE_HOST):$(SERVICE_PORT); \
	elif command -v ab >/dev/null 2>&1; then \
		$(call log_info,Running basic load test with Apache Bench); \
		ab -n 1000 -c 10 $(HEALTH_CHECK_URL); \
	else \
		$(call log_warning,No load testing tools available (locust, ab)); \
	fi

test-e2e: ## Run end-to-end tests
	$(call log_section,Running E2E Tests)
	@$(MAKE) serve-debug & \
	SERVER_PID=$$!; \
	sleep 5; \
	$(MAKE) health-wait; \
	if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -m "e2e" -v; \
		TEST_RESULT=$$?; \
	else \
		$(call log_warning,No E2E tests found); \
		TEST_RESULT=0; \
	fi; \
	kill $$SERVER_PID 2>/dev/null || true; \
	exit $$TEST_RESULT

# ═══════════════════════════════════════════════════════════════════════════
#  DOCKER TARGETS
# ═══════════════════════════════════════════════════════════════════════════

docker-build: ## Build Docker image
	$(call log_section,Building Docker Image)
	@if [ -f "Dockerfile" ]; then \
		docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .; \
		$(call log_success,Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)); \
	else \
		$(call log_error,No Dockerfile found); \
		exit 1; \
	fi

docker-run: ## Run service in Docker
	$(call log_section,Running Service in Docker)
	@docker run -d \
		--name $(SERVICE_NAME) \
		-p $(SERVICE_PORT):$(SERVICE_PORT) \
		-e SERVICE_HOST=0.0.0.0 \
		-e SERVICE_PORT=$(SERVICE_PORT) \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	$(call log_success,Service running in Docker container: $(SERVICE_NAME))

docker-stop: ## Stop Docker container
	$(call log_section,Stopping Docker Container)
	@docker stop $(SERVICE_NAME) 2>/dev/null || true
	@docker rm $(SERVICE_NAME) 2>/dev/null || true
	$(call log_success,Docker container stopped and removed)

docker-logs: ## Show Docker container logs
	@docker logs -f $(SERVICE_NAME)

docker-shell: ## Open shell in Docker container
	@docker exec -it $(SERVICE_NAME) /bin/bash

# ═══════════════════════════════════════════════════════════════════════════
#  DATABASE TARGETS (for services with databases)
# ═══════════════════════════════════════════════════════════════════════════

migrate: ## Run database migrations
	$(call log_section,Running Database Migrations)
	@if [ -f "manage.py" ]; then \
		$(PYTHON) manage.py migrate; \
	elif [ -f "alembic.ini" ]; then \
		alembic upgrade head; \
	else \
		$(call log_warning,No migration system detected); \
	fi

migrate-check: ## Check for pending migrations
	$(call log_section,Checking Migrations)
	@if [ -f "manage.py" ]; then \
		$(PYTHON) manage.py makemigrations --check --dry-run; \
	elif [ -f "alembic.ini" ]; then \
		alembic check; \
	else \
		$(call log_warning,No migration system detected); \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  DEPLOYMENT TARGETS
# ═══════════════════════════════════════════════════════════════════════════

deploy-check: ## Check deployment readiness
	$(call log_section,Checking Deployment Readiness)
	@$(MAKE) validate
	@$(MAKE) quality
	@$(MAKE) test
	@$(MAKE) build-check
	$(call log_success,Deployment checks passed)

deploy-build: ## Build for deployment
	$(call log_section,Building for Deployment)
	@$(MAKE) clean
	@$(MAKE) install-minimal
	@$(MAKE) build
	@if [ -f "Dockerfile" ]; then \
		$(MAKE) docker-build; \
	fi
	$(call log_success,Deployment build completed)

# ═══════════════════════════════════════════════════════════════════════════
#  PHONY TARGETS
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: serve serve-prod serve-debug stop restart
.PHONY: health health-wait status
.PHONY: test-service test-api test-load test-e2e
.PHONY: docker-build docker-run docker-stop docker-logs docker-shell
.PHONY: migrate migrate-check
.PHONY: deploy-check deploy-build
.PHONY: _start_service _start_fastapi _start_django _start_flask _start_generic

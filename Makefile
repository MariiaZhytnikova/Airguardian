# ================================================================
# ✨ Drone Monitoring System — Makefile
# ================================================================

# Colors
GREEN  := \033[0;32m
BLUE   := \033[0;34m
YELLOW := \033[1;33m
RED    := \033[0;31m
NC     := \033[0m

# Default environment
ENV_FILE = .env

# ================================================================
# 🎯 Help
# ================================================================
.PHONY: help
help:
	@echo ""
	@echo "$(BLUE)🚀 Drone Monitoring System – Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ================================================================
# 🐳 Docker Commands
# ================================================================
up: ## Start all services (build if needed)
	@echo "$(YELLOW)Starting Docker services...$(NC)"
	docker compose up --build

down: ## Stop all services
	@echo "$(YELLOW)Stopping Docker services...$(NC)"
	docker compose down

restart: ## Restart all services
	@echo "$(YELLOW)Restarting Docker services...$(NC)"
	docker compose down
	docker compose up --build

logs: ## View logs from all containers
	docker compose logs -f

ps: ## Show running Docker containers
	docker compose ps

# ================================================================
# 🧪 Local Development
# ================================================================
run: ## Run FastAPI backend locally (without Docker)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

celery-worker: ## Run Celery worker locally
	celery -A app.celery_app worker --loglevel=info

celery-beat: ## Run Celery beat scheduler locally
	celery -A app.celery_app beat --loglevel=info

# ================================================================
# 🐘 Database Commands
# ================================================================
db-shell: ## Enter PostgreSQL shell inside Docker
	docker exec -it postgres-db psql -U $$POSTGRES_USER -d $$POSTGRES_DB

db-reset: ## ⚠️ Delete DB volume + reset everything
	@echo "$(RED)WARNING: This will delete ALL database data!$(NC)"
	docker compose down -v

# ================================================================
# 🧹 Code Quality
# ================================================================
format: ## Format code with Black
	poetry run black app

lint: ## Lint code with Flake8
	poetry run flake8 app

# ================================================================
# 🔧 Utilities
# ================================================================
env: ## Create .env file from example
	cp .env.example .env && echo "$(GREEN).env created$(NC)"

clean: ## Remove Python cache files
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.pyc" -exec rm -r {} +

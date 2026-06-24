.PHONY: help dev dev-backend dev-dashboard install test lint build deploy clean demo

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Development ──────────────────────────────────────────────────────────────

install: ## Install all dependencies
	cd backend && pip install -e ".[dev]"
	cd dashboard && npm install

dev: ## Start all services for development
	@echo "Starting Crosscut development environment..."
	$(MAKE) -j2 dev-backend dev-dashboard

dev-backend: ## Start backend dev server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-dashboard: ## Start dashboard dev server
	cd dashboard && npm run dev

# ─── Testing ──────────────────────────────────────────────────────────────────

test: ## Run all tests
	cd backend && pytest -v --cov=app --cov-report=term-missing

test-unit: ## Run unit tests only
	cd backend && pytest tests/unit -v

test-integration: ## Run integration tests
	cd backend && pytest tests/integration -v

# ─── Code Quality ────────────────────────────────────────────────────────────

lint: ## Run linters
	cd backend && ruff check app/ && ruff format --check app/
	cd dashboard && npm run lint

format: ## Auto-format code
	cd backend && ruff format app/ tests/
	cd dashboard && npx prettier --write "src/**/*.{ts,tsx,css}"

# ─── Build ────────────────────────────────────────────────────────────────────

build: ## Build production images
	docker compose -f deploy/docker-compose.yml build

build-dashboard: ## Build dashboard for production
	cd dashboard && npm run build

# ─── Deployment ───────────────────────────────────────────────────────────────

deploy: ## Deploy with Docker Compose
	docker compose -f deploy/docker-compose.yml up -d

deploy-dev: ## Deploy development stack
	docker compose -f deploy/docker-compose.dev.yml up -d

down: ## Stop all services
	docker compose -f deploy/docker-compose.yml down

# ─── Database ─────────────────────────────────────────────────────────────────

db-migrate: ## Run database migrations
	cd backend && alembic upgrade head

db-revision: ## Create new migration
	cd backend && alembic revision --autogenerate -m "$(msg)"

# ─── Demo ─────────────────────────────────────────────────────────────────────

demo: ## Run the hackathon demo scenario
	cd backend && python -m demo.demo_scenario

demo-seed: ## Seed database with demo data
	cd backend && python -m demo.seed_data

# ─── Cleanup ──────────────────────────────────────────────────────────────────

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -rf backend/dist backend/build
	rm -rf dashboard/.next dashboard/out

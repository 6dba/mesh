.PHONY: dev-up dev-down prod-up prod-down deploy test lint sync docs clean master agent

dev-up:
	docker-compose up -d --build

dev-down:
	docker-compose down

prod-up:
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker-compose -f docker-compose.prod.yml down

deploy:
	cd ansible && ./deploy.sh

sync:
	uv sync

install:
	uv pip install -e .

test:
	uv run pytest master/tests agent/tests cli/tests sdk/tests --cov

lint:
	uv run flake8 .
	uv run black --check .
	uv run isort --check-only .

master:
	uv run kosatka-mesh master run

agent:
	uv run kosatka-mesh agent run

docs:
	@echo "Documentation is available in the docs/ directory."
	@echo "Main entry point: docs/quickstart.md"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

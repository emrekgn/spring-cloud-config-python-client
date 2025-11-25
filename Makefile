.PHONY: help install install-dev clean lint test get-version set-version build publish

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in production mode
	uv sync --frozen

install-dev:  ## Install package with development dependencies
	uv python install 3.12
	uv sync --all-extras
	uv run pre-commit install

clean:  ## Clean build artifacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:  ## Run linting checks
	uv run ruff check .
	uv run mypy ai_streaming_client

test:  ## Run unit tests
	uv run pytest

get-version: ## Get version
	@python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

set-version: ## Set version
ifndef VERSION
	@echo "Missing argument: VERSION" && false;
endif
	@sed -i 's/^version = ".*"/version = "$(VERSION)"/' pyproject.toml
	uv sync --all-extras

build:  ## Build package
	rm -rf dist/
	uv build

publish: build ## Publish package
ifndef AUTH_TOKEN
	@echo "Missing argument: AUTH_TOKEN" && false;
endif
	export UV_PUBLISH_URL="https://github.com/emrekgn/api/v4/projects/packages/pypi" && \
	export UV_PUBLISH_USERNAME="github+token" && \
	export UV_PUBLISH_PASSWORD=${AUTH_TOKEN} && \
	uv publish dist/*.whl

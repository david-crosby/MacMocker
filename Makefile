.PHONY: help install test test-quick test-full clean build deploy lint format

help:
	@echo "MacMocker - Available commands:"
	@echo ""
	@echo "  make install     - Install dependencies using uv"
	@echo "  make test-quick  - Run quick test suite"
	@echo "  make test-full   - Run full test suite"
	@echo "  make clean       - Clean build artifacts and caches"
	@echo "  make build       - Build .pkg installer"
	@echo "  make lint        - Run linting checks"
	@echo "  make format      - Format code with black"
	@echo ""

install:
	@echo "Installing dependencies with uv..."
	uv pip install -e .
	@echo "Installation complete!"

test-quick:
	@echo "Running quick test suite..."
	python3 main.py --config config/quick_tests.yaml --log-level INFO

test-full:
	@echo "Running full test suite..."
	python3 main.py --config config/full_tests.yaml --log-level INFO

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf deployment/build/
	@echo "Clean complete!"

build:
	@echo "Building package..."
	cd deployment && chmod +x build_pkg.sh && ./build_pkg.sh
	@echo "Build complete!"

lint:
	@echo "Running linting checks..."
	ruff check .
	@echo "Linting complete!"

format:
	@echo "Formatting code..."
	black .
	@echo "Formatting complete!"

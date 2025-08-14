.PHONY: install build-css build-css-prod dev server clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install Python and Node.js dependencies"
	@echo "  build-css    - Build CSS in development mode (with watch)"
	@echo "  build-css-prod - Build CSS in production mode (minified)"
	@echo "  dev          - Start development server with CSS building"
	@echo "  server       - Start gunicorn production server"
	@echo "  clean        - Clean generated files"

# Install dependencies
install:
	pip install -r requirements.txt
	npm install

# Build CSS in development mode
build-css:
	npm run build-css

# Build CSS in production mode (minified)
build-css-prod:
	npm run build-css-prod

# Development server - builds CSS and starts Flask dev server
dev: build-css
	gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

# Production server with gunicorn
server: build-css-prod
	gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

# Clean generated files
clean:
	rm -f assets/css/output.css
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

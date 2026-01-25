.PHONY: help build run stop restart logs status clean prune dev run-local install

# Default target
help:
	@echo "EPD Display Management"
	@echo ""
	@echo "Production targets:"
	@echo "  make build     - Build container image"
	@echo "  make run       - Start production container"
	@echo "  make stop      - Stop container"
	@echo "  make restart   - Restart container"
	@echo "  make logs      - View container logs (follow mode)"
	@echo "  make status    - Show container status"
	@echo "  make clean     - Stop and remove container"
	@echo "  make prune     - Remove container and image"
	@echo ""
	@echo "Development targets:"
	@echo "  make dev       - Start development environment (hot reload)"
	@echo "  make dev-stop  - Stop development environment"
	@echo "  make dev-logs  - View development logs"
	@echo ""
	@echo "Local (no container) targets:"
	@echo "  make install   - Install dependencies (frontend + backend)"
	@echo "  make run-local - Run locally (no containers)"
	@echo ""
	@echo "Service targets:"
	@echo "  make shell     - Shell into container"
	@echo ""

# Build container image
build:
	@echo "Building EPD Display container image..."
	podman-compose build
	@echo "Done!"

# Start production container
run:
	@echo "Starting EPD Display container..."
	podman-compose up -d
	@echo "Done!"
	@echo "Access the web interface at http://localhost"

# Stop container
stop:
	@echo "Stopping EPD Display container..."
	podman-compose down
	@echo "Done!"

# Restart container
restart: stop run

# View container logs
logs:
	@echo "Showing container logs (Ctrl+C to exit)..."
	podman-compose logs -f

# Show container status
status:
	@echo "Container status:"
	@podman ps -a --filter name=epd
	@echo ""
	@echo "API Health:"
	@curl -s http://localhost/api/v1/health 2>/dev/null | jq . || echo "Not accessible"
	@echo ""
	@echo "Scheduler status:"
	@curl -s http://localhost/api/v1/scheduler 2>/dev/null | jq . || echo "Not accessible"

# Clean up container
clean: stop
	@echo "Removing container..."
	podman rm -f epd-app 2>/dev/null || true
	@echo "Done!"

# Remove container and image
prune: clean
	@echo "Removing container image..."
	podman rmi epd_color_display-app:latest 2>/dev/null || true
	@echo "Done!"

# Development targets
dev:
	@echo "Starting development environment..."
	podman-compose -f docker-compose.dev.yml up -d
	@echo "Done!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"

dev-stop:
	@echo "Stopping development environment..."
	podman-compose -f docker-compose.dev.yml down
	@echo "Done!"

dev-logs:
	@echo "Showing development logs (Ctrl+C to exit)..."
	podman-compose -f docker-compose.dev.yml logs -f

# Shell target
shell:
	@echo "Opening shell in container..."
	podman exec -it epd-app /bin/bash

# Local (no container) targets
install:
	@echo "Installing frontend dependencies..."
	@cd frontend && bun install
	@echo "Installing backend dependencies..."
	@cd backend && uv sync
	@echo "Done!"

run-local: install
	@echo "Building frontend..."
	@cd frontend && bun run build
	@echo "Starting backend (serving frontend)..."
	@echo "Access at http://localhost:8000"
	@cd backend && GPIOZERO_PIN_FACTORY=lgpio uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: help build run stop restart logs status clean prune dev

# Default target
help:
	@echo "EPD Display Container Management"
	@echo ""
	@echo "Production targets:"
	@echo "  make build     - Build all container images"
	@echo "  make run       - Start production containers"
	@echo "  make stop      - Stop all containers"
	@echo "  make restart   - Restart all containers"
	@echo "  make logs      - View container logs (follow mode)"
	@echo "  make status    - Show container status"
	@echo "  make clean     - Stop and remove all containers"
	@echo "  make prune     - Remove containers and images"
	@echo ""
	@echo "Development targets:"
	@echo "  make dev       - Start development environment (hot reload)"
	@echo "  make dev-stop  - Stop development environment"
	@echo "  make dev-logs  - View development logs"
	@echo ""
	@echo "Service targets:"
	@echo "  make shell-backend  - Shell into backend container"
	@echo "  make shell-frontend - Shell into frontend container"
	@echo ""

# Build all container images
build:
	@echo "Building EPD Display container images..."
	podman-compose build
	@echo "Done!"

# Start production containers
run:
	@echo "Starting EPD Display containers..."
	podman-compose up -d
	@echo "Done!"
	@echo "Access the web interface at http://localhost"

# Stop all containers
stop:
	@echo "Stopping EPD Display containers..."
	podman-compose down
	@echo "Done!"

# Restart containers
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
	@curl -s http://localhost/api/v1/health 2>/dev/null | jq . || echo "Backend not accessible"
	@echo ""
	@echo "Scheduler status:"
	@curl -s http://localhost/api/v1/scheduler 2>/dev/null | jq . || echo "Backend not accessible"

# Clean up containers
clean: stop
	@echo "Removing containers..."
	podman rm -f epd-backend epd-frontend 2>/dev/null || true
	@echo "Done!"

# Remove containers and images
prune: clean
	@echo "Removing container images..."
	podman rmi epd-color-display-backend:latest epd-color-display-frontend:latest 2>/dev/null || true
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

# Shell targets
shell-backend:
	@echo "Opening shell in backend container..."
	podman exec -it epd-backend /bin/bash

shell-frontend:
	@echo "Opening shell in frontend container..."
	podman exec -it epd-frontend /bin/sh

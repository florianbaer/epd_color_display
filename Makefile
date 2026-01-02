.PHONY: help build run stop restart logs status clean prune

# Default target
help:
	@echo "EPD Display Container Management"
	@echo ""
	@echo "Available targets:"
	@echo "  make build     - Build the container image"
	@echo "  make run       - Start the container"
	@echo "  make stop      - Stop the container"
	@echo "  make restart   - Restart the container"
	@echo "  make logs      - View container logs (follow mode)"
	@echo "  make status    - Show container status"
	@echo "  make clean     - Stop and remove the container"
	@echo "  make prune     - Remove container and image"
	@echo "  make shell     - Open a shell in the running container"
	@echo ""

# Build the container image
build:
	@echo "Building epd-display container image..."
	podman build -t epd-display:latest .
	@echo "✓ Build complete!"

# Start the container using compose
run:
	@echo "Starting EPD Display container..."
	podman-compose up -d
	@echo "✓ Container started!"
	@echo "Access the web interface at http://localhost"

# Stop the container
stop:
	@echo "Stopping EPD Display container..."
	podman-compose down
	@echo "✓ Container stopped!"

# Restart the container
restart: stop run

# View container logs
logs:
	@echo "Showing container logs (Ctrl+C to exit)..."
	podman logs -f epd-display

# Show container status
status:
	@echo "Container status:"
	@podman ps -a --filter name=epd-display
	@echo ""
	@echo "Scheduler status:"
	@curl -s http://localhost/scheduler-status 2>/dev/null | jq . || echo "Container not running or not accessible"

# Clean up container
clean: stop
	@echo "Removing container..."
	podman rm -f epd-display 2>/dev/null || true
	@echo "✓ Cleanup complete!"

# Remove container and image
prune: clean
	@echo "Removing container image..."
	podman rmi epd-display:latest 2>/dev/null || true
	@echo "✓ Prune complete!"

# Open shell in running container
shell:
	@echo "Opening shell in container..."
	podman exec -it epd-display /bin/bash

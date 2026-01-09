#!/bin/bash
# Force update to latest Docker image from GHCR

set -e

echo "🔄 Forcing update to latest image from GitHub Container Registry..."

# Stop and remove existing container
echo "📦 Stopping existing container..."
docker compose down

# Remove the old image to force fresh pull
echo "🗑️  Removing old image..."
docker rmi ghcr.io/liamgwallace/docker-assistant-claude-mcp:latest 2>/dev/null || echo "Image already removed or doesn't exist locally"

# Pull the latest image (bypass cache)
echo "⬇️  Pulling latest image from GHCR (this may take a few minutes)..."
docker pull ghcr.io/liamgwallace/docker-assistant-claude-mcp:latest --no-cache

# Start with the fresh image
echo "🚀 Starting container with fresh image..."
docker compose up -d

# Wait for container to start
echo "⏳ Waiting for container to be healthy..."
sleep 5

# Show status
echo ""
echo "📊 Container status:"
docker compose ps

# Test Claude CLI
echo ""
echo "🧪 Testing Claude Code CLI installation:"
docker exec docker-mcp-server which claude || echo "❌ Claude CLI not found"
docker exec docker-mcp-server claude --version || echo "❌ Claude CLI not working"

# Test health check
echo ""
echo "🏥 Testing health check:"
docker exec docker-mcp-server nc -z localhost 8000 && echo "✅ Health check OK" || echo "❌ Health check failed"

echo ""
echo "✅ Update complete! Check logs with: docker compose logs -f"

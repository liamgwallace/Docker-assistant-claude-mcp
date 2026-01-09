FROM python:3.11-slim

LABEL org.opencontainers.image.title="Docker Management MCP Server"
LABEL org.opencontainers.image.description="AI-assisted Docker container management via FastMCP and Claude Code"
LABEL org.opencontainers.image.source="https://github.com/yourusername/docker-assistant-claude-mcp"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    jq \
    bash \
    git \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh

# Install Docker Compose plugin
RUN mkdir -p /usr/local/lib/docker/cli-plugins && \
    curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose && \
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Install Portainer Stack Utils (psu)
RUN curl -L https://github.com/greenled/portainer-stack-utils/releases/latest/download/psu_linux_amd64 \
    -o /usr/local/bin/psu && \
    chmod +x /usr/local/bin/psu

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Claude Code CLI (native installation for Linux)
RUN curl -fsSL https://claude.ai/install.sh | bash

# Add Claude Code CLI to PATH (installs to ~/.local/bin for root user)
ENV PATH="/root/.local/bin:${PATH}"

# Copy application code
COPY src/ ./src/
COPY docs/ ./docs/
COPY skills/ ./skills/
COPY src/config/ ./config/

# Create data directory for job storage
RUN mkdir -p /app/data/jobs

# Create volume mount points
RUN mkdir -p /home/liam/docker/stacks /home/liam/docker/volumes

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check - verify server port is listening
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD nc -z localhost 8000 || exit 1

# Expose MCP server port
EXPOSE 8000

# Run the FastMCP server (now defaults to HTTP mode)
CMD ["python", "-m", "src.server"]

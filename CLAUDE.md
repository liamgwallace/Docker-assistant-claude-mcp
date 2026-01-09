# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Docker Management MCP Server - An AI-assisted Docker container management system that exposes Docker and Portainer operations as Model Context Protocol (MCP) tools. The architecture uses FastMCP to provide tools that Claude Desktop (or other MCP clients) can call, which then delegate to Claude Code CLI for actual Docker operations.

**Key Insight:** This is a "Claude-managing-Claude" architecture where:
1. MCP client (e.g., Claude Desktop) calls MCP tools
2. FastMCP server receives the tool call
3. Server delegates to Claude Code CLI with structured prompts
4. Claude Code CLI executes Docker/Portainer commands
5. Results flow back through the chain

## Development Commands

### Local Development

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server (defaults to HTTP mode on 0.0.0.0:8000)
python -m src.server

# Or run with uvicorn directly
python -m uvicorn src.server:mcp.app --reload --host 0.0.0.0 --port 8000

# Set required environment variables first (or use .env file)
export ANTHROPIC_API_KEY="your-key"
export PORTAINER_URL="http://localhost:9000"
```

### Docker Deployment

```bash
# Production: Use pre-built image from GitHub Container Registry
docker compose up -d
docker compose logs -f
docker compose down

# Development: Build and run locally
docker compose -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.dev.yml logs -f

# View logs
docker logs docker-mcp-server

# Health check (internal port)
docker exec docker-mcp-server curl -f http://localhost:8000/health

# Access from network (external port 8523)
curl http://192.168.8.146:8523/mcp
curl http://192.168.8.146:8523/health
```

### Testing MCP Tools

```bash
# Test docker_execute tool
curl -X POST http://localhost:8000/tools/docker_execute \
  -H "Content-Type: application/json" \
  -d '{"request": "List all running containers"}'

# Use MCP Inspector for interactive testing
npx @modelcontextprotocol/inspector http://localhost:8000
```

## Architecture

### Request Flow

```
MCP Client → FastMCP Server → ClaudeCodeExecutor → Claude Code CLI → Docker/Portainer
     ↓              ↓                  ↓                    ↓              ↓
   Tool         Tool Handler      Prompt Builder      Command Exec     Operations
```

### Core Components

**1. FastMCP Server (`src/server.py`)**
- Defines three MCP tools: `docker_execute`, `docker_execute_async`, `docker_job_status`
- Handles lifecycle management (startup/shutdown)
- Implements periodic job cleanup background task
- Each tool returns structured markdown responses in MCP format

**2. Docker Manager (`src/tools/docker_manager.py`)**
- Orchestrates between executor and job tracker
- Handles sync vs async execution patterns
- Formats responses with consistent markdown structure

**3. Claude Code Executor (`src/tools/claude_code_executor.py`)**
- **Critical component**: Builds comprehensive prompts for Claude Code CLI
- Loads three context sources:
  - `skills/docker-management-skill.md` - Docker/Portainer command reference
  - `src/config/system_config.yaml` - System-specific settings (IPs, paths)
  - `src/config/docker_compose_template.yaml` - Template for new stacks
- Executes Claude Code CLI via subprocess in headless mode: `claude -p <prompt> --model <model>`
- Uses ANTHROPIC_API_KEY environment variable for authentication (no interactive login)
- Validates environment on startup

**4. Job Tracker (`src/tools/job_tracker.py`)**
- File-based storage in `/app/data/jobs/` (one JSON file per job)
- States: PENDING → RUNNING → COMPLETED/FAILED
- Auto-cleanup of old jobs (default: 24 hours)

**5. Configuration (`src/config/environment.py`)**
- Pydantic Settings with environment variable loading
- Supports `.env` files for local development
- Creates required directories on initialization

### Key Files That Form "Claude Code's Brain"

When making changes to what Claude Code does, these files define its behavior:

1. **`skills/docker-management-skill.md`** - Docker command reference, naming conventions, workflows
2. **`src/config/system_config.yaml`** - Environment-specific values (networks, domains, paths)
3. **`src/config/docker_compose_template.yaml`** - Template for generating stack files

The prompt builder in `claude_code_executor.py:_build_prompt()` combines these into a single context-rich prompt.

### Container-to-Host Networking

The MCP server runs in a container but needs to access services on the Docker host (like Portainer). This is handled via `host.docker.internal`:

- `docker-compose.yml` includes `extra_hosts: - "host.docker.internal:host-gateway"`
- Default `PORTAINER_URL` uses `http://host.docker.internal:9000`
- Works on Docker Desktop by default; enabled on Linux via extra_hosts

## Critical Patterns

### Adding a New MCP Tool

1. Add tool definition in `src/server.py` with `@mcp.tool()` decorator
2. Add handler method in `src/tools/docker_manager.py`
3. Tool must return dict with structure: `{"content": [{"type": "text", "text": "..."}]}`
4. Use markdown formatting in response text

### Modifying Claude Code Behavior

1. **For command changes**: Edit `skills/docker-management-skill.md`
2. **For environment values**: Edit `src/config/system_config.yaml`
3. **For stack templates**: Edit `src/config/docker_compose_template.yaml`
4. **For prompt structure**: Edit `claude_code_executor.py:_build_prompt()`

### Error Handling Pattern

All tools follow this pattern:
```python
try:
    result = await some_operation()
    return {"content": [{"type": "text", "text": result}]}
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    return {"content": [{"type": "text", "text": f"## Error\n\n{str(e)}"}]}
```

### Async Job Pattern

1. `docker_execute_async` creates job via `JobTracker.create_job()`
2. Spawns background task with `asyncio.create_task(_execute_background_job())`
3. Returns immediately with job ID
4. Background task updates job status: PENDING → RUNNING → COMPLETED/FAILED
5. Client polls with `docker_job_status` to check progress

## Environment Variables

Required:
- `ANTHROPIC_API_KEY` - Required for Claude Code CLI authentication (no interactive login needed)

Important:
- `PORTAINER_URL` - Default: `http://host.docker.internal:9000`
- `PORTAINER_TOKEN` - Required for Portainer operations
- `STACKS_DIR` - Where Docker Compose files are stored (default: `/home/liam/docker/stacks`)
- `VOLUMES_DIR` - Where volumes are stored (default: `/home/liam/docker/volumes`)

See `.env.example` for complete list.

## Deployment

### Local (Default: HTTP Mode)

The server now defaults to HTTP mode when run directly:
```bash
python -m src.server
# Starts on http://0.0.0.0:8000/mcp
# Accessible from localhost and network IPs
```

### Production (GitHub Container Registry)

The default `docker-compose.yml` uses pre-built images from GHCR:
- Image: `ghcr.io/liamgwallace/docker-assistant-claude-mcp:latest`
- Built automatically by `.github/workflows/build-and-push.yml` on push to main
- No local build required - just `docker compose up -d`

### Development (Local Build)

Use `docker-compose.dev.yml` for local development:
- Builds from local Dockerfile
- Same configuration as production
- Useful for testing changes before pushing

## Security Considerations

**Docker Socket Access**: The container mounts `/var/run/docker.sock` which provides root-equivalent access to the host. This is required for Docker management but is a security risk.

**Mitigation strategies**:
- Run only on trusted networks
- Consider using Docker Socket Proxy for production
- Container runs as root (required for Docker socket access)
- `security_opt: no-new-privileges:true` limits privilege escalation

**API Keys**: Store `ANTHROPIC_API_KEY` and `PORTAINER_TOKEN` securely in `.env` with `chmod 600 .env`

## Common Gotchas

1. **External `web` network**: Must exist before starting (`docker network create web`)
2. **Claude Code CLI**: Installed via official installer (`curl -fsSL https://claude.ai/install.sh | bash`)
3. **Authentication**: Uses ANTHROPIC_API_KEY environment variable - no interactive login needed
4. **Portainer endpoint ID**: Usually `1` but verify with `psu endpoint ls`
5. **File paths**: Paths in prompts must match mounted volumes in container
6. **Model name**: Currently hardcoded to `claude-sonnet-4-5-20250929` in environment.py
7. **Job cleanup**: Old jobs auto-delete after 24 hours to prevent disk bloat

## File Structure Conventions

```
src/
├── server.py              # FastMCP tool definitions
├── tools/
│   ├── docker_manager.py  # Tool orchestration logic
│   ├── claude_code_executor.py  # Prompt building & CLI execution
│   └── job_tracker.py     # Async job management
├── config/
│   ├── environment.py     # Settings & env vars
│   ├── system_config.yaml # System-specific configuration
│   └── docker_compose_template.yaml  # Stack template
└── utils/
    └── validators.py      # Input validation (minimal usage)

skills/
└── docker-management-skill.md  # Claude Code's Docker knowledge base

docs/                      # CLI reference documentation
└── *.md                   # Reference docs for Docker/Portainer/FastMCP
```

## Debugging

```bash
# Check Claude Code CLI is accessible
docker exec docker-mcp-server which claude
docker exec docker-mcp-server claude --version

# Test Docker socket access
docker exec docker-mcp-server docker ps

# Test Portainer connectivity
docker exec docker-mcp-server curl -f $PORTAINER_URL/api/status

# View job files
docker exec docker-mcp-server ls -la /app/data/jobs/

# Check environment
docker exec docker-mcp-server env | grep ANTHROPIC_API_KEY

# Manual prompt test (if needed)
docker exec -it docker-mcp-server claude chat --message "List all Docker containers"
```

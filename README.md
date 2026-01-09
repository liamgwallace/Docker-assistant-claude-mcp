# Docker Management MCP Server

AI-assisted Docker container management through Claude Code CLI, exposed as Model Context Protocol (MCP) tools. Manage your Docker infrastructure using natural language through FastMCP.

## Overview

This MCP server provides three powerful tools for Docker and Portainer management:

- **`docker_execute`** - Synchronous execution of Docker tasks with immediate results
- **`docker_execute_async`** - Background execution for long-running operations
- **`docker_job_status`** - Status tracking for asynchronous jobs

All tasks are executed through Claude Code CLI, which has full access to Docker CLI, Portainer CLI, and your Docker environment.

## Features

- **Natural Language Interface** - Describe what you want in plain English
- **Full Docker Management** - Deploy, update, restart, stop, and monitor containers
- **Portainer Integration** - Stack management via both `psu` and `portainer-cli`
- **Traefik Support** - Automatic reverse proxy configuration
- **Job Tracking** - Background execution with status monitoring
- **Health Checks** - Built-in container health monitoring
- **Comprehensive Context** - Claude Code has detailed knowledge of Docker best practices

## Architecture

```
┌─────────────┐
│  MCP Client │ (Claude Desktop, etc.)
└──────┬──────┘
       │ MCP Protocol
       ▼
┌─────────────────────┐
│  FastMCP Server     │
│  - docker_execute   │
│  - docker_execute_  │
│    async            │
│  - docker_job_      │
│    status           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Claude Code CLI    │
│  + Docker Skill     │
│  + System Config    │
└──────┬──────────────┘
       │
       ├──────────────────┐
       ▼                  ▼
┌─────────────┐    ┌──────────────┐
│  Docker CLI │    │ Portainer CLI│
└──────┬──────┘    └──────┬───────┘
       │                  │
       ▼                  ▼
┌────────────────────────────┐
│   Docker Daemon / Portainer│
└────────────────────────────┘
```

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2
- Portainer CE/BE (optional but recommended)
- External `web` network for Traefik (if using Traefik)
- Anthropic API key for Claude Code

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/docker-assistant-claude-mcp.git
cd docker-assistant-claude-mcp
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

**Required configuration:**

```bash
# Anthropic API Key (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Portainer Configuration (RECOMMENDED)
PORTAINER_URL=http://192.168.1.xxx:9000
PORTAINER_TOKEN=ptr_your_token_here

# File system paths
STACKS_DIR=/home/liam/docker/stacks
VOLUMES_DIR=/home/liam/docker/volumes
```

### 3. Update System Configuration (Optional)

The default configuration uses `host.docker.internal` to access services on your host machine. This works automatically on Docker Desktop and Linux with the provided `extra_hosts` configuration.

If you need to customize, edit `src/config/system_config.yaml`:

```yaml
network:
  internal_ip: "host.docker.internal"  # Access host from container
  portainer_url: "http://host.docker.internal:9000"
```

**Note:** You don't need to use specific IP addresses like `192.168.1.xxx` - `host.docker.internal` handles this automatically!

### 4. Create External Network (if needed)

If using Traefik, ensure the `web` network exists:

```bash
docker network create web
```

### 5. Deploy the MCP Server

#### Option A: Production (Pre-built Image) - RECOMMENDED

Uses the image built by GitHub Actions (fast, no build time):

```bash
# Pull the latest image (optional - compose will pull automatically)
docker pull ghcr.io/liamgwallace/docker-assistant-claude-mcp:latest

# Start the service
docker compose up -d

# View logs
docker compose logs -f

# Check health
curl http://localhost:8000/health
```

The default `docker-compose.yml` uses: `ghcr.io/liamgwallace/docker-assistant-claude-mcp:latest`

**Note:** If the image is private, authenticate first:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

#### Option B: Development (Local Build)

Build from source for testing changes:

```bash
# Build and start using dev compose file
docker compose -f docker-compose.dev.yml up -d --build

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop
docker compose -f docker-compose.dev.yml down
```

### 6. Verify Installation

```bash
# Check container is running
docker ps | grep docker-mcp-server

# Check health endpoint
docker exec docker-mcp-server curl -f http://localhost:8000/health

# View logs
docker logs docker-mcp-server
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Anthropic API key for Claude Code |
| `PORTAINER_URL` | No | `http://host.docker.internal:9000` | Portainer instance URL |
| `PORTAINER_TOKEN` | No | - | Portainer API access token |
| `PORTAINER_ENDPOINT_ID` | No | `1` | Portainer endpoint ID |
| `DOCKER_SOCKET_PATH` | No | `/var/run/docker.sock` | Docker socket path |
| `DOCKER_DEFAULT_NETWORK` | No | `web` | Default Docker network |
| `STACKS_DIR` | No | `/home/liam/docker/stacks` | Docker stacks directory |
| `VOLUMES_DIR` | No | `/home/liam/docker/volumes` | Docker volumes directory |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `MAX_JOB_AGE_HOURS` | No | `24` | Auto-cleanup old jobs after N hours |
| `JOB_CLEANUP_INTERVAL_MINUTES` | No | `60` | Job cleanup interval |

### Container-to-Host Networking

The MCP server container needs to communicate with services running on your host machine (like Portainer). We use `host.docker.internal` which is a special DNS name that resolves to the host.

**How it works:**
```yaml
# docker-compose.yml includes:
extra_hosts:
  - "host.docker.internal:host-gateway"
```

**Then use in your configuration:**
```bash
PORTAINER_URL=http://host.docker.internal:9000
```

**Alternatives (if needed):**
- Docker Desktop: `host.docker.internal` works by default
- Linux: Enabled via `extra_hosts` (already configured)
- Manual IP: You can still use `http://192.168.1.xxx:9000` if preferred

**Why NOT use `localhost`?**
`localhost` inside a container refers to the container itself, not the host machine.

### Generating Portainer API Token

1. Log in to Portainer web interface
2. Go to **Account Settings**
3. Navigate to **Access Tokens**
4. Click **Add access token**
5. Give it a description (e.g., "MCP Server")
6. Copy the token (starts with `ptr_`)
7. Add to your `.env` file

## MCP Tool Reference

### Tool 1: `docker_execute`

**Synchronous execution** - Waits for task completion and returns full output.

**Best for:**
- Quick operations (restart, stop, start)
- Status checks and health queries
- Simple deployments
- Tasks expected to complete in < 30 seconds

**Parameters:**
- `request` (string, required): Natural language request for Docker management

**Example Usage:**

```json
{
  "request": "Deploy nginx web server named 'my-nginx' exposed at mynginx.bramleyvale.com"
}
```

**Response Format:**
Returns markdown-formatted text with sections:
- Status (Success/Failed/Warning)
- Output (command outputs)
- Details (what was done)
- Access Information (URLs, commands)
- Next Steps (recommendations)

### Tool 2: `docker_execute_async`

**Asynchronous execution** - Returns immediately with job ID for background processing.

**Best for:**
- Complex multi-service deployments
- Long-running operations
- Stack updates with image pulls
- Tasks that may take > 30 seconds

**Parameters:**
- `request` (string, required): Natural language request for Docker management

**Example Usage:**

```json
{
  "request": "Deploy a complete WordPress stack with MySQL database and Redis cache"
}
```

**Response:**
Returns immediately with:
- Job ID (UUID)
- Request summary
- Instructions for checking status

### Tool 3: `docker_job_status`

**Status checking** - Check progress and results of asynchronous jobs.

**Parameters:**
- `job_id` (string, required): Job ID from `docker_execute_async`

**Example Usage:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
Returns job status:
- **pending**: Job queued but not started
- **running**: Currently executing
- **completed**: Finished successfully (includes full output)
- **failed**: Encountered error (includes error details)

## Usage Examples

### Example 1: Deploy a Web Service

**Request:**
```json
{
  "tool": "docker_execute",
  "params": {
    "request": "Deploy nginx web server named 'my-website' exposed at mywebsite.bramleyvale.com using the latest nginx image"
  }
}
```

**What happens:**
1. Claude Code generates a docker-compose.yml with Traefik labels
2. Saves compose file to `/home/liam/docker/stacks/my_website/`
3. Deploys via Portainer CLI (`psu stack deploy`)
4. Verifies deployment and health status
5. Returns access URL and management commands

### Example 2: Check Stack Health

**Request:**
```json
{
  "tool": "docker_execute",
  "params": {
    "request": "Check the health status of all running stacks and show me any containers with issues"
  }
}
```

**What happens:**
1. Lists all stacks via `psu stack ls`
2. Checks container status with `docker ps -a`
3. Inspects health checks for each container
4. Reviews recent logs for unhealthy containers
5. Returns comprehensive health report

### Example 3: Update Stack Images

**Request:**
```json
{
  "tool": "docker_execute",
  "params": {
    "request": "Update the 'my-website' stack to pull the latest images and redeploy"
  }
}
```

**What happens:**
1. Navigates to stack directory
2. Pulls latest images with `docker compose pull`
3. Redeploys stack via Portainer
4. Verifies update successful
5. Returns new container IDs and versions

### Example 4: Complex Async Deployment

**Request:**
```json
{
  "tool": "docker_execute_async",
  "params": {
    "request": "Deploy a complete monitoring stack with Prometheus, Grafana, and Node Exporter"
  }
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

**Then check status:**
```json
{
  "tool": "docker_job_status",
  "params": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Example 5: Restart Services

**Request:**
```json
{
  "tool": "docker_execute",
  "params": {
    "request": "Restart all containers in the 'my-website' stack"
  }
}
```

### Example 6: View Logs

**Request:**
```json
{
  "tool": "docker_execute",
  "params": {
    "request": "Show me the last 100 lines of logs from the 'my-website-container' container"
  }
}
```

### Example 7: Resource Usage

**Request:**
```json
{
  "tool": "docker_execute",
  "params": {
    "request": "Show me current CPU and memory usage for all running containers"
  }
}
```

## Project Structure

```
docker-management-mcp/
├── src/
│   ├── server.py                    # FastMCP server with tool definitions
│   ├── tools/
│   │   ├── docker_manager.py        # Main tool handler logic
│   │   ├── claude_code_executor.py  # Claude Code CLI wrapper
│   │   └── job_tracker.py           # Background job tracking
│   ├── config/
│   │   ├── environment.py           # Environment configuration
│   │   ├── docker_compose_template.yaml
│   │   └── system_config.yaml       # System-specific settings
│   └── utils/
│       └── validators.py            # Input validation utilities
├── docs/                            # CLI reference documentation
│   ├── portainer-cli-reference.md
│   ├── docker-cli-reference.md
│   └── fastmcp-reference.md
├── skills/                          # Context for Claude Code
│   └── docker-management-skill.md
├── data/
│   └── jobs/                        # Job status storage
├── .github/
│   └── workflows/
│       └── build-and-push.yml       # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Troubleshooting

### Issue: Container won't start

**Check logs:**
```bash
docker logs docker-mcp-server
```

**Verify environment:**
```bash
docker exec docker-mcp-server env | grep ANTHROPIC_API_KEY
```

**Check Docker socket access:**
```bash
docker exec docker-mcp-server ls -la /var/run/docker.sock
```

### Issue: Portainer connection fails

**Test connectivity:**
```bash
docker exec docker-mcp-server curl -f $PORTAINER_URL/api/status
```

**Verify token:**
```bash
docker exec docker-mcp-server curl -H "X-API-Key: $PORTAINER_TOKEN" $PORTAINER_URL/api/endpoints
```

### Issue: Claude Code CLI not found

**Check installation:**
```bash
docker exec docker-mcp-server which claude
docker exec docker-mcp-server claude --version
```

**Manually install (if needed):**
```bash
docker exec docker-mcp-server pip install anthropic-cli
```

### Issue: Network 'web' not found

**Create external network:**
```bash
docker network create web
```

**Verify it exists:**
```bash
docker network ls | grep web
```

### Issue: Permission denied on Docker socket

**Check permissions:**
```bash
ls -la /var/run/docker.sock
```

**Fix permissions:**
```bash
sudo chmod 666 /var/run/docker.sock
# OR
sudo usermod -aG docker $USER
```

### Issue: Jobs not completing

**Check job status:**
```bash
docker exec docker-mcp-server ls -la /app/data/jobs/
```

**View specific job:**
```bash
docker exec docker-mcp-server cat /app/data/jobs/{job-id}.json
```

**Check Claude Code API key:**
```bash
docker exec docker-mcp-server curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages
```

## Security Considerations

### Docker Socket Access

This container requires access to the Docker socket (`/var/run/docker.sock`) to manage containers. This provides **root-equivalent access** to the host system.

**Recommendations:**
- Run on isolated/trusted networks only
- Consider using [Docker Socket Proxy](https://github.com/Tecnativa/docker-socket-proxy) for production
- Implement network firewalls
- Regularly audit container activities

### API Keys

Store sensitive credentials securely:

```bash
# Use Docker secrets (Swarm mode)
echo "sk-ant-api03-..." | docker secret create anthropic_key -

# Use environment file with restricted permissions
chmod 600 .env
```

### Network Isolation

The MCP server should be on a trusted network:

```yaml
# Production: Use internal network only
networks:
  internal:
    internal: true
```

## Development

### Running Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export PORTAINER_URL="http://localhost:9000"

# Run server
python -m uvicorn src.server:mcp.app --reload --host 0.0.0.0 --port 8000
```

### Testing Tools

```bash
# Using curl
curl -X POST http://localhost:8000/tools/docker_execute \
  -H "Content-Type: application/json" \
  -d '{"request": "List all running containers"}'

# Using MCP Inspector
npx @modelcontextprotocol/inspector http://localhost:8000
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Powered by [Claude Code](https://github.com/anthropics/claude-code)
- Uses [Portainer Stack Utils](https://github.com/greenled/portainer-stack-utils)
- Docker management via [Portainer CLI](https://github.com/bothub-it/portainer-cli)

## Support

- Issues: [GitHub Issues](https://github.com/yourusername/docker-assistant-claude-mcp/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/docker-assistant-claude-mcp/discussions)
- Documentation: See `docs/` directory

## Roadmap

- [ ] Add support for Docker Swarm
- [ ] Implement webhook notifications
- [ ] Add Prometheus metrics export
- [ ] Create web UI for job monitoring
- [ ] Add support for custom Docker registries
- [ ] Implement backup/restore functionality
- [ ] Add stack templates library
- [ ] Create MCP client examples

---

**Note:** This is a hobby/home lab project. Use at your own risk in production environments. Always test in a safe environment first.

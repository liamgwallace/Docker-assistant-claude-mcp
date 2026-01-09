# Docker Management Skill

## Your Role
You are managing a Docker environment via Portainer CLI and direct Docker commands. You have full access to:
- **Portainer CLI** (portainer-stack-utils `psu` and portainer-cli Python package)
- **Docker CLI** with direct Docker daemon access via socket
- **File system access** to Docker stacks and volumes directories
- **System configuration** and templates

## System Overview

### Environment Details
- **Docker Socket**: `/var/run/docker.sock` (full access)
- **Stacks Directory**: `/home/liam/docker/stacks/`
- **Volumes Directory**: `/home/liam/docker/volumes/`
- **Network**: External `web` network (already created, DO NOT try to create)
- **Portainer Endpoint**: ID 1 (primary)
- **Domain Pattern**: `*.bramleyvale.com`

### Traefik Reverse Proxy
All web services use Traefik for routing with these patterns:
- Services exposed at: `{service-name}.bramleyvale.com`
- Entrypoint: `web` (HTTP)
- No direct port mappings needed for web services
- Traefik handles all routing via labels

## Naming Conventions

### CRITICAL: Follow These Conventions
1. **Container names**: lowercase-with-hyphens (e.g., `my-app-container`)
2. **Stack names**: lowercase_with_underscores (e.g., `my_app_stack`)
3. **Volume names**: `{stack_name}_{purpose}` (e.g., `my_app_data`)
4. **Service names**: lowercase-with-hyphens (e.g., `my-app-service`)

## Portainer CLI Tools

### Tool 1: portainer-stack-utils (psu)
Primary tool for stack management. Go-based CLI.

#### Authentication
Three methods (use any):

```bash
# Method 1: Command-line flags
psu --url http://portainer:9000 --user admin --password mypass --endpoint 1 stack ls

# Method 2: Environment variables (PREFERRED)
export PORTAINER_URL="http://portainer:9000"
export PORTAINER_TOKEN="ptr_your_token_here"
export PORTAINER_ENDPOINT="1"
psu stack ls

# Method 3: Config file ~/.psu.yaml
# url: http://portainer:9000
# token: ptr_your_token_here
# endpoint: 1
```

#### Key Commands

**Deploy or Update Stack:**
```bash
# Deploy new or update existing stack
psu stack deploy {stack_name} \
  --stack-file docker-compose.yml \
  --endpoint 1

# With environment variables
psu stack deploy {stack_name} \
  --stack-file docker-compose.yml \
  --env-file .env \
  --endpoint 1
```

**List Stacks:**
```bash
# List all stacks
psu stack ls --endpoint 1

# Custom format
psu stack ls --format "{{ .Name }}: {{ .Status }}" --endpoint 1
```

**Show Stack Services:**
```bash
# Show services in a stack
psu stack ps {stack_name} --endpoint 1
```

**Remove Stack:**
```bash
# Remove a stack
psu stack rm {stack_name} --endpoint 1
```

**List Endpoints:**
```bash
# List all Portainer endpoints
psu endpoint ls
```

### Tool 2: portainer-cli (Python)
Alternative Python-based CLI for stack operations.

#### Installation & Setup
```bash
# Already installed via pip
# Config file: ~/.portainer-cli.json or .portainer-cli.json
```

#### Key Commands

**Create Stack:**
```bash
portainer-cli create_stack \
  -n {stack_name} \
  -e 1 \
  -sf docker-compose.yml \
  -env "KEY=value"
```

**Update Stack:**
```bash
# Get stack ID first
STACK_ID=$(portainer-cli get_stack_id -n {stack_name} -e 1)

# Update the stack
portainer-cli update_stack \
  -s $STACK_ID \
  -e 1 \
  -sf docker-compose.yml
```

**Create or Update (Upsert):**
```bash
portainer-cli create_or_update_stack \
  -n {stack_name} \
  -e 1 \
  -sf docker-compose.yml
```

## Docker CLI Commands

### Container Management

**List Containers:**
```bash
# All running containers
docker ps

# All containers (including stopped)
docker ps -a

# Filter by name
docker ps --filter "name=my-app"

# Custom format
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Container Lifecycle:**
```bash
# Start container
docker start {container_name}

# Stop container (graceful, 10s timeout)
docker stop {container_name}

# Stop with custom timeout
docker stop -t 30 {container_name}

# Restart container
docker restart {container_name}

# Kill container (immediate)
docker kill {container_name}

# Remove container
docker rm {container_name}

# Remove with force
docker rm -f {container_name}
```

**Container Inspection:**
```bash
# Full container details (JSON)
docker inspect {container_name}

# Get specific field
docker inspect --format='{{.State.Health.Status}}' {container_name}

# Get IP address
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' {container_name}

# Check health status
docker inspect --format='{{.State.Health.Status}}' {container_name}
```

**Container Logs:**
```bash
# Recent logs (last 100 lines)
docker logs {container_name} --tail 100

# Follow logs (real-time)
docker logs {container_name} -f

# Logs with timestamps
docker logs {container_name} --timestamps

# Logs since specific time
docker logs {container_name} --since 30m
docker logs {container_name} --since 2024-01-01T00:00:00
```

**Container Statistics:**
```bash
# Live stats (continuous)
docker stats {container_name}

# One-time stats snapshot
docker stats {container_name} --no-stream

# All containers
docker stats --no-stream

# Custom format
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

**Container Processes:**
```bash
# List processes in container
docker top {container_name}

# With custom ps format
docker top {container_name} aux
```

### Docker Compose Commands

**Stack Deployment:**
```bash
# Navigate to stack directory first
cd /home/liam/docker/stacks/{stack_name}/

# Start stack (detached)
docker compose up -d

# Start with build
docker compose up -d --build

# Start with pull
docker compose up -d --pull always

# Scale services
docker compose up -d --scale web=3
```

**Stack Management:**
```bash
# Stop stack (keeps containers)
docker compose stop

# Start stopped stack
docker compose start

# Restart stack
docker compose restart

# Pause stack
docker compose pause

# Unpause stack
docker compose unpause

# Stop and remove stack
docker compose down

# Down with volumes
docker compose down -v

# Down with images
docker compose down --rmi all
```

**Stack Information:**
```bash
# List services
docker compose ps

# List all (including stopped)
docker compose ps -a

# View logs
docker compose logs

# Follow logs
docker compose logs -f

# Logs for specific service
docker compose logs {service_name}

# View configuration
docker compose config

# Validate configuration
docker compose config --quiet
```

**Image Management:**
```bash
# Pull images
docker compose pull

# Pull specific service
docker compose pull {service_name}

# Build images
docker compose build

# Build without cache
docker compose build --no-cache
```

### Image Management

**List Images:**
```bash
# All images
docker images

# Filter by name
docker images nginx

# Dangling images
docker images --filter "dangling=true"

# Custom format
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

**Pull Images:**
```bash
# Pull latest
docker pull nginx:latest

# Pull specific tag
docker pull postgres:15-alpine

# Pull by digest
docker pull nginx@sha256:abc123...
```

**Remove Images:**
```bash
# Remove specific image
docker rmi nginx:latest

# Remove with force
docker rmi -f nginx:latest

# Remove multiple
docker rmi nginx:latest postgres:15

# Remove dangling images
docker image prune

# Remove all unused images
docker image prune -a

# Remove with filter
docker image prune -a --filter "until=24h"
```

### Network Management

**List Networks:**
```bash
# All networks
docker network ls

# Filter by driver
docker network ls --filter driver=bridge

# Custom format
docker network ls --format "{{.Name}}: {{.Driver}}"
```

**Inspect Network:**
```bash
# Network details
docker network inspect web

# Get subnet
docker network inspect --format='{{range .IPAM.Config}}{{.Subnet}}{{end}}' web

# List connected containers
docker network inspect --format='{{range $k, $v := .Containers}}{{$v.Name}} {{end}}' web
```

**Network Operations:**
```bash
# Create network (NOT NEEDED - 'web' exists)
docker network create my_network

# Connect container to network
docker network connect web {container_name}

# Disconnect from network
docker network disconnect web {container_name}

# Remove network
docker network rm {network_name}

# Remove unused networks
docker network prune
```

### Volume Management

**List Volumes:**
```bash
# All volumes
docker volume ls

# Dangling volumes
docker volume ls --filter dangling=true

# Filter by name
docker volume ls --filter name=my_app
```

**Inspect Volume:**
```bash
# Volume details
docker volume inspect {volume_name}

# Get mount point
docker volume inspect --format='{{.Mountpoint}}' {volume_name}
```

**Volume Operations:**
```bash
# Create volume
docker volume create {volume_name}

# Create with driver options
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.1,rw \
  --opt device=:/path/to/dir \
  {volume_name}

# Remove volume
docker volume rm {volume_name}

# Remove unused volumes (CAREFUL!)
docker volume prune

# Remove with filter
docker volume prune --filter "label!=keep"
```

### Health Checks

**Check Container Health:**
```bash
# Health status
docker inspect --format='{{.State.Health.Status}}' {container_name}

# Full health info
docker inspect --format='{{json .State.Health}}' {container_name} | jq

# Health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' {container_name}
```

**Define Health Check in Compose:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:80/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

## Common Task Workflows

### Task 1: Deploy New Stack

**Steps:**
1. Create stack directory
2. Generate docker-compose.yml
3. Apply configuration
4. Deploy via Portainer
5. Verify deployment

**Example:**
```bash
# 1. Create directory
mkdir -p /home/liam/docker/stacks/my_app
cd /home/liam/docker/stacks/my_app

# 2. Create docker-compose.yml
cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  my-app:
    image: nginx:latest
    container_name: my-app-container
    restart: unless-stopped
    networks:
      - web
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`myapp.bramleyvale.com`)"
      - "traefik.http.routers.myapp.entrypoints=web"
      - "traefik.http.services.myapp.loadbalancer.server.port=80"
    volumes:
      - my_app_data:/usr/share/nginx/html
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  web:
    external: true

volumes:
  my_app_data:
EOF

# 3. Deploy via Portainer
psu stack deploy my_app --stack-file docker-compose.yml --endpoint 1

# 4. Verify
docker ps --filter "name=my-app"
docker logs my-app-container --tail 50
```

### Task 2: Check Stack Health

**Steps:**
1. List all stacks
2. Check container status
3. Check health checks
4. Review logs if issues

**Example:**
```bash
# 1. List stacks
psu stack ls --endpoint 1

# 2. Check containers
docker ps -a --filter "name=my-app"

# 3. Check health
docker inspect --format='{{.State.Health.Status}}' my-app-container

# 4. Check logs if needed
docker logs my-app-container --tail 100

# 5. Check stats
docker stats my-app-container --no-stream
```

### Task 3: Update Stack with New Image

**Steps:**
1. Navigate to stack directory
2. Update image tag if needed
3. Pull new images
4. Redeploy stack
5. Verify update

**Example:**
```bash
# 1. Navigate to stack
cd /home/liam/docker/stacks/my_app

# 2. Pull latest images
docker compose pull

# 3. Redeploy via Portainer
psu stack deploy my_app --stack-file docker-compose.yml --endpoint 1

# OR use docker compose
docker compose up -d --pull always

# 4. Verify
docker ps --filter "name=my-app"
docker logs my-app-container --tail 20
```

### Task 4: Restart Services

**Single Container:**
```bash
docker restart my-app-container
```

**All Containers in Stack:**
```bash
cd /home/liam/docker/stacks/my_app
docker compose restart
```

**Full Recreation:**
```bash
cd /home/liam/docker/stacks/my_app
docker compose down
docker compose up -d
```

### Task 5: Stop/Start Services

**Stop:**
```bash
# Single container
docker stop my-app-container

# Stack
cd /home/liam/docker/stacks/my_app
docker compose stop
```

**Start:**
```bash
# Single container
docker start my-app-container

# Stack
cd /home/liam/docker/stacks/my_app
docker compose start
```

### Task 6: View Logs

**Recent Logs:**
```bash
docker logs my-app-container --tail 100
```

**Follow Logs:**
```bash
docker logs my-app-container -f
```

**Stack Logs:**
```bash
cd /home/liam/docker/stacks/my_app
docker compose logs -f
```

**Service-Specific Logs:**
```bash
cd /home/liam/docker/stacks/my_app
docker compose logs -f my-app
```

### Task 7: Check Resource Usage

**Single Container:**
```bash
docker stats my-app-container --no-stream
```

**All Containers:**
```bash
docker stats --no-stream
```

**Continuous Monitoring:**
```bash
docker stats
```

### Task 8: Remove Stack

**Via Portainer:**
```bash
psu stack rm my_app --endpoint 1
```

**Via Docker Compose:**
```bash
cd /home/liam/docker/stacks/my_app
docker compose down

# With volumes
docker compose down -v
```

**Clean Up:**
```bash
# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Remove unused images
docker image prune -a
```

## Docker Compose Template

Use this template when creating new stacks:

```yaml
version: '3.8'

services:
  service-name:
    image: image:tag
    container_name: service-name-container
    restart: unless-stopped
    networks:
      - web

    # Traefik labels (if web service)
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.servicename.rule=Host(`servicename.bramleyvale.com`)"
      - "traefik.http.routers.servicename.entrypoints=web"
      - "traefik.http.services.servicename.loadbalancer.server.port=80"

    # Environment variables
    environment:
      - ENV_VAR=value

    # Volumes
    volumes:
      - service_data:/data
      - /home/liam/docker/volumes/service:/config

    # Ports (ONLY if not using Traefik)
    # ports:
    #   - "8080:80"

    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

networks:
  web:
    external: true

volumes:
  service_data:
    driver: local
```

## Response Format

**ALWAYS** structure your responses in markdown with these sections:

### Status Section
```markdown
## Status: Success ✓
# OR
## Status: Failed ❌
# OR
## Status: Warning ⚠️
```

### Output Section
```markdown
### Output
\```
[Command outputs here]
\```
```

### Details Section
```markdown
### Details
- What was done
- Configuration applied
- Files created/modified
- Services affected
```

### Access Information (if applicable)
```markdown
### Access Information
- URL: http://servicename.bramleyvale.com
- Container: service-name-container
- Logs: `docker logs service-name-container`
```

### Next Steps (if applicable)
```markdown
### Next Steps
- Recommendations
- Additional actions needed
- Monitoring suggestions
```

## Example Response

```markdown
## Status: Success ✓

### Output
\```
Stack deployed successfully
Container my-app-container is running
Health check: healthy
\```

### Details
Created stack `my_app` with the following configuration:
- **Service**: my-app-container
- **Image**: nginx:latest
- **Network**: web (external)
- **Traefik Routing**: myapp.bramleyvale.com
- **Health Check**: Enabled (30s interval)
- **Volume**: my_app_data mounted to /usr/share/nginx/html

### Access Information
- **URL**: http://myapp.bramleyvale.com
- **Container Logs**: `docker logs my-app-container`
- **Stats**: `docker stats my-app-container --no-stream`

### Next Steps
- Monitor container health: `docker inspect --format='{{.State.Health.Status}}' my-app-container`
- View logs: `docker logs my-app-container -f`
- Update content in: `/home/liam/docker/volumes/my_app/`
```

## Important Rules

1. **ALWAYS** use the external `web` network - DO NOT create it
2. **ALWAYS** check for port conflicts before assigning ports
3. **ALWAYS** follow naming conventions strictly
4. **ALWAYS** include health checks for web services
5. **ALWAYS** save compose files before deploying
6. **NEVER** use direct `docker run` - always use compose files and Portainer
7. **NEVER** try to create the `web` network
8. **NEVER** expose ports for Traefik-enabled services
9. **ALWAYS** provide clear, structured responses in markdown
10. **ALWAYS** include error messages and troubleshooting steps if failures occur

## Troubleshooting

### Stack Deployment Fails
```bash
# Check Portainer connectivity
psu endpoint ls

# Validate compose file
docker compose config --quiet

# Check for port conflicts
docker ps --format "{{.Ports}}"

# Check network exists
docker network inspect web
```

### Container Won't Start
```bash
# Check logs
docker logs {container_name}

# Check events
docker events --since 5m

# Inspect container
docker inspect {container_name}

# Check resource usage
docker stats --no-stream
```

### Health Check Failing
```bash
# Check health status
docker inspect --format='{{json .State.Health}}' {container_name} | jq

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' {container_name}

# Test health check manually
docker exec {container_name} curl -f http://localhost/health
```

### Network Issues
```bash
# Inspect network
docker network inspect web

# Check container network
docker inspect --format='{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' {container_name}

# Reconnect to network
docker network disconnect web {container_name}
docker network connect web {container_name}
```

## Best Practices

1. **Always validate** compose files before deploying
2. **Always test** health check commands
3. **Always backup** data volumes before major changes
4. **Monitor logs** after deployment
5. **Use named volumes** for persistent data
6. **Pin image versions** for production (not `:latest`)
7. **Include resource limits** for production services
8. **Document** custom configurations in compose files
9. **Clean up** unused resources regularly
10. **Test locally** when possible before deploying

---

**Remember**: You have full Docker and Portainer CLI access. Execute commands directly and provide clear, actionable responses. Structure all output in markdown format with status, output, details, and next steps.

# Docker CLI Reference Guide

A comprehensive reference for Docker CLI commands covering container management, Docker Compose, images, networks, and volumes.

## Table of Contents

1. [Container Management](#container-management)
2. [Docker Compose Commands](#docker-compose-commands)
3. [Image Management](#image-management)
4. [Network Management](#network-management)
5. [Volume Management](#volume-management)
6. [Best Practices](#best-practices)

---

## Container Management

### docker ps

List running containers.

**Syntax:**
```bash
docker ps [OPTIONS]
```

**Common Options:**
- `-a, --all` - Show all containers (default shows just running)
- `-q, --quiet` - Only display container IDs
- `-s, --size` - Display total file sizes
- `-n, --last` - Show n last created containers (includes all states)
- `--filter` - Filter output based on conditions
- `--format` - Format output using a Go template
- `--no-trunc` - Don't truncate output

**Examples:**

```bash
# List all running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List container IDs only
docker ps -q

# List containers with size information
docker ps -s

# List last 5 created containers
docker ps -n 5

# Filter containers by status
docker ps --filter "status=exited"

# Filter by name
docker ps --filter "name=web"

# Custom format output
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
```

**Output Example:**
```
CONTAINER ID   IMAGE          COMMAND                  CREATED        STATUS        PORTS                    NAMES
a1b2c3d4e5f6   nginx:latest   "/docker-entrypoint.…"   2 hours ago    Up 2 hours    0.0.0.0:8080->80/tcp     webserver
b2c3d4e5f6g7   postgres:14    "docker-entrypoint.s…"   3 hours ago    Up 3 hours    5432/tcp                 database
```

---

### docker inspect

Return low-level information on Docker objects (containers, images, volumes, networks).

**Syntax:**
```bash
docker inspect [OPTIONS] NAME|ID [NAME|ID...]
```

**Common Options:**
- `-f, --format` - Format output using a Go template
- `-s, --size` - Display total file sizes (containers only)
- `--type` - Return JSON for specified type

**Examples:**

```bash
# Inspect a container
docker inspect my-container

# Get specific information using format
docker inspect --format='{{.State.Status}}' my-container

# Get IP address
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' my-container

# Get container environment variables
docker inspect --format='{{.Config.Env}}' my-container

# Check health status
docker inspect --format='{{json .State.Health}}' my-container

# Get multiple containers' info
docker inspect container1 container2

# Inspect with size information
docker inspect --size my-container
```

**Output Example (JSON):**
```json
[
    {
        "Id": "a1b2c3d4e5f6...",
        "Created": "2026-01-08T10:30:00.000000000Z",
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "Health": {
                "Status": "healthy",
                "FailingStreak": 0,
                "Log": [...]
            }
        },
        "Config": {
            "Hostname": "a1b2c3d4e5f6",
            "Env": ["PATH=/usr/local/bin:/usr/bin"],
            "Image": "nginx:latest"
        },
        "NetworkSettings": {
            "IPAddress": "172.17.0.2"
        }
    }
]
```

---

### docker logs

Fetch the logs of a container.

**Syntax:**
```bash
docker logs [OPTIONS] CONTAINER
```

**Common Options:**
- `-f, --follow` - Follow log output (live stream)
- `-t, --timestamps` - Show timestamps (RFC3339Nano format)
- `--tail` - Number of lines to show from the end of logs
- `--since` - Show logs since timestamp or relative (e.g., 2h30m)
- `--until` - Show logs before a timestamp
- `--details` - Show extra details provided to logs

**Examples:**

```bash
# View logs
docker logs my-container

# Follow logs in real-time
docker logs -f my-container

# Show timestamps
docker logs -t my-container

# Show last 100 lines
docker logs --tail 100 my-container

# Show logs from last 2 hours
docker logs --since 2h my-container

# Show logs since specific time
docker logs --since 2026-01-08T10:00:00 my-container

# Combine options
docker logs -f --tail 50 --timestamps my-container

# Show logs with extra details
docker logs --details my-container
```

**Output Example:**
```
2026-01-08T10:30:45.123456789Z 192.168.1.1 - - [08/Jan/2026:10:30:45 +0000] "GET / HTTP/1.1" 200 612
2026-01-08T10:30:46.234567890Z 192.168.1.2 - - [08/Jan/2026:10:30:46 +0000] "GET /api HTTP/1.1" 200 1024
```

**Important Notes:**
- Only works with `json-file` or `journald` logging drivers
- Shows STDOUT and STDERR by default
- Negative numbers or non-integers for `--tail` default to "all"

---

### docker start

Start one or more stopped containers.

**Syntax:**
```bash
docker start [OPTIONS] CONTAINER [CONTAINER...]
```

**Common Options:**
- `-a, --attach` - Attach STDOUT/STDERR and forward signals
- `-i, --interactive` - Attach container's STDIN
- `--detach-keys` - Override key sequence for detaching

**Examples:**

```bash
# Start a container
docker start my-container

# Start multiple containers
docker start container1 container2 container3

# Start and attach to container
docker start -a my-container

# Start interactively
docker start -ai my-container

# Start all stopped containers
docker start $(docker ps -aq)
```

---

### docker stop

Stop one or more running containers.

**Syntax:**
```bash
docker stop [OPTIONS] CONTAINER [CONTAINER...]
```

**Common Options:**
- `-t, --time` - Seconds to wait before killing the container (default 10)

**Examples:**

```bash
# Stop a container
docker stop my-container

# Stop multiple containers
docker stop container1 container2 container3

# Stop with custom timeout (30 seconds)
docker stop -t 30 my-container

# Stop all running containers
docker stop $(docker ps -q)
```

**Process:**
1. Sends SIGTERM signal
2. Waits for specified timeout
3. Sends SIGKILL if still running

---

### docker restart

Restart one or more containers.

**Syntax:**
```bash
docker restart [OPTIONS] CONTAINER [CONTAINER...]
```

**Common Options:**
- `-t, --time` - Seconds to wait before killing the container (default 10)

**Examples:**

```bash
# Restart a container
docker restart my-container

# Restart multiple containers
docker restart container1 container2

# Restart with custom timeout
docker restart -t 30 my-container

# Restart all containers
docker restart $(docker ps -aq)
```

---

### docker stats

Display a live stream of container resource usage statistics.

**Syntax:**
```bash
docker stats [OPTIONS] [CONTAINER...]
```

**Common Options:**
- `-a, --all` - Show all containers (default shows just running)
- `--no-stream` - Disable streaming stats and only pull the first result
- `--no-trunc` - Do not truncate output
- `--format` - Format output using a Go template

**Examples:**

```bash
# Show stats for all running containers
docker stats

# Show stats for specific containers
docker stats my-container another-container

# Show stats for all containers (including stopped)
docker stats -a

# Get one-time stats (no streaming)
docker stats --no-stream

# Custom format
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

**Output Example:**
```
CONTAINER ID   NAME          CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O       PIDS
a1b2c3d4e5f6   webserver     0.50%     100MiB / 2GiB         4.88%     1.2MB / 800kB     10MB / 2MB      5
b2c3d4e5f6g7   database      1.20%     500MiB / 2GiB        24.41%     800kB / 1.5MB     50MB / 10MB     20
```

**Metrics Displayed:**
- CPU % - Percentage of host CPU used
- MEM USAGE / LIMIT - Current memory usage and limit
- MEM % - Percentage of available memory used
- NET I/O - Network input/output
- BLOCK I/O - Disk read/write
- PIDS - Number of processes

---

### docker top

Display the running processes of a container.

**Syntax:**
```bash
docker top CONTAINER [ps OPTIONS]
```

**Examples:**

```bash
# Show processes in container
docker top my-container

# Show processes with custom ps options
docker top my-container aux

# Show specific columns
docker top my-container -eo pid,comm
```

**Output Example:**
```
UID     PID      PPID     C    STIME   TTY   TIME       CMD
root    1234     1220     0    10:30   ?     00:00:01   nginx: master process
nginx   1235     1234     0    10:30   ?     00:00:00   nginx: worker process
```

---

### Health Check Commands

Health checks monitor container health and report status.

**Check Health Status:**

```bash
# View health status in docker ps
docker ps --filter "health=healthy"
docker ps --filter "health=unhealthy"
docker ps --filter "health=starting"

# Get detailed health information
docker inspect --format='{{json .State.Health}}' my-container

# Pretty print health status
docker inspect --format='{{.State.Health.Status}}' my-container
```

**Dockerfile HEALTHCHECK Example:**
```dockerfile
# HTTP endpoint check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# TCP port check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD nc -z localhost 8080 || exit 1

# Custom script check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD /app/health-check.sh
```

**Health States:**
- `starting` - Container is starting up (within start-period)
- `healthy` - Health check passed
- `unhealthy` - Health check failed (reached max retries)

**docker-compose.yml HEALTHCHECK Example:**
```yaml
services:
  web:
    image: nginx
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Best Practices:**
- Set appropriate `--interval` to avoid excessive checks
- Use `--start-period` for applications with slow startup
- Keep health check commands lightweight
- Return exit code 0 for healthy, 1 for unhealthy
- Monitor the last 5 health checks via `docker inspect`

---

## Docker Compose Commands

Docker Compose simplifies managing multi-container applications using YAML configuration files.

### docker compose up

Create and start containers defined in compose file.

**Syntax:**
```bash
docker compose up [OPTIONS] [SERVICE...]
```

**Common Options:**
- `-d, --detach` - Detached mode: run in background
- `--build` - Build images before starting containers
- `--force-recreate` - Recreate containers even if config hasn't changed
- `--no-deps` - Don't start linked services
- `--no-build` - Don't build images, even if missing
- `--remove-orphans` - Remove containers for services not in compose file
- `--scale` - Scale SERVICE to NUM instances
- `-f, --file` - Specify alternate compose file
- `--dry-run` - Test command without changing state

**Examples:**

```bash
# Start all services
docker compose up

# Start in detached mode
docker compose up -d

# Start specific services
docker compose up web database

# Build and start
docker compose up --build

# Start with custom file
docker compose -f docker-compose.prod.yml up -d

# Scale service to multiple instances
docker compose up --scale web=3

# Force recreate all containers
docker compose up --force-recreate

# Remove orphaned containers
docker compose up --remove-orphans

# Dry run to test configuration
docker compose up --dry-run
```

**Sample compose.yaml:**
```yaml
services:
  web:
    build: .
    ports:
      - "8000:5000"
    depends_on:
      - redis
  redis:
    image: "redis:alpine"
```

---

### docker compose down

Stop and remove containers, networks, volumes, and images created by `up`.

**Syntax:**
```bash
docker compose down [OPTIONS]
```

**Common Options:**
- `--volumes` - Remove named volumes and anonymous volumes
- `--remove-orphans` - Remove containers for services not in compose file
- `--rmi` - Remove images (type: 'all' or 'local')
- `-t, --timeout` - Shutdown timeout in seconds

**Examples:**

```bash
# Stop and remove containers and networks
docker compose down

# Remove containers, networks, and volumes
docker compose down --volumes

# Remove containers, networks, and all images
docker compose down --rmi all

# Remove only locally built images
docker compose down --rmi local

# Custom timeout
docker compose down -t 30

# Remove orphaned containers
docker compose down --remove-orphans
```

---

### docker compose ps

List containers for services in compose file.

**Syntax:**
```bash
docker compose ps [OPTIONS] [SERVICE...]
```

**Common Options:**
- `-a, --all` - Show all containers (including stopped)
- `-q, --quiet` - Only display IDs
- `--services` - Display services
- `--filter` - Filter services by property
- `--format` - Format output

**Examples:**

```bash
# List running service containers
docker compose ps

# List all containers including stopped
docker compose ps -a

# List only container IDs
docker compose ps -q

# List service names
docker compose ps --services

# Filter by status
docker compose ps --filter "status=running"

# Custom format
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

**Output Example:**
```
NAME                COMMAND                  SERVICE    STATUS         PORTS
myapp-web-1         "python app.py"          web        Up 2 hours     0.0.0.0:8000->5000/tcp
myapp-redis-1       "redis-server"           redis      Up 2 hours     6379/tcp
```

---

### docker compose logs

View output from containers.

**Syntax:**
```bash
docker compose logs [OPTIONS] [SERVICE...]
```

**Common Options:**
- `-f, --follow` - Follow log output
- `-t, --timestamps` - Show timestamps
- `--tail` - Number of lines to show from the end
- `--since` - Show logs since timestamp
- `--no-color` - Produce monochrome output

**Examples:**

```bash
# View logs from all services
docker compose logs

# View logs from specific service
docker compose logs web

# Follow logs in real-time
docker compose logs -f

# Show timestamps
docker compose logs -t

# Show last 100 lines
docker compose logs --tail=100

# Show logs from last hour
docker compose logs --since 1h

# Combine options for specific service
docker compose logs -f --tail=50 web
```

**Output Example:**
```
web-1    | 2026-01-08 10:30:45 [INFO] Starting server on port 5000
redis-1  | 2026-01-08 10:30:45 * Ready to accept connections
web-1    | 2026-01-08 10:30:46 [INFO] Connected to database
```

---

### docker compose pull

Pull service images from registry.

**Syntax:**
```bash
docker compose pull [OPTIONS] [SERVICE...]
```

**Common Options:**
- `-q, --quiet` - Pull without printing progress
- `--ignore-pull-failures` - Pull what it can and ignore failures
- `--include-deps` - Also pull images of services declared as dependencies

**Examples:**

```bash
# Pull all service images
docker compose pull

# Pull specific service image
docker compose pull web

# Pull quietly
docker compose pull -q

# Pull with dependencies
docker compose pull --include-deps web

# Ignore failures
docker compose pull --ignore-pull-failures
```

---

### docker compose restart

Restart service containers.

**Syntax:**
```bash
docker compose restart [OPTIONS] [SERVICE...]
```

**Common Options:**
- `-t, --timeout` - Shutdown timeout in seconds

**Examples:**

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart web

# Restart with custom timeout
docker compose restart -t 30 web

# Restart multiple services
docker compose restart web database
```

---

### Stack Management

Managing complete application stacks with Docker Compose.

**Common Workflows:**

```bash
# Complete deployment workflow
docker compose pull                    # Pull latest images
docker compose build                   # Build custom images
docker compose up -d                   # Start stack in background
docker compose ps                      # Verify services running

# Update and restart workflow
docker compose pull                    # Get latest images
docker compose up -d --force-recreate  # Recreate with new images
docker compose ps                      # Verify update

# Scaling services
docker compose up -d --scale web=3     # Scale web service to 3 instances
docker compose ps                      # Verify scaled instances

# Health monitoring
docker compose ps                      # Check service status
docker compose logs -f                 # Monitor logs
docker compose top                     # View running processes

# Cleanup
docker compose down                    # Stop and remove containers
docker compose down --volumes          # Also remove volumes
docker compose down --rmi all          # Remove everything including images
```

**Environment-Specific Deployments:**

```bash
# Development
docker compose -f docker-compose.yml up -d

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Testing
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

**Override Files:**
```bash
# docker-compose.override.yml is automatically loaded
docker compose up -d

# Multiple compose files
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
```

---

## Image Management

### docker pull

Pull an image or repository from a registry.

**Syntax:**
```bash
docker pull [OPTIONS] NAME[:TAG|@DIGEST]
```

**Common Options:**
- `-a, --all-tags` - Download all tagged images in the repository
- `--platform` - Set platform if server is multi-platform capable
- `-q, --quiet` - Suppress verbose output
- `--disable-content-trust` - Skip image verification (default true)

**Examples:**

```bash
# Pull latest version
docker pull nginx

# Pull specific tag
docker pull nginx:1.24

# Pull specific version
docker pull nginx:1.24.0-alpine

# Pull by digest
docker pull nginx@sha256:abc123...

# Pull all tags
docker pull -a nginx

# Pull for specific platform
docker pull --platform linux/amd64 nginx

# Pull from custom registry
docker pull myregistry.com:5000/myapp:latest

# Pull quietly
docker pull -q nginx
```

**Output Example:**
```
Using default tag: latest
latest: Pulling from library/nginx
a2abf6c4d29d: Pull complete
a9edb18cadd1: Pull complete
589b7251471a: Pull complete
Digest: sha256:abc123def456...
Status: Downloaded newer image for nginx:latest
docker.io/library/nginx:latest
```

---

### docker images

List images.

**Syntax:**
```bash
docker images [OPTIONS] [REPOSITORY[:TAG]]
```

**Common Options:**
- `-a, --all` - Show all images (including intermediate)
- `-q, --quiet` - Only show image IDs
- `--digests` - Show digests
- `--filter` - Filter output based on conditions
- `--format` - Format output using template
- `--no-trunc` - Don't truncate output

**Examples:**

```bash
# List all images
docker images

# List images with digests
docker images --digests

# List all images including intermediates
docker images -a

# List only image IDs
docker images -q

# Filter by reference
docker images nginx

# Filter by dangling images
docker images --filter "dangling=true"

# Filter by label
docker images --filter "label=maintainer=nginx"

# Filter by before/since
docker images --filter "before=nginx:latest"

# Custom format
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# List with full information
docker images --no-trunc
```

**Output Example:**
```
REPOSITORY    TAG         IMAGE ID       CREATED        SIZE
nginx         latest      a1b2c3d4e5f6   2 weeks ago    142MB
postgres      14          b2c3d4e5f6g7   3 weeks ago    376MB
redis         alpine      c3d4e5f6g7h8   1 month ago    32.3MB
```

---

### docker rmi

Remove one or more images.

**Syntax:**
```bash
docker rmi [OPTIONS] IMAGE [IMAGE...]
```

**Common Options:**
- `-f, --force` - Force removal of the image
- `--no-prune` - Do not delete untagged parent images

**Examples:**

```bash
# Remove an image
docker rmi nginx

# Remove by image ID
docker rmi a1b2c3d4e5f6

# Remove multiple images
docker rmi nginx redis postgres

# Force remove (even if used by stopped containers)
docker rmi -f nginx

# Remove image without deleting untagged parents
docker rmi --no-prune nginx

# Remove all images
docker rmi $(docker images -q)

# Remove dangling images
docker rmi $(docker images -f "dangling=true" -q)

# Remove images by pattern
docker images | grep "myapp" | awk '{print $3}' | xargs docker rmi
```

**Output Example:**
```
Untagged: nginx:latest
Untagged: nginx@sha256:abc123...
Deleted: sha256:a1b2c3d4e5f6...
Deleted: sha256:b2c3d4e5f6g7...
```

**Important Notes:**
- Cannot remove image if used by existing containers (unless forced)
- Force flag bypasses checks but may leave orphaned containers
- By default, removes untagged parent images (dangling images)

---

### docker image prune

Remove unused images.

**Syntax:**
```bash
docker image prune [OPTIONS]
```

**Common Options:**
- `-a, --all` - Remove all unused images, not just dangling ones
- `-f, --force` - Do not prompt for confirmation
- `--filter` - Provide filter values (e.g., 'until=<timestamp>')

**Examples:**

```bash
# Remove dangling images (interactive)
docker image prune

# Remove all unused images
docker image prune -a

# Remove without confirmation
docker image prune -f

# Remove images older than 24 hours
docker image prune -a --filter "until=24h"

# Remove with label filter
docker image prune --filter "label=deprecated"

# Combine filters
docker image prune -a --filter "until=168h" --filter "label!=keep"
```

**Output Example:**
```
WARNING! This will remove all dangling images.
Are you sure you want to continue? [y/N] y
Deleted Images:
deleted: sha256:abc123...
deleted: sha256:def456...

Total reclaimed space: 1.2GB
```

**Dangling vs Unused:**
- **Dangling images**: Untagged images (layers with no relationship to tagged images)
- **Unused images**: Images not referenced by any container

---

## Network Management

### docker network ls

List networks.

**Syntax:**
```bash
docker network ls [OPTIONS]
```

**Common Options:**
- `-q, --quiet` - Only display network IDs
- `-f, --filter` - Filter output based on conditions
- `--format` - Format output using template
- `--no-trunc` - Do not truncate output

**Examples:**

```bash
# List all networks
docker network ls

# List only network IDs
docker network ls -q

# Filter by driver
docker network ls --filter driver=bridge

# Filter by name
docker network ls --filter name=my-network

# Filter by type
docker network ls --filter type=custom

# Custom format
docker network ls --format "table {{.ID}}\t{{.Name}}\t{{.Driver}}"

# Show full network IDs
docker network ls --no-trunc
```

**Output Example:**
```
NETWORK ID          NAME                DRIVER              SCOPE
a1b2c3d4e5f6        bridge              bridge              local
b2c3d4e5f6g7        host                host                local
c3d4e5f6g7h8        none                null                local
d4e5f6g7h8i9        my-network          bridge              local
```

**Default Networks:**
- **bridge**: Default network for containers
- **host**: Container uses host network stack
- **none**: Container has no network access

---

### docker network inspect

Display detailed information on one or more networks.

**Syntax:**
```bash
docker network inspect [OPTIONS] NETWORK [NETWORK...]
```

**Common Options:**
- `-f, --format` - Format output using template
- `-v, --verbose` - Verbose output for diagnostics

**Examples:**

```bash
# Inspect a network
docker network inspect my-network

# Get specific information
docker network inspect --format='{{.Driver}}' my-network

# Get subnet information
docker network inspect --format='{{range .IPAM.Config}}{{.Subnet}}{{end}}' my-network

# Get gateway
docker network inspect --format='{{range .IPAM.Config}}{{.Gateway}}{{end}}' my-network

# List connected containers
docker network inspect --format='{{range $k,$v := .Containers}}{{$v.Name}} {{end}}' my-network

# Inspect multiple networks
docker network inspect bridge host
```

**Output Example (JSON):**
```json
[
    {
        "Name": "my-network",
        "Id": "d4e5f6g7h8i9...",
        "Created": "2026-01-08T10:00:00.000000000Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Config": [
                {
                    "Subnet": "172.18.0.0/16",
                    "Gateway": "172.18.0.1"
                }
            ]
        },
        "Containers": {
            "a1b2c3d4e5f6": {
                "Name": "web-1",
                "EndpointID": "abc123...",
                "MacAddress": "02:42:ac:12:00:02",
                "IPv4Address": "172.18.0.2/16",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {}
    }
]
```

---

### docker network create

Create a network.

**Syntax:**
```bash
docker network create [OPTIONS] NETWORK
```

**Common Options:**
- `-d, --driver` - Driver to manage the network (default "bridge")
- `--subnet` - Subnet in CIDR format
- `--gateway` - Gateway for the master subnet
- `--ip-range` - Allocate container IP from a sub-range
- `--internal` - Restrict external access to the network
- `--ipv6` - Enable IPv6 networking
- `--label` - Set metadata on network
- `--opt` - Set driver specific options

**Examples:**

```bash
# Create basic network
docker network create my-network

# Create with specific driver
docker network create -d bridge my-bridge-network

# Create with custom subnet
docker network create --subnet=172.20.0.0/16 my-network

# Create with subnet and gateway
docker network create \
  --subnet=172.20.0.0/16 \
  --gateway=172.20.0.1 \
  my-network

# Create with IP range
docker network create \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.240.0/20 \
  my-network

# Create internal network (no external access)
docker network create --internal my-internal-network

# Create with IPv6
docker network create --ipv6 \
  --subnet=2001:db8::/64 \
  my-ipv6-network

# Create with labels
docker network create \
  --label env=production \
  --label app=web \
  my-network

# Create overlay network (Swarm mode)
docker network create -d overlay my-overlay-network

# Create with custom MTU
docker network create \
  -o "com.docker.network.driver.mtu"="1450" \
  my-network
```

**Output:**
```
d4e5f6g7h8i9a1b2c3d4e5f6g7h8i9a1b2c3d4e5f6g7h8i9a1b2c3d4e5f6
```

**Network Drivers:**
- **bridge**: Default, isolated network on host
- **host**: Remove network isolation
- **overlay**: Multi-host networking (Swarm)
- **macvlan**: Assign MAC address to container
- **none**: Disable networking

**Best Practices:**
- Use custom networks for container communication
- Avoid using default bridge network in production
- Use overlay networks for multi-host setups
- Implement network segmentation for security

---

### docker network connect

Connect a container to a network.

**Syntax:**
```bash
docker network connect [OPTIONS] NETWORK CONTAINER
```

**Examples:**

```bash
# Connect container to network
docker network connect my-network my-container

# Connect with alias
docker network connect --alias web my-network my-container

# Connect with specific IP
docker network connect --ip 172.20.0.10 my-network my-container
```

---

### docker network disconnect

Disconnect a container from a network.

**Syntax:**
```bash
docker network disconnect [OPTIONS] NETWORK CONTAINER
```

**Examples:**

```bash
# Disconnect container from network
docker network disconnect my-network my-container

# Force disconnect
docker network disconnect -f my-network my-container
```

---

### docker network rm

Remove one or more networks.

**Syntax:**
```bash
docker network rm NETWORK [NETWORK...]
```

**Examples:**

```bash
# Remove a network
docker network rm my-network

# Remove multiple networks
docker network rm network1 network2 network3

# Remove all unused networks
docker network prune
```

---

## Volume Management

### docker volume ls

List volumes.

**Syntax:**
```bash
docker volume ls [OPTIONS]
```

**Common Options:**
- `-q, --quiet` - Only display volume names
- `-f, --filter` - Filter output based on conditions
- `--format` - Format output using template

**Examples:**

```bash
# List all volumes
docker volume ls

# List only volume names
docker volume ls -q

# Filter by driver
docker volume ls --filter driver=local

# Filter by name
docker volume ls --filter name=my-vol

# Filter dangling volumes (not used by containers)
docker volume ls --filter dangling=true

# Filter by label
docker volume ls --filter label=environment=prod

# Custom format
docker volume ls --format "table {{.Name}}\t{{.Driver}}\t{{.Mountpoint}}"
```

**Output Example:**
```
DRIVER    VOLUME NAME
local     my-volume
local     postgres-data
local     redis-data
local     a1b2c3d4e5f6g7h8i9...
```

---

### docker volume inspect

Display detailed information on one or more volumes.

**Syntax:**
```bash
docker volume inspect [OPTIONS] VOLUME [VOLUME...]
```

**Common Options:**
- `-f, --format` - Format output using template

**Examples:**

```bash
# Inspect a volume
docker volume inspect my-volume

# Get mountpoint
docker volume inspect --format='{{.Mountpoint}}' my-volume

# Get driver
docker volume inspect --format='{{.Driver}}' my-volume

# Get labels
docker volume inspect --format='{{json .Labels}}' my-volume

# Inspect multiple volumes
docker volume inspect volume1 volume2
```

**Output Example (JSON):**
```json
[
    {
        "CreatedAt": "2026-01-08T10:00:00Z",
        "Driver": "local",
        "Labels": {
            "environment": "production",
            "app": "database"
        },
        "Mountpoint": "/var/lib/docker/volumes/my-volume/_data",
        "Name": "my-volume",
        "Options": {},
        "Scope": "local"
    }
]
```

**Key Information:**
- **Mountpoint**: Actual location on host filesystem
- **Driver**: Volume driver (usually "local")
- **Labels**: Metadata attached to volume
- **Scope**: Local or global (for cluster)
- **Options**: Driver-specific options

---

### docker volume create

Create a volume.

**Syntax:**
```bash
docker volume create [OPTIONS] [VOLUME]
```

**Common Options:**
- `-d, --driver` - Specify volume driver (default "local")
- `--label` - Set metadata for volume
- `-o, --opt` - Set driver specific options
- `--name` - Specify volume name

**Examples:**

```bash
# Create volume with auto-generated name
docker volume create

# Create named volume
docker volume create my-volume

# Create with specific driver
docker volume create -d local my-volume

# Create with labels
docker volume create \
  --label environment=production \
  --label app=database \
  postgres-data

# Create with driver options
docker volume create \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/to/dir \
  nfs-volume

# Create with specific mountpoint options
docker volume create \
  --opt type=tmpfs \
  --opt device=tmpfs \
  --opt o=size=100m,uid=1000 \
  temp-volume
```

**Output:**
```
my-volume
```

---

### docker volume rm

Remove one or more volumes.

**Syntax:**
```bash
docker volume rm [OPTIONS] VOLUME [VOLUME...]
```

**Common Options:**
- `-f, --force` - Force removal of volume

**Examples:**

```bash
# Remove a volume
docker volume rm my-volume

# Remove multiple volumes
docker volume rm volume1 volume2 volume3

# Force remove
docker volume rm -f my-volume

# Remove all unused volumes
docker volume prune
```

**Important Notes:**
- Cannot remove volume in use by a container
- Use `--force` to bypass some checks (use cautiously)
- Data is permanently deleted

---

### docker volume prune

Remove unused local volumes.

**Syntax:**
```bash
docker volume prune [OPTIONS]
```

**Common Options:**
- `-f, --force` - Do not prompt for confirmation
- `--filter` - Provide filter values
- `-a, --all` - Remove all unused volumes, not just anonymous ones

**Examples:**

```bash
# Remove anonymous unused volumes (interactive)
docker volume prune

# Remove all unused volumes
docker volume prune -a

# Remove without confirmation
docker volume prune -f

# Remove with all flag and no confirmation
docker volume prune -af

# Remove volumes with label filter
docker volume prune --filter "label=temporary"

# Remove volumes not used in last 24 hours
docker volume prune --filter "label!=keep"
```

**Output Example:**
```
WARNING! This will remove anonymous local volumes not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Volumes:
a1b2c3d4e5f6g7h8i9...
b2c3d4e5f6g7h8i9a1...

Total reclaimed space: 2.5GB
```

**Important Notes:**
- Volumes are never removed automatically (to prevent data loss)
- Anonymous volumes are volumes without explicit names
- Use `--all` flag to prune both anonymous and named volumes
- Named volumes require the `--all` flag to be pruned
- Always verify before pruning in production environments

**Anonymous vs Named Volumes:**
```bash
# Named volume (won't be pruned without --all)
docker volume create my-data

# Anonymous volume (will be pruned)
docker run -v /data nginx
```

---

## Best Practices

### Container Lifecycle Management

**1. Container Design**
- **Single Concern**: Each container should have one primary concern
- **Ephemeral Containers**: Design containers to be easily stopped, destroyed, and rebuilt
- **Stateless When Possible**: Store state in volumes or external services
- **Minimal Images**: Include only necessary dependencies

**Example:**
```bash
# Good: Separate concerns
docker run -d --name web nginx
docker run -d --name db postgres
docker run -d --name cache redis

# Not ideal: Multiple services in one container
docker run -d --name monolith custom-image-with-everything
```

**2. Resource Management**

**Set Resource Limits:**
```bash
# Limit memory
docker run -d --memory="512m" --memory-swap="1g" nginx

# Limit CPU
docker run -d --cpus="1.5" nginx

# Combined limits
docker run -d \
  --memory="1g" \
  --cpus="2" \
  --pids-limit=100 \
  nginx
```

**In docker-compose.yml:**
```yaml
services:
  web:
    image: nginx
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

**3. Health Checks**

**Always implement health checks:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost/health || exit 1
```

**Monitor health:**
```bash
# Check health status
docker ps --filter "health=unhealthy"

# Inspect health details
docker inspect --format='{{json .State.Health}}' container-name | jq
```

**4. Logging Best Practices**

**Use appropriate log drivers:**
```bash
# JSON file (default, works with docker logs)
docker run -d --log-driver json-file nginx

# Configure log rotation
docker run -d \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  nginx
```

**Monitor logs effectively:**
```bash
# Follow recent logs
docker logs -f --tail 100 container-name

# Filter by time
docker logs --since 1h container-name

# Multiple containers
docker compose logs -f --tail=50 web database
```

### Security Best Practices

**1. Run as Non-Root User**

```dockerfile
# Create and use non-root user
RUN useradd -r -u 1001 appuser
USER appuser
```

```bash
# Run with specific user
docker run -d --user 1001:1001 nginx
```

**2. Use Official Images**

```bash
# Good: Official verified images
docker pull nginx
docker pull postgres:14-alpine

# Verify image source
docker pull docker.io/library/nginx:latest
```

**3. Scan for Vulnerabilities**

```bash
# Use Docker Scout or similar tools
docker scout cves nginx:latest

# Regular updates
docker pull nginx:latest
docker compose pull
```

**4. Limit Capabilities**

```bash
# Drop all capabilities and add only needed ones
docker run -d \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  nginx
```

### Network Best Practices

**1. Use Custom Networks**

```bash
# Create dedicated network
docker network create --driver bridge app-network

# Use in production
docker run -d --name web --network app-network nginx
docker run -d --name db --network app-network postgres
```

**2. Network Segmentation**

```bash
# Frontend network
docker network create frontend

# Backend network
docker network create backend

# Web server on both
docker network connect frontend web
docker network connect backend web

# Database only on backend
docker network connect backend db
```

**3. Service Discovery**

```bash
# Containers can reach each other by name
docker run -d --name db --network app-net postgres
docker run -d --name web --network app-net \
  -e DATABASE_URL=postgresql://db:5432/mydb \
  myapp
```

### Volume Best Practices

**1. Use Named Volumes for Persistent Data**

```bash
# Create named volume
docker volume create postgres-data

# Use in container
docker run -d \
  --name db \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:14
```

**2. Backup Volumes**

```bash
# Backup volume to tar
docker run --rm \
  -v postgres-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz -C /data .

# Restore volume from tar
docker run --rm \
  -v postgres-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup.tar.gz -C /data
```

**3. Volume Labels for Organization**

```bash
# Create with labels
docker volume create \
  --label env=production \
  --label app=database \
  --label backup=daily \
  prod-db-data
```

### Image Management Best Practices

**1. Regular Cleanup**

```bash
# Remove dangling images weekly
docker image prune -f

# Remove unused images monthly
docker image prune -af --filter "until=168h"

# Complete system cleanup
docker system prune -af --volumes
```

**2. Tag Strategy**

```bash
# Use semantic versioning
docker tag myapp:latest myapp:1.0.0
docker tag myapp:latest myapp:1.0
docker tag myapp:latest myapp:1

# Environment tags
docker tag myapp:latest myapp:production
docker tag myapp:dev-abc123 myapp:staging
```

**3. Multi-Stage Builds**

```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:18-alpine
COPY --from=builder /app/node_modules ./node_modules
COPY . .
CMD ["node", "server.js"]
```

### Docker Compose Best Practices

**1. Environment-Specific Configs**

```bash
# Base config
# docker-compose.yml

# Development overrides
# docker-compose.override.yml (auto-loaded)

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Testing
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

**2. Use .env Files**

```bash
# .env file
POSTGRES_VERSION=14
POSTGRES_PASSWORD=secret
APP_PORT=8000

# docker-compose.yml
services:
  db:
    image: postgres:${POSTGRES_VERSION}
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  web:
    ports:
      - "${APP_PORT}:5000"
```

**3. Health Checks in Compose**

```yaml
services:
  web:
    image: nginx
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Monitoring and Maintenance

**1. Regular Health Monitoring**

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.State}}"

# Monitor resource usage
docker stats --no-stream

# Check disk usage
docker system df
```

**2. Automated Cleanup Script**

```bash
#!/bin/bash
# cleanup.sh

echo "Removing stopped containers..."
docker container prune -f

echo "Removing dangling images..."
docker image prune -f

echo "Removing unused networks..."
docker network prune -f

echo "Removing unused volumes (careful!)..."
docker volume prune -f

echo "Cleanup complete!"
docker system df
```

**3. Log Rotation**

```bash
# Configure globally in /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "compress": "true"
  }
}
```

### Production Deployment Checklist

**Pre-Deployment:**
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Logging configured with rotation
- [ ] Volumes for persistent data
- [ ] Custom networks configured
- [ ] Security scans completed
- [ ] Backup strategy in place

**Deployment:**
```bash
# 1. Pull latest images
docker compose pull

# 2. Build if needed
docker compose build

# 3. Run database migrations (if applicable)
docker compose run --rm web python manage.py migrate

# 4. Start services
docker compose up -d

# 5. Verify health
docker compose ps
docker compose logs -f --tail=50
```

**Post-Deployment:**
- [ ] Verify all services healthy
- [ ] Check logs for errors
- [ ] Test application endpoints
- [ ] Monitor resource usage
- [ ] Set up alerts

### Troubleshooting Common Issues

**1. Container Won't Start**

```bash
# Check logs
docker logs container-name

# Inspect container
docker inspect container-name

# Check events
docker events --since 10m

# Try interactive mode
docker run -it --entrypoint /bin/sh image-name
```

**2. Network Connectivity Issues**

```bash
# Check network configuration
docker network inspect network-name

# Test connectivity between containers
docker exec container1 ping container2

# Check DNS resolution
docker exec container1 nslookup container2
```

**3. Performance Issues**

```bash
# Check resource usage
docker stats

# Inspect detailed metrics
docker inspect --format='{{.State.Status}}' container-name

# Check host resources
df -h  # Disk space
free -h  # Memory
top  # CPU usage
```

**4. Volume Permission Issues**

```bash
# Check volume mountpoint
docker volume inspect volume-name

# Fix permissions (example)
docker run --rm -v volume-name:/data alpine chown -R 1000:1000 /data
```

---

## Quick Reference

### Essential Commands Cheatsheet

**Container Basics:**
```bash
docker ps                          # List running containers
docker ps -a                       # List all containers
docker logs -f <container>         # Follow container logs
docker exec -it <container> bash   # Interactive shell
docker stop <container>            # Stop container
docker start <container>           # Start container
docker restart <container>         # Restart container
docker rm <container>              # Remove container
```

**Images:**
```bash
docker images                      # List images
docker pull <image>                # Pull image
docker rmi <image>                 # Remove image
docker image prune -a              # Remove unused images
docker build -t <name> .           # Build image
```

**Docker Compose:**
```bash
docker compose up -d               # Start services
docker compose down                # Stop and remove
docker compose ps                  # List services
docker compose logs -f             # Follow logs
docker compose restart             # Restart services
docker compose pull                # Pull images
```

**Networks:**
```bash
docker network ls                  # List networks
docker network create <name>       # Create network
docker network inspect <name>      # Inspect network
docker network connect <net> <con> # Connect container
```

**Volumes:**
```bash
docker volume ls                   # List volumes
docker volume create <name>        # Create volume
docker volume inspect <name>       # Inspect volume
docker volume prune                # Remove unused volumes
```

**System:**
```bash
docker system df                   # Show disk usage
docker system prune                # Clean up everything
docker stats                       # Resource usage
docker info                        # System info
```

---

## Sources

This reference guide was compiled from official Docker documentation and verified industry resources:

- [Docker CLI Reference](https://docs.docker.com/reference/cli/docker/)
- [Docker Container Commands](https://docs.docker.com/reference/cli/docker/container/)
- [Docker Compose Documentation](https://docs.docker.com/reference/cli/docker/compose/)
- [Docker Image Commands](https://docs.docker.com/reference/cli/docker/image/pull/)
- [Docker Network Documentation](https://docs.docker.com/reference/cli/docker/network/)
- [Docker Volume Documentation](https://docs.docker.com/reference/cli/docker/volume/)
- [Docker Build Best Practices](https://docs.docker.com/build/building/best-practices/)
- [Container Runtime Metrics](https://docs.docker.com/engine/containers/runmetrics/)
- [Docker Health Checks Guide](https://lumigo.io/container-monitoring/docker-health-check-a-practical-guide/)
- [Docker Container Lifecycle Management](https://daily.dev/blog/docker-container-lifecycle-management-best-practices)
- [Docker Logging Documentation](https://docs.docker.com/engine/logging/)
- [Prune Unused Docker Objects](https://docs.docker.com/engine/manage-resources/pruning/)

---

**Document Version:** 1.0
**Last Updated:** January 8, 2026
**Docker Version Compatibility:** Docker Engine 20.10+ and Docker Compose V2

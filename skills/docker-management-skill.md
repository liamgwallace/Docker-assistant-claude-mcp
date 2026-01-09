# Docker Management Skill

## Your Role
You manage Docker via Portainer CLI and Docker CLI with full access to:
- Docker socket (`/var/run/docker.sock`)
- Portainer CLI (psu + portainer-cli)
- Stacks dir: `/home/liam/docker/stacks/`
- Volumes dir: `/home/liam/docker/volumes/`

## Environment
- **Network**: External `web` network (already exists - DO NOT create)
- **Portainer**: Endpoint ID 1
- **Domain**: `*.bramleyvale.com`
- **Traefik**: Routes via labels, no port mappings needed for web services

## Naming Rules
- Containers: `lowercase-with-hyphens`
- Stacks: `lowercase_with_underscores`
- Volumes: `{stack_name}_{purpose}`

## Portainer CLI (psu)

```bash
# Deploy/update stack
psu stack deploy {name} --stack-file docker-compose.yml --endpoint 1

# List stacks
psu stack ls --endpoint 1

# Show stack services
psu stack ps {name} --endpoint 1

# Remove stack
psu stack rm {name} --endpoint 1
```

## Docker Commands

### Containers
```bash
docker ps [-a] [--filter name=x]
docker start|stop|restart {name}
docker logs {name} [--tail 100] [-f] [--timestamps]
docker inspect {name}
docker stats [--no-stream]
docker rm [-f] {name}
```

### Docker Compose
```bash
cd /home/liam/docker/stacks/{name}
docker compose up -d [--pull always]
docker compose down [-v]
docker compose ps [-a]
docker compose logs [-f] [service]
docker compose pull
docker compose restart
```

### Images
```bash
docker images
docker pull {image}:{tag}
docker rmi {image}
docker image prune [-a]
```

### Networks
```bash
docker network ls
docker network inspect web
docker network connect|disconnect web {container}
```

### Volumes
```bash
docker volume ls
docker volume inspect {name}
docker volume rm {name}
docker volume prune
```

## Docker Compose Template

```yaml
version: '3.8'

services:
  service-name:
    image: image:tag
    container_name: service-name-container
    restart: unless-stopped
    networks:
      - web
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.service.rule=Host(`service.bramleyvale.com`)"
      - "traefik.http.routers.service.entrypoints=web"
      - "traefik.http.services.service.loadbalancer.server.port=80"
    environment:
      - VAR=value
    volumes:
      - service_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  web:
    external: true

volumes:
  service_data:
```

## Common Workflows

### Deploy Stack
```bash
mkdir -p /home/liam/docker/stacks/{name}
cd /home/liam/docker/stacks/{name}
# Create docker-compose.yml
psu stack deploy {name} --stack-file docker-compose.yml --endpoint 1
docker ps --filter name={name}
```

### Check Health
```bash
psu stack ls --endpoint 1
docker ps -a
docker inspect --format='{{.State.Health.Status}}' {container}
docker logs {container} --tail 50
```

### Update Stack
```bash
cd /home/liam/docker/stacks/{name}
docker compose pull
psu stack deploy {name} --stack-file docker-compose.yml --endpoint 1
```

### Restart
```bash
docker restart {container}
# OR
cd /home/liam/docker/stacks/{name} && docker compose restart
```

### Remove Stack
```bash
psu stack rm {name} --endpoint 1
docker volume prune  # if needed
```

## Response Format

Always use this structure:

```markdown
## Status: Success ✓ | Failed ❌

### Output
\```
[command outputs]
\```

### Details
- What was done
- Configuration applied

### Access (if applicable)
- URL: http://service.bramleyvale.com
- Logs: `docker logs container-name`
```

## Critical Rules
1. External `web` network exists - never create it
2. Check port conflicts before assigning
3. Traefik services don't need port mappings
4. Include health checks for web services
5. Save compose files before deploying
6. Provide clear structured responses

## Troubleshooting

```bash
# Stack won't deploy
psu endpoint ls
docker compose config --quiet

# Container won't start
docker logs {container}
docker inspect {container}

# Health check failing
docker inspect --format='{{json .State.Health}}' {container} | jq
```

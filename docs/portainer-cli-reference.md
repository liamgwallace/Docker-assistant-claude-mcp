# Portainer CLI Tools Reference

This comprehensive guide covers two popular CLI tools for managing Portainer:
1. **portainer-stack-utils (psu)** - A Go-based CLI tool
2. **portainer-cli** - A Python-based CLI tool

## Table of Contents
- [Overview](#overview)
- [portainer-stack-utils (psu)](#portainer-stack-utils-psu)
  - [Installation](#installation-psu)
  - [Authentication & Configuration](#authentication--configuration-psu)
  - [Commands Reference](#commands-reference-psu)
  - [Usage Examples](#usage-examples-psu)
- [portainer-cli](#portainer-cli)
  - [Installation](#installation-portainer-cli)
  - [Authentication & Configuration](#authentication--configuration-portainer-cli)
  - [Commands Reference](#commands-reference-portainer-cli)
  - [Usage Examples](#usage-examples-portainer-cli)
- [Error Handling & Troubleshooting](#error-handling--troubleshooting)
- [Sources & References](#sources--references)

---

## Overview

### portainer-stack-utils (psu)
- **Language**: Go
- **Repository**: https://github.com/greenled/portainer-stack-utils
- **License**: GNU General Public License version 3
- **Status**: Active development (master branch is unstable; use release versions)
- **Portainer API Version**: Created for Portainer API 1.22.0

### portainer-cli
- **Language**: Python
- **Repository**: https://github.com/bothub-it/portainer-cli
- **PyPI**: https://pypi.org/project/portainer-cli/
- **Latest Version**: 0.3.0
- **Status**: Inactive (no updates in past 12+ months)
- **Use Case**: Continuous integration and deployment environments

---

## portainer-stack-utils (psu)

### Installation (psu)

#### Download Binaries
Download pre-compiled binaries for your platform and architecture from the [GitHub releases page](https://github.com/greenled/portainer-stack-utils/releases).

**Supported Platforms:**
- Linux (amd64, arm, arm64)
- Windows (amd64)
- macOS (amd64, arm64)

#### Using Docker
```bash
docker pull greenled/portainer-stack-utils
```

Run with Docker:
```bash
docker run --rm greenled/portainer-stack-utils psu help
```

#### From Source (Go)
```bash
go install github.com/greenled/portainer-stack-utils@latest
```

### Authentication & Configuration (psu)

portainer-stack-utils supports three configuration methods that can be combined:

#### 1. Inline Flags
```bash
psu stack deploy mystack \
  --url https://portainer.example.com \
  --user admin \
  --password mypassword \
  --endpoint primary \
  --stack-file docker-compose.yml
```

#### 2. Environment Variables
All configuration keys can be set via environment variables with the `PSU_` prefix.

**Naming Convention:**
- Pattern: `PSU_[COMMAND_[SUBCOMMAND_]]FLAG`
- Replace `-` and `.` with `_` in flag names
- All uppercase

**Common Environment Variables:**
```bash
export PSU_URL=https://portainer.example.com
export PSU_USER=admin
export PSU_PASSWORD=mypassword
export PSU_ACCESS_TOKEN=your_api_token_here
export PSU_INSECURE=true  # Skip SSL verification
export PSU_ENDPOINT=primary
export PSU_TIMEOUT=60
export PSU_LOG_LEVEL=info
```

**For Stack Deploy:**
```bash
export PSU_STACK_DEPLOY_ENV_FILE=.env
export PSU_STACK_DEPLOY_STACK_FILE=docker-compose.yml
```

#### 3. Configuration Files
Default location: `$HOME/.psu.yaml`

**Supported formats:** JSON, TOML, YAML, HCL, envfile, Java properties

**Example YAML configuration** (`~/.psu.yaml`):
```yaml
url: https://portainer.example.com
user: admin
password: mypassword
# Or use access token instead:
# access-token: your_api_token_here
insecure: false
log-level: info
endpoint: primary
timeout: 60

stack:
  deploy:
    env-file: .env
    stack-file: docker-compose.yml
```

**Example JSON configuration** (`~/.psu.json`):
```json
{
  "url": "https://portainer.example.com",
  "user": "admin",
  "password": "mypassword",
  "endpoint": "primary",
  "log-level": "info"
}
```

**Using a custom config file:**
```bash
psu --config /path/to/config.yaml stack ls
```

#### Global Flags
These flags work with all commands:

| Flag | Short | Description | Environment Variable |
|------|-------|-------------|---------------------|
| `--url` | | Portainer server URL | `PSU_URL` |
| `--user` | | Portainer username | `PSU_USER` |
| `--password` | | Portainer password | `PSU_PASSWORD` |
| `--access-token` | | Portainer API access token | `PSU_ACCESS_TOKEN` |
| `--endpoint` | | Portainer endpoint name or ID | `PSU_ENDPOINT` |
| `--insecure` | `-i` | Skip SSL certificate verification | `PSU_INSECURE` |
| `--log-level` | | Log verbosity (panic, fatal, error, warn, info, debug, trace) | `PSU_LOG_LEVEL` |
| `--config` | | Path to configuration file | `PSU_CONFIG` |
| `--timeout` | | Request timeout in seconds | `PSU_TIMEOUT` |

### Commands Reference (psu)

#### General Commands

##### help
Display help information for commands.

```bash
psu help
psu help stack
psu help stack deploy
```

##### status
Display status information.

```bash
psu status
psu status --help
```

##### config
View and manage configuration.

```bash
# List all available configuration options
psu config ls

# Show current configuration
psu config show
```

---

#### Stack Commands

##### stack deploy
Deploy a new stack or update an existing one.

**Aliases:** `create`, `up`

**Syntax:**
```bash
psu stack deploy [stack-name] [flags]
```

**Flags:**
| Flag | Short | Description |
|------|-------|-------------|
| `--stack-file` | `-c` | Path to docker-compose file |
| `--env-file` | `-e` | Path to environment file |
| `--prune` | | Remove services not defined in compose file |
| `--endpoint` | | Target endpoint |

**Examples:**
```bash
# Basic deployment
psu stack deploy mystack --stack-file docker-compose.yml

# With environment file
psu stack deploy mystack -c docker-compose.yml -e .env

# With debug logging
psu stack deploy mystack -c docker-compose.yml --log-level debug

# Deploy to specific endpoint
psu stack deploy mystack \
  --endpoint primary \
  --stack-file docker-compose.yml \
  --env-file .env
```

##### stack list (ls)
List all stacks on an endpoint.

**Syntax:**
```bash
psu stack ls [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--endpoint` | Target endpoint |
| `--format` | Format output using Go template |
| `--quiet` | Only display stack names |

**Examples:**
```bash
# List all stacks
psu stack ls

# List stacks on specific endpoint
psu stack ls --endpoint primary

# Custom format (stack names only)
psu stack ls --endpoint primary --format "{{ .Name }}"

# Show stack names and IDs
psu stack ls --format "{{ .Name }}: {{ .Id }}"
```

##### stack remove (rm)
Remove a stack.

**Syntax:**
```bash
psu stack rm [stack-name] [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--endpoint` | Target endpoint |

**Examples:**
```bash
# Remove a stack
psu stack rm mystack

# Remove stack from specific endpoint
psu stack rm mystack --endpoint primary
```

##### stack ps
Show tasks/services in a stack.

**Syntax:**
```bash
psu stack ps [stack-name] [flags]
```

**Examples:**
```bash
# Show stack services
psu stack ps mystack --endpoint primary
```

---

#### Endpoint Commands

##### endpoint list
List all endpoints.

**Syntax:**
```bash
psu endpoint ls [flags]
```

**Examples:**
```bash
# List all endpoints
psu endpoint ls

# List with custom format
psu endpoint ls --format "{{ .Name }}: {{ .URL }}"
```

---

#### Docker Proxy Command

##### proxy
Expose an endpoint's Docker API through a local proxy, allowing you to run Docker commands with Portainer's RBAC.

**Syntax:**
```bash
psu proxy --endpoint [endpoint-name] --address [listen-address]
```

**Examples:**
```bash
# Start proxy on localhost:2375
psu proxy --endpoint primary --address 127.0.0.1:2375

# In another terminal, configure Docker client:
export DOCKER_HOST=tcp://127.0.0.1:2375

# Now run Docker commands through Portainer
docker ps
docker images
docker stack ls
```

**Known Limitations:**
- WebSocket commands fail: `docker attach`, `docker exec`, `docker system events`
- Error: "unable to upgrade to tcp, received 200"
- Stacks created via `docker stack` (not `psu stack`) have limited control in Portainer

---

### Usage Examples (psu)

#### Example 1: Basic Stack Deployment
```bash
# Set environment variables
export PSU_URL=https://portainer.example.com
export PSU_USER=admin
export PSU_PASSWORD=secretpass
export PSU_ENDPOINT=production

# Deploy stack
psu stack deploy wordpress --stack-file docker-compose.yml
```

#### Example 2: Deploy with Environment Variables
```bash
# Create .env file
cat > .env << EOF
MYSQL_ROOT_PASSWORD=strongpassword
MYSQL_DATABASE=wordpress
MYSQL_USER=wpuser
MYSQL_PASSWORD=wppass
WORDPRESS_DB_HOST=db:3306
ALLOWED_HOSTS=*
EOF

# Deploy using inline flags
psu stack deploy wordpress \
  --url https://portainer.example.com \
  --user admin \
  --password secretpass \
  --endpoint production \
  --stack-file docker-compose.yml \
  --env-file .env

# Or using environment variables
export PSU_STACK_DEPLOY_ENV_FILE=.env
psu stack deploy wordpress -c docker-compose.yml
```

#### Example 3: Using Configuration File
```bash
# Create config file
cat > ~/.psu.yaml << EOF
url: https://portainer.example.com
user: admin
password: secretpass
insecure: false
log-level: info
endpoint: production
EOF

# Now commands use the config automatically
psu stack ls
psu stack deploy myapp -c docker-compose.yml -e .env
psu stack rm oldapp
```

#### Example 4: List Stacks with Filtering
```bash
# List all stack names
psu stack ls --format "{{ .Name }}"

# List stacks with details
psu stack ls --endpoint production

# Get specific stack information
psu stack ps mystack --endpoint production
```

#### Example 5: CI/CD Pipeline Integration
```bash
#!/bin/bash
# deploy.sh - Example CI/CD deployment script

set -e

# Configuration
export PSU_URL=${PORTAINER_URL}
export PSU_ACCESS_TOKEN=${PORTAINER_TOKEN}
export PSU_ENDPOINT=${DEPLOY_ENVIRONMENT:-staging}
export PSU_LOG_LEVEL=info

# Deploy the stack
echo "Deploying to ${PSU_ENDPOINT}..."
psu stack deploy ${CI_PROJECT_NAME} \
  --stack-file docker-compose.yml \
  --env-file .env.${PSU_ENDPOINT} \
  --prune

echo "Deployment complete!"

# Verify deployment
psu stack ps ${CI_PROJECT_NAME}
```

#### Example 6: Using Access Tokens (Recommended for CI/CD)
```bash
# Generate access token in Portainer UI first
# User menu > My account > Access tokens

export PSU_URL=https://portainer.example.com
export PSU_ACCESS_TOKEN=ptr_your_access_token_here
export PSU_ENDPOINT=production

# Deploy without username/password
psu stack deploy myapp -c docker-compose.yml
```

---

## portainer-cli

### Installation (portainer-cli)

#### Using pip
```bash
pip install portainer-cli
```

#### From Source
```bash
git clone https://github.com/bothub-it/portainer-cli.git
cd portainer-cli
pipenv install  # or: pip install -r requirements.txt
```

#### For Development
```bash
git clone https://github.com/bothub-it/portainer-cli.git
cd portainer-cli
make install  # Uses Pipenv for development dependencies
```

### Authentication & Configuration (portainer-cli)

#### Command-Line Authentication
Use `-a` or `--authentication` flag with `-username` and `-password`:

```bash
portainer-cli [command] \
  -u http://portainer.example.com \
  -a \
  -username admin \
  -password secretpass \
  [other options]
```

#### Configuration File
Save configuration to `.portainer-cli.json` in the current directory:

```json
{
  "url": "http://portainer.example.com",
  "username": "admin",
  "password": "secretpass"
}
```

The CLI will automatically load this configuration file if present.

#### Common Options
| Option | Description |
|--------|-------------|
| `-u`, `--url` | Portainer server URL |
| `-a`, `--authentication` | Enable authentication (requires -username and -password) |
| `-username` | Portainer username |
| `-password` | Portainer password |
| `-e`, `--endpoint_id` | Endpoint ID |
| `-n`, `--name` | Stack name |
| `-s`, `--stack_id` | Stack ID |
| `-sf`, `--stack_file` | Path to docker-compose file |
| `-env-file` | Path to environment variables file |

### Commands Reference (portainer-cli)

#### create_stack
Create a new stack.

**Syntax:**
```bash
portainer-cli create_stack -n [stack_name] -e [endpoint_id] -sf [stack_file]
```

**Options:**
- `-n`, `--name`: Stack name (required)
- `-e`, `--endpoint_id`: Endpoint ID (required)
- `-sf`, `--stack_file`: Path to docker-compose.yml (required)
- `-env-file`: Path to environment variables file (optional)

**Example:**
```bash
portainer-cli create_stack \
  -u http://portainer.example.com \
  -a -username admin -password secretpass \
  -n myapp \
  -e 1 \
  -sf docker-compose.yml
```

#### update_stack
Update an existing stack.

**Syntax:**
```bash
portainer-cli update_stack -s [stack_id] -e [endpoint_id] -sf [stack_file]
```

**Options:**
- `-s`, `--stack_id`: Stack ID (required)
- `-e`, `--endpoint_id`: Endpoint ID (required)
- `-sf`, `--stack_file`: Path to docker-compose.yml (required)
- `-env-file`: Path to environment variables file (optional)

**Alternative syntax:**
```bash
portainer-cli update_stack [stack_id] [endpoint_id] [stack_file] [-env-file]
```

**Example:**
```bash
portainer-cli update_stack \
  -u http://portainer.example.com \
  -a -username admin -password secretpass \
  -s 5 \
  -e 1 \
  -sf docker-compose.yml
```

#### create_or_update_stack
Create a stack if it doesn't exist, or update it if it does (based on stack name).

**Syntax:**
```bash
portainer-cli create_or_update_stack -n [stack_name] -e [endpoint_id] -sf [stack_file]
```

**Options:**
- `-n`, `--name`: Stack name (required)
- `-e`, `--endpoint_id`: Endpoint ID (required)
- `-sf`, `--stack_file`: Path to docker-compose.yml (required)
- `-env-file`: Path to environment variables file (optional)

**Example:**
```bash
portainer-cli create_or_update_stack \
  -u http://portainer.example.com \
  -a -username admin -password secretpass \
  -n myapp \
  -e 1 \
  -sf docker-compose.yml \
  -env-file .env
```

#### get_stack_id
Get the ID of a stack by its name.

**Syntax:**
```bash
portainer-cli get_stack_id -n [stack_name] -e [endpoint_id]
```

**Options:**
- `-n`, `--name`: Stack name (required)
- `-e`, `--endpoint_id`: Endpoint ID (required)

**Example:**
```bash
STACK_ID=$(portainer-cli get_stack_id \
  -u http://portainer.example.com \
  -a -username admin -password secretpass \
  -n myapp \
  -e 1)
echo "Stack ID: $STACK_ID"
```

#### update_registry
Update registry authentication.

**Syntax:**
```bash
portainer-cli update_registry [registry_id] -a -username [user] -password [pass]
```

**Example:**
```bash
portainer-cli update_registry 1 \
  -u http://portainer.example.com \
  -a \
  -username douglas \
  -password d1234
```

---

### Usage Examples (portainer-cli)

#### Example 1: Basic Stack Creation
```bash
# Create a new stack
portainer-cli create_stack \
  -u http://192.168.1.100:9000 \
  -a -username admin -password admin123 \
  -n wordpress \
  -e 1 \
  -sf docker-compose.yml
```

#### Example 2: Update Existing Stack
```bash
# First, get the stack ID
STACK_ID=$(portainer-cli get_stack_id \
  -u http://192.168.1.100:9000 \
  -a -username admin -password admin123 \
  -n wordpress \
  -e 1)

# Update the stack
portainer-cli update_stack \
  -u http://192.168.1.100:9000 \
  -a -username admin -password admin123 \
  -s $STACK_ID \
  -e 1 \
  -sf docker-compose.yml
```

#### Example 3: Using Configuration File
```bash
# Create configuration file
cat > .portainer-cli.json << EOF
{
  "url": "http://192.168.1.100:9000",
  "username": "admin",
  "password": "admin123"
}
EOF

# Now commands can omit URL and authentication
portainer-cli create_or_update_stack \
  -n myapp \
  -e 1 \
  -sf docker-compose.yml
```

#### Example 4: Deploy with Environment Variables
```bash
# Create environment file
cat > .env << EOF
DATABASE_URL=postgresql://user:pass@db:5432/mydb
SECRET_KEY=my-secret-key
DEBUG=false
EOF

# Deploy stack with environment variables
portainer-cli create_or_update_stack \
  -u http://portainer.example.com \
  -a -username admin -password secretpass \
  -n myapp \
  -e 1 \
  -sf docker-compose.yml \
  -env-file .env
```

#### Example 5: CI/CD Integration
```bash
#!/bin/bash
# deploy.sh - GitLab CI/CD deployment script

set -e

# Deploy or update stack
portainer-cli create_or_update_stack \
  -u ${PORTAINER_URL} \
  -a -username ${PORTAINER_USER} -password ${PORTAINER_PASSWORD} \
  -n ${CI_PROJECT_NAME} \
  -e ${PORTAINER_ENDPOINT_ID} \
  -sf docker-compose.yml \
  -env-file .env.production

echo "Deployment successful!"
```

#### Example 6: Multiple Stacks Deployment
```bash
#!/bin/bash
# deploy-all.sh - Deploy multiple stacks

STACKS=("frontend" "backend" "database" "cache")

for stack in "${STACKS[@]}"; do
  echo "Deploying $stack..."
  portainer-cli create_or_update_stack \
    -u http://portainer.example.com \
    -a -username admin -password secretpass \
    -n $stack \
    -e 1 \
    -sf stacks/$stack/docker-compose.yml \
    -env-file stacks/$stack/.env
done

echo "All stacks deployed!"
```

---

## Error Handling & Troubleshooting

### Common Issues with portainer-stack-utils

#### 1. WebSocket Connection Errors
**Problem:** Commands fail with "unable to upgrade to tcp, received 200"

**Affected Commands:**
- `docker attach`
- `docker exec`
- `docker system events`

**Solution:** These commands are known to fail when using `psu proxy`. Use the Portainer UI for interactive container operations.

#### 2. Bad Substitution Error
**Problem:** Error like `./psu: line 290: bad substitution`

**Cause:** Special characters in docker-compose files not properly escaped

**Solution:**
- Upgrade to latest version
- Check docker-compose file for unusual characters
- Validate YAML syntax

#### 3. Authentication Failures
**Problem:** "Unauthorized" or "Access denied" errors

**Solutions:**
```bash
# 1. Verify credentials
psu status --log-level debug

# 2. Use access token instead of password
export PSU_ACCESS_TOKEN=ptr_your_token_here
unset PSU_PASSWORD

# 3. Check endpoint exists
psu endpoint ls

# 4. Verify SSL settings
export PSU_INSECURE=true  # For self-signed certificates
```

#### 4. SSL Certificate Errors
**Problem:** Certificate verification failures

**Solutions:**
```bash
# Option 1: Skip verification (not recommended for production)
psu stack deploy mystack --insecure -c docker-compose.yml

# Option 2: Use environment variable
export PSU_INSECURE=true

# Option 3: Add to config file
echo "insecure: true" >> ~/.psu.yaml
```

#### 5. Stack Deployment Failures
**Problem:** Stack fails to deploy

**Troubleshooting Steps:**
```bash
# 1. Enable debug logging
psu stack deploy mystack -c docker-compose.yml --log-level debug

# 2. Verify compose file is valid
docker-compose -f docker-compose.yml config

# 3. Check endpoint is accessible
psu endpoint ls

# 4. Verify environment file exists
test -f .env && echo "Found" || echo "Missing"

# 5. Check for existing stack conflicts
psu stack ls | grep mystack
```

#### 6. Configs/Secrets Limitations
**Problem:** Cannot deploy stacks with configs/secrets

**Current Limitation:** Can only use `external: true` for configs/secrets

**Workaround:**
1. Create configs/secrets manually in Portainer UI first
2. Reference them as external in docker-compose.yml:
```yaml
configs:
  my_config:
    external: true
```

### Common Issues with portainer-cli

#### 1. Password in Shell History
**Problem:** Passwords appear in bash/zsh history

**Solutions:**
```bash
# Option 1: Use configuration file
cat > .portainer-cli.json << EOF
{
  "url": "http://portainer.example.com",
  "username": "admin",
  "password": "secretpass"
}
EOF

# Option 2: Read password from file
PASSWORD=$(cat password.txt)
portainer-cli create_stack -a -username admin -password "$PASSWORD" ...

# Option 3: Prompt for password (if tool supports)
read -s -p "Password: " PASSWORD
portainer-cli create_stack -a -username admin -password "$PASSWORD" ...
```

#### 2. Module Not Found Errors
**Problem:** Import errors when running portainer-cli

**Solution:**
```bash
# Reinstall with dependencies
pip uninstall portainer-cli
pip install portainer-cli

# Or install in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install portainer-cli
```

#### 3. Invalid Endpoint ID
**Problem:** "Endpoint not found" errors

**Solution:**
```bash
# Find endpoint IDs via Portainer API
curl -X GET "http://portainer.example.com/api/endpoints" \
  -H "X-API-Key: your_token_here"

# Or check in Portainer UI: Home > Environments
# The endpoint ID is in the URL when viewing an environment
```

#### 4. Stack Already Exists
**Problem:** Cannot create stack with duplicate name

**Solution:**
```bash
# Use create_or_update_stack instead
portainer-cli create_or_update_stack \
  -n mystack \
  -e 1 \
  -sf docker-compose.yml

# Or delete existing stack first via Portainer UI/API
```

### Security Best Practices

#### For portainer-stack-utils:
```bash
# 1. Use access tokens instead of passwords
export PSU_ACCESS_TOKEN=ptr_your_token_here

# 2. Never use trace logging in production
export PSU_LOG_LEVEL=info  # NOT trace or debug

# 3. Store configs in protected files
chmod 600 ~/.psu.yaml

# 4. Use environment-specific configs
psu --config /secure/prod.yaml stack deploy ...

# 5. Rotate access tokens regularly
# Generate new tokens in Portainer: User menu > Access tokens
```

#### For portainer-cli:
```bash
# 1. Use configuration files instead of inline credentials
chmod 600 .portainer-cli.json

# 2. Never commit credentials to version control
echo ".portainer-cli.json" >> .gitignore
echo "password.txt" >> .gitignore

# 3. Use environment variables in CI/CD
portainer-cli create_stack \
  -u ${PORTAINER_URL} \
  -a -username ${PORTAINER_USER} -password ${PORTAINER_PASS}
```

### Logging and Debugging

#### portainer-stack-utils Log Levels:
- `panic` - Unexpected errors that stop execution
- `fatal` - Expected errors that stop execution
- `error` - Errors that don't stop execution
- `warn` - Warning messages
- `info` - General information (default)
- `debug` - Detailed information
- `trace` - **DANGER:** Includes sensitive data (tokens, passwords, env vars)

**Enable debugging:**
```bash
# Temporary
psu stack deploy mystack --log-level debug -c docker-compose.yml

# Persistent
export PSU_LOG_LEVEL=debug
```

#### Troubleshooting Checklist:
1. ✅ Verify Portainer is accessible
2. ✅ Check credentials/access token
3. ✅ Confirm endpoint exists and is online
4. ✅ Validate docker-compose.yml syntax
5. ✅ Check environment file exists and is readable
6. ✅ Review Portainer server logs
7. ✅ Test with debug/trace logging
8. ✅ Check network connectivity and firewall rules

---

## Sources & References

### portainer-stack-utils (psu)
- [GitHub Repository](https://github.com/greenled/portainer-stack-utils)
- [GitLab Mirror (Bash version)](https://gitlab.com/psuapp/psu)
- [Docker Hub Image](https://hub.docker.com/r/greenled/portainer-stack-utils/)
- [Go Package Documentation](https://pkg.go.dev/github.com/greenled/portainer-stack-utils)
- [Documentation Site](https://psuapp.gitlab.io/psu/1-0-stable/)

### portainer-cli
- [GitHub Repository](https://github.com/bothub-it/portainer-cli)
- [PyPI Package](https://pypi.org/project/portainer-cli/)
- [GitHub README](https://github.com/bothub-it/portainer-cli/blob/master/README.md)

### Portainer Official Documentation
- [Portainer Documentation](https://docs.portainer.io/)
- [Accessing the Portainer API](https://docs.portainer.io/api/access)
- [API Documentation](https://docs.portainer.io/api/docs)
- [API Usage Examples](https://docs.portainer.io/api/examples)
- [CLI Configuration Options](https://docs.portainer.io/advanced/cli)
- [Stacks Documentation](https://docs.portainer.io/user/docker/stacks)
- [Logs, Errors and Debugging](https://docs.portainer.io/faqs/troubleshooting/logs-errors-and-debugging)
- [Portainer Knowledge Base](https://portal.portainer.io/knowledge/troubleshooting)

### Docker Stack Reference
- [Docker Stack Commands](https://docs.docker.com/reference/cli/docker/stack/)
- [Docker Stack Deploy](https://docs.docker.com/reference/cli/docker/stack/deploy/)

### Community Resources
- [Portainer HTTP API by Example (Gist)](https://gist.github.com/deviantony/77026d402366b4b43fa5918d41bc42f8)
- [Using Portainer and GitHub for Continuous Deployment](https://joshbuker.com/blog/using-portainer-and-github-for-continuous-deployment/)

---

## Additional Notes

### Comparison: psu vs portainer-cli

| Feature | portainer-stack-utils (psu) | portainer-cli |
|---------|----------------------------|---------------|
| Language | Go | Python |
| Installation | Binary download | pip install |
| Status | Active | Inactive |
| Configuration | Multiple methods (flags, env, files) | Flags or config file |
| Authentication | Password or access token | Password only |
| Stack Commands | deploy, ls, rm, ps | create, update, create_or_update |
| Additional Features | Docker proxy, endpoint management | Registry updates |
| API Support | Comprehensive | Basic stack operations |
| CI/CD Ready | Yes, with access tokens | Yes, but less secure |
| Documentation | Good | Limited |

### Recommendations

**Use portainer-stack-utils if:**
- You need a modern, actively maintained tool
- You want comprehensive Portainer API access
- You need Docker proxy functionality
- You prefer native binaries without dependencies
- You want secure access token authentication

**Use portainer-cli if:**
- You already have Python infrastructure
- You only need basic stack operations
- You prefer pip-based installation
- Your existing automation uses it

**For new projects:** portainer-stack-utils (psu) is recommended due to active development and better feature set.

---

*Last Updated: 2026-01-08*
*Document Version: 1.0*

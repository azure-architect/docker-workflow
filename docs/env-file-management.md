# Environment File Management Guide

## Overview

All Docker deployments in the `/resources` directory use a centralized environment file approach for configuration management. This ensures consistency, portability, and easy maintenance across all projects.

## Directory Structure

```
/resources/
├── .env                    # Shared environment variables for ALL projects
├── n8n/
│   ├── docker-compose.yml  # Uses variables from /resources/.env
│   └── deploy.sh
├── postgres/
│   ├── docker-compose.yml  # Uses variables from /resources/.env
│   └── deploy.sh
└── other-projects/
    ├── docker-compose.yml  # Uses variables from /resources/.env
    └── deploy.sh
```

## Environment File Patterns

### 1. Shared Configuration (`/resources/.env`)

```bash
# Global Settings
TIMEZONE=America/New_York
SERVER_HOST=192.168.0.135

# Port Allocation Strategy
# n8n: 5612
# PostgreSQL: 5432
# Redis: 6379
# Custom Apps: 8000+

# n8n Configuration
N8N_HOST=192.168.0.135
N8N_PORT=5678                # Internal container port
N8N_EXTERNAL_PORT=5612       # External access port
N8N_PROTOCOL=http
N8N_OWNER_EMAIL=admin@localhost
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin123

# PostgreSQL Configuration
POSTGRES_EXTERNAL_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=main

# Redis Configuration
REDIS_EXTERNAL_PORT=6379
REDIS_PASSWORD=redis_password

# API Keys and Secrets
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=ant-...
```

### 2. Docker Compose Usage

Always reference environment variables with defaults:

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n-workflow
    restart: unless-stopped
    ports:
      - "${N8N_EXTERNAL_PORT:-5612}:5678"
    environment:
      - N8N_HOST=${N8N_HOST:-192.168.0.135}
      - N8N_PORT=${N8N_PORT:-5678}
      - N8N_PROTOCOL=${N8N_PROTOCOL:-http}
      - GENERIC_TIMEZONE=${TIMEZONE:-America/New_York}
      - N8N_OWNER_EMAIL=${N8N_OWNER_EMAIL}
      - N8N_BASIC_AUTH_ACTIVE=${N8N_BASIC_AUTH_ACTIVE:-true}
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
```

### 3. Deployment Script Usage

```bash
#!/bin/bash
# Always use --env-file to reference shared environment
ssh $REMOTE_HOST "cd $REMOTE_BASE/$PROJECT_NAME && docker compose --env-file ../.env up -d"
```

## Port Management Strategy

### Port Allocation Ranges
- **1000-4999**: Reserved for system services
- **5000-5999**: Development/automation tools (n8n, etc.)
- **6000-6999**: Databases and cache (Redis, etc.)
- **7000-7999**: Monitoring and logging
- **8000-8999**: Custom applications
- **9000-9999**: Development/testing instances

### Port Documentation
Always document port assignments in the shared `.env` file:

```bash
# Port Allocation Registry
# 5612 - n8n workflow automation
# 5432 - PostgreSQL database
# 6379 - Redis cache
# 8080 - App Server (development)
# 8081 - App Server (staging)
```

## Environment Variable Naming Conventions

### Service-Specific Variables
```bash
# Pattern: {SERVICE}_{PROPERTY}
N8N_HOST=192.168.0.135
N8N_EXTERNAL_PORT=5612
POSTGRES_USER=postgres
REDIS_PASSWORD=secure_password
```

### Port Variables
```bash
# Pattern: {SERVICE}_EXTERNAL_PORT for public access
# Pattern: {SERVICE}_PORT for internal container port
N8N_EXTERNAL_PORT=5612    # Public access
N8N_PORT=5678            # Internal container
```

### Credentials
```bash
# Pattern: {SERVICE}_{CREDENTIAL_TYPE}
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin123
POSTGRES_PASSWORD=secure_password
```

## Best Practices

### 1. Single Source of Truth
- All configuration in `/resources/.env`
- No hardcoded values in docker-compose.yml
- Use environment variables with sensible defaults

### 2. Environment Synchronization
```bash
# Local .env is template, always sync to remote
scp ./local/.env root@192.168.0.135:/resources/.env
```

### 3. Container Restarts
```bash
# Always restart containers after .env changes
docker compose down && docker compose --env-file ../.env up -d
```

### 4. Variable Validation
```bash
# Validate required variables before deployment
if [ -z "$N8N_EXTERNAL_PORT" ]; then
    echo "Error: N8N_EXTERNAL_PORT not set in .env"
    exit 1
fi
```

## Security Considerations

### 1. Sensitive Data
- Keep API keys and passwords in the shared `.env` file
- Never commit `.env` files to git
- Use strong, unique passwords for each service

### 2. File Permissions
```bash
# Secure the shared environment file
chmod 600 /resources/.env
chown root:root /resources/.env
```

### 3. Variable Scoping
- Use service-specific prefixes to avoid conflicts
- Document all variables in comments
- Regular audit of unused variables

## Deployment Workflow

### 1. Local Development
```bash
# Edit local .env template
nano ./n8n-deploy/.env

# Sync to remote server
scp .env root@192.168.0.135:/resources/.env
```

### 2. Service Deployment
```bash
# Deploy with shared environment
rsync -avz . root@192.168.0.135:/resources/n8n/
ssh root@192.168.0.135 "cd /resources/n8n && docker compose --env-file ../.env up -d"
```

### 3. Verification
```bash
# Verify environment loaded correctly
ssh root@192.168.0.135 "docker exec service-name env | grep SERVICE_"
```

## Troubleshooting

### Common Issues

1. **Variables not loading**: Ensure `--env-file ../.env` is used
2. **Port conflicts**: Check port allocation in shared `.env`
3. **Permission denied**: Check `.env` file permissions
4. **Stale configuration**: Restart containers after `.env` changes

### Debug Commands
```bash
# Check environment file
cat /resources/.env | grep SERVICE_

# Verify container environment
docker exec container-name env | grep SERVICE_

# Test port accessibility
netstat -tlnp | grep PORT_NUMBER
```

This centralized approach ensures all deployments are consistent, portable, and easy to manage across the entire `/resources` directory structure.
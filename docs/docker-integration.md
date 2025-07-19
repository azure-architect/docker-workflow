# Docker Integration User Guide

This guide covers how to use the Docker integration system with Claude Code for managing containers, development environments, and monitoring on your remote Docker server.

## Overview

The Docker integration provides container management through CLI tools and a comprehensive API wrapper. It connects to your Docker server at `192.168.0.135:2375` and includes safety validations to prevent dangerous operations.

## Current Implementation Status

✅ **Fully Implemented:**
- Docker API wrapper (`DockerManager` class)
- CLI tools (`docker_control.py`, `docker_dashboard.py`)
- Safety validation hooks
- Real-time monitoring dashboard
- Comprehensive error handling

⚠️ **Documentation Only (Not Yet Implemented):**
- Natural language Claude Code commands (`/docker`, `/dev_environment`)
- Automatic environment generation from descriptions
- Intelligent project analysis and recommendations
- One-command deployment workflows

The current system provides a solid foundation for Docker operations through Python APIs and CLI tools. The natural language interface is planned for future development.

## Quick Start

### Prerequisites

1. **Install Docker Python Library**
   ```bash
   pip install docker
   ```

2. **Verify Connection**
   ```bash
   python docker_control.py health
   ```

### Basic Usage

**List Containers:**
```bash
# CLI interface (WORKING)
python docker_control.py list           # Running containers
python docker_control.py list --all     # All containers

# Claude Code commands (DOCUMENTATION ONLY - shows guidance, doesn't execute)
/docker                                  # Shows Docker management help
/dev_environment                         # Shows environment setup guidance
```

**Container Management:**
```bash
# Direct Python API (WORKING)
python -c "from docker_control import DockerManager; dm = DockerManager(); dm.start_container('container_name')"

# CLI interface (WORKING)
python docker_control.py list
python docker_control.py health
python docker_control.py info

# Real-time monitoring (WORKING)
python docker_dashboard.py --refresh 5
```

## Command Reference

### Claude Code Commands (Currently Documentation Only)

⚠️ **Important**: The `/docker` and `/dev_environment` commands currently show **guidance and documentation only**. They do not execute actual Docker operations. Use the CLI tools below for actual functionality.

#### `/docker` - Docker Management Guidance
Shows comprehensive Docker management documentation including:

- Container operation guidance and examples
- Safety feature explanations
- Available CLI tool usage
- Best practices for container management

#### `/dev_environment` - Environment Setup Guidance  
Shows development environment setup documentation including:

**Supported Environments:**
- **Node.js Full Stack**: React/Vue + Node.js + MongoDB/PostgreSQL + Redis + Nginx
- **Python Development**: Flask/Django/FastAPI + PostgreSQL/MySQL + Redis + Celery
- **Full-Stack Web**: Frontend + API + Database + Cache + Load Balancer
- **Microservices**: API Gateway + Multiple Services + Service-specific DBs + Message Queue
- **Data Science**: Jupyter + PostgreSQL + Redis + Grafana

**Current Status**: Documentation and guidance only. For actual environment setup, use the CLI tools and Docker API below.

### CLI Tools

#### `docker_control.py` - Core Management
Direct command-line interface for Docker operations:

```bash
# Basic commands
python docker_control.py list           # List running containers
python docker_control.py list --all     # List all containers
python docker_control.py health         # Check Docker server health
python docker_control.py info           # Get system information

# Advanced usage (via Python import)
from docker_control import DockerManager
dm = DockerManager()

# Container operations
containers = dm.list_containers(all=True)
dm.run_container('nginx:latest', name='web-server', ports={'80': 8080})
dm.stop_container('web-server')
dm.start_container('web-server')
dm.remove_container('web-server')

# Image operations
dm.build_image('.', 'myapp:latest')
logs = dm.get_logs('web-server', lines=100)

# System operations
info = dm.system_info()
health = dm.health_check()
```

#### `docker_dashboard.py` - Real-time Monitoring
Live dashboard for monitoring container status and system health:

```bash
# Start dashboard with default 5-second refresh
python docker_dashboard.py

# Custom refresh rate and host
python docker_dashboard.py --refresh 3 --host 192.168.0.135:2375

# Command-line options
--refresh, -r    Refresh interval in seconds (default: 5)
--host          Docker host (default: 192.168.0.135:2375)
```

**Dashboard Features:**
- Real-time container status with color coding
- System resource information (CPU, memory, disk)
- Health status monitoring
- Container summary statistics
- Automatic refresh with graceful shutdown (Ctrl+C)

## Safety Features

### Critical Container Protection
The system automatically prevents removal of containers with critical names:
- Database containers: `database`, `db`, `mysql`, `postgres`, `postgresql`, `mongodb`, `mongo`
- Cache containers: `redis`, `cache`, `elasticsearch`
- Infrastructure: `nginx`, `proxy`, `traefik`

### Dangerous Operation Validation
Pre-execution hooks validate operations to prevent:
- Removing running containers without force flag
- Deleting base images without specific tags
- Creating privileged containers
- Conflicting with system networks
- Direct `docker rm`/`docker rmi` commands (redirected to safe wrapper)

### Error Handling
Comprehensive error handling with:
- Automatic connection recovery
- User-friendly error messages
- Graceful fallbacks for network issues
- Detailed logging for debugging

## Configuration

### Environment Variables
Set in `.claude/settings.json`:
```json
{
  "env": {
    "DOCKER_HOST": "tcp://192.168.0.135:2375"
  }
}
```

### Permissions
Docker operations are explicitly allowed in Claude Code:
```json
{
  "permissions": {
    "allow": [
      "Bash(docker *)",
      "Bash(python docker_control.py *)",
      "Bash(python docker_dashboard.py *)"
    ]
  }
}
```

### Hook Configuration
Safety validation is automatically applied:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "filePattern": "docker*",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/docker_pre_tool_use.py"
          }
        ]
      }
    ]
  }
}
```

## Development Environment Templates

### Node.js Full Stack
Creates a complete development environment with:
- **Frontend**: React/Vue/Angular development server with hot reload
- **Backend**: Node.js API with automatic restart on code changes
- **Database**: MongoDB or PostgreSQL with data persistence
- **Cache**: Redis for sessions and caching
- **Proxy**: Nginx for routing and static file serving
- **Networking**: Container-to-container communication
- **Volumes**: Source code mounted for live development

### Python Development
Sets up Python development environment with:
- **Application**: Python with Flask/Django/FastAPI framework
- **Database**: PostgreSQL or MySQL with persistent storage
- **Cache**: Redis for caching and session management
- **Worker Queue**: Celery for background task processing
- **Monitoring**: Built-in health checks and logging
- **Development Tools**: Hot reload, debugger support

### Microservices Architecture
Creates microservices development environment:
- **API Gateway**: Nginx or Traefik for service routing
- **Services**: Multiple containerized backend services
- **Databases**: Service-specific database instances
- **Message Queue**: Redis or RabbitMQ for inter-service communication
- **Service Discovery**: Automatic container networking
- **Load Balancing**: Request distribution across service instances

## Best Practices

### Container Naming
Use descriptive, consistent naming conventions:
```bash
# Good
my-app-api
my-app-database
my-app-cache

# Avoid
container1
temp
test
```

### Resource Management
- Monitor resource usage with the dashboard
- Clean up unused containers and images regularly
- Use appropriate restart policies
- Set resource limits for production containers

### Development Workflow
1. Use `/dev_environment` for initial setup
2. Mount source code directories as volumes
3. Use container networking for service communication
4. Monitor with `docker_dashboard.py`
5. Clean up with `/docker` commands when done

### Security Considerations
- The system connects to Docker without TLS (development only)
- Critical container protection is enforced
- Privileged containers are blocked
- Use force flags carefully
- Regular security updates for base images

## Integration with Claude Code Pipeline

The Docker integration follows the Claude Code pipeline methodology:

1. **Planning**: Use `/dev_environment` to analyze and plan deployments
2. **Implementation**: Containers are created with proper configuration
3. **Testing**: Built-in health checks and monitoring
4. **Documentation**: Automatic logging and status reporting
5. **Maintenance**: Easy cleanup and resource management

This ensures consistent, repeatable, and well-documented container management throughout your development workflow.
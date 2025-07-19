# Docker Container Management

I'll help you manage your Docker environment on the remote server (192.168.0.135:2375). This command provides safe container operations with built-in validations.

## Available Operations

### 1. Container Management
- **List Containers**: View running or all containers
- **Start/Stop Containers**: Control container lifecycle
- **Remove Containers**: Safely remove containers (with critical container protection)
- **View Logs**: Get container logs for debugging

### 2. Image Operations
- **Build Images**: Create images from Dockerfiles
- **Pull Images**: Download images from registries
- **List Images**: View available local images

### 3. System Information
- **Health Check**: Verify Docker server connectivity and status
- **System Info**: Get Docker server statistics and information

## Safety Features

- **Critical Container Protection**: Prevents removal of database, cache, and proxy containers
- **Validation Hooks**: Pre-execution validation for dangerous operations
- **Connection Recovery**: Automatic reconnection to Docker server
- **Error Handling**: Comprehensive error messages and recovery guidance

## Usage Examples

Tell me what you'd like to do with Docker:

- "List all containers"
- "Stop the nginx container"
- "Build an image from the current directory"
- "Show logs for the database container"
- "Check Docker server health"
- "Start a new Redis container"

I'll execute the appropriate Docker operations using the integrated DockerManager class, ensuring safe and validated container management.

## Container Templates

I can also help you set up common development environments:
- **Web Stack**: Nginx + Application + Database
- **API Stack**: Node.js/Python + Database + Redis
- **Monitoring**: Prometheus + Grafana + AlertManager
- **Database Cluster**: MySQL/PostgreSQL with replication

What would you like to do with your Docker environment?
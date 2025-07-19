# Docker API Reference

Complete API documentation for the DockerManager class and related components.

## DockerManager Class

The `DockerManager` class provides a comprehensive interface for Docker operations with built-in error handling and connection management.

### Constructor

```python
DockerManager(host: str = "192.168.0.135:2375") -> None
```

**Parameters:**
- `host` (str): Docker server host in format "ip:port"

**Example:**
```python
from docker_control import DockerManager

# Use default host
dm = DockerManager()

# Custom host
dm = DockerManager("localhost:2376")
```

## Container Management

### list_containers()

```python
list_containers(all: bool = False) -> List[Dict[str, str]]
```

List running containers or all containers.

**Parameters:**
- `all` (bool): If True, include stopped containers

**Returns:**
- List of container information dictionaries

**Response Format:**
```python
[
    {
        "id": "75be6c27fcdd",           # Container ID (12 chars)
        "name": "portainer",           # Container name
        "image": "portainer/portainer-ce:latest",  # Image name
        "status": "running",           # Container status
        "created": "2025-07-18T23:52:52.860563554Z",  # Creation timestamp
        "ports": "9000/tcp, 8999:9443/tcp"  # Port mappings
    }
]
```

**Example:**
```python
# List running containers
running = dm.list_containers()

# List all containers (including stopped)
all_containers = dm.list_containers(all=True)

for container in running:
    print(f"{container['name']}: {container['status']}")
```

### run_container()

```python
run_container(
    image: str,
    name: Optional[str] = None,
    ports: Optional[Dict[str, int]] = None,
    volumes: Optional[Dict[str, Dict[str, str]]] = None,
    environment: Optional[Dict[str, str]] = None,
    command: Optional[str] = None,
    detach: bool = True,
    remove: bool = False
) -> Dict[str, str]
```

Run a new container with comprehensive configuration options.

**Parameters:**
- `image` (str): Docker image name and tag
- `name` (Optional[str]): Container name
- `ports` (Optional[Dict[str, int]]): Port mapping {container_port: host_port}
- `volumes` (Optional[Dict[str, Dict[str, str]]]): Volume mapping
- `environment` (Optional[Dict[str, str]]): Environment variables
- `command` (Optional[str]): Command to run in container
- `detach` (bool): Run container in background (default: True)
- `remove` (bool): Remove container when it exits (default: False)

**Returns:**
- Container information dictionary

**Examples:**
```python
# Simple container
result = dm.run_container("nginx:latest", name="web-server")

# Container with port mapping
result = dm.run_container(
    image="nginx:latest",
    name="web-server",
    ports={"80": 8080}  # Host port 8080 -> Container port 80
)

# Container with environment variables and volumes
result = dm.run_container(
    image="postgres:13",
    name="database",
    ports={"5432": 5432},
    environment={
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "user",
        "POSTGRES_PASSWORD": "password"
    },
    volumes={
        "/host/data": {"bind": "/var/lib/postgresql/data", "mode": "rw"}
    }
)

# Non-detached container (blocks until completion)
result = dm.run_container(
    image="alpine:latest",
    command="echo 'Hello World'",
    detach=False
)
print(result["output"])  # "Hello World"
```

### stop_container()

```python
stop_container(container_id_or_name: str, timeout: int = 10) -> Dict[str, str]
```

Stop a running container.

**Parameters:**
- `container_id_or_name` (str): Container ID or name
- `timeout` (int): Seconds to wait before killing container (default: 10)

**Returns:**
- Container status information

**Example:**
```python
result = dm.stop_container("web-server", timeout=30)
print(f"Container {result['name']} {result['action']}")
```

### start_container()

```python
start_container(container_id_or_name: str) -> Dict[str, str]
```

Start a stopped container.

**Parameters:**
- `container_id_or_name` (str): Container ID or name

**Returns:**
- Container status information

**Example:**
```python
result = dm.start_container("web-server")
print(f"Container {result['name']} {result['action']}")
```

### remove_container()

```python
remove_container(container_id_or_name: str, force: bool = False) -> Dict[str, str]
```

Remove a container.

**Parameters:**
- `container_id_or_name` (str): Container ID or name
- `force` (bool): Force removal of running container (default: False)

**Returns:**
- Removal status information

**Example:**
```python
# Remove stopped container
result = dm.remove_container("web-server")

# Force remove running container
result = dm.remove_container("web-server", force=True)
```

### get_logs()

```python
get_logs(container_id_or_name: str, lines: int = 100, follow: bool = False) -> str
```

Get container logs.

**Parameters:**
- `container_id_or_name` (str): Container ID or name
- `lines` (int): Number of lines to retrieve (default: 100)
- `follow` (bool): Stream logs in real-time (default: False)

**Returns:**
- Container logs as string

**Example:**
```python
# Get last 100 lines
logs = dm.get_logs("web-server")
print(logs)

# Get last 500 lines
logs = dm.get_logs("web-server", lines=500)

# Stream logs (blocks)
logs = dm.get_logs("web-server", follow=True)
```

## Image Management

### build_image()

```python
build_image(path: str, tag: str, dockerfile: str = "Dockerfile") -> Dict[str, str]
```

Build a Docker image from a Dockerfile.

**Parameters:**
- `path` (str): Build context path
- `tag` (str): Image tag
- `dockerfile` (str): Dockerfile name (default: "Dockerfile")

**Returns:**
- Build result information

**Example:**
```python
# Build from current directory
result = dm.build_image(".", "myapp:latest")
print(f"Built image {result['tag']} with ID {result['id']}")
print("Build logs:")
print(result['logs'])

# Build with custom Dockerfile
result = dm.build_image("/path/to/app", "myapp:v1.0", dockerfile="Dockerfile.prod")
```

## System Information

### system_info()

```python
system_info() -> Dict[str, Any]
```

Get Docker system information.

**Returns:**
- System information dictionary

**Response Format:**
```python
{
    "containers": 8,                    # Total containers
    "containers_running": 6,            # Running containers
    "containers_paused": 0,             # Paused containers
    "containers_stopped": 2,            # Stopped containers
    "images": 15,                       # Total images
    "server_version": "20.10.7",        # Docker version
    "memory_total": 8589934592,         # Total memory (bytes)
    "memory_available": 4294967296,     # Available memory (bytes)
    "cpus": 4,                          # Number of CPUs
    "docker_root_dir": "/var/lib/docker",  # Docker root directory
    "operating_system": "Ubuntu 20.04", # OS information
    "architecture": "x86_64"            # System architecture
}
```

**Example:**
```python
info = dm.system_info()
print(f"Docker Version: {info['server_version']}")
print(f"Running Containers: {info['containers_running']}/{info['containers']}")
print(f"Total Images: {info['images']}")
print(f"Memory: {info['memory_available'] / (1024**3):.1f}GB available")
```

### health_check()

```python
health_check() -> Dict[str, Any]
```

Perform comprehensive health check of Docker environment.

**Returns:**
- Health check results

**Response Format:**
```python
{
    "connection": True,                 # Connection status
    "server_reachable": True,           # Server ping status
    "containers_accessible": True,      # Container listing access
    "images_accessible": True,          # Image listing access
    "error_details": []                 # List of error messages
}
```

**Example:**
```python
health = dm.health_check()
if health["connection"]:
    print("✅ Docker connection healthy")
else:
    print("❌ Docker connection failed")
    for error in health["error_details"]:
        print(f"Error: {error}")
```

## Error Handling

All methods include comprehensive error handling and raise appropriate exceptions:

### Common Exceptions

- `ConnectionError`: Docker server connection failed
- `ValueError`: Container/image not found
- `RuntimeError`: Operation failed (with detailed message)

### Exception Handling Examples

```python
try:
    containers = dm.list_containers()
except ConnectionError as e:
    print(f"Cannot connect to Docker server: {e}")
except RuntimeError as e:
    print(f"Docker operation failed: {e}")

try:
    dm.stop_container("nonexistent-container")
except ValueError as e:
    print(f"Container not found: {e}")
```

## Connection Management

### Automatic Reconnection

The DockerManager automatically handles connection issues:

```python
# Connection is established in constructor
dm = DockerManager()

# If connection is lost, it's automatically restored on next operation
containers = dm.list_containers()  # Reconnects if needed
```

### Manual Connection Testing

```python
# Test connection explicitly
try:
    health = dm.health_check()
    if health["connection"]:
        print("Connection OK")
except ConnectionError:
    print("Connection failed")
```

## CLI Integration

### Command Line Interface

The `docker_control.py` module includes a CLI interface:

```bash
# Available commands
python docker_control.py list           # List running containers
python docker_control.py list --all     # List all containers
python docker_control.py health         # Health check
python docker_control.py info           # System information
```

### Programmatic Usage

```python
# Import and use directly
from docker_control import main
import sys

# Simulate command line arguments
sys.argv = ["docker_control.py", "list", "--all"]
main()  # Executes list command
```

## Safety Validation

### Critical Container Protection

The Docker integration includes safety hooks that prevent dangerous operations:

```python
# These operations will be blocked by safety hooks
dm.remove_container("database")    # Blocked: critical container
dm.remove_container("redis")       # Blocked: critical container
dm.remove_container("nginx")       # Blocked: critical container

# Override with explicit understanding
dm.remove_container("database", force=True)  # Still blocked by hooks
```

### Validation Rules

- **Critical containers**: Cannot remove containers with names containing: database, db, mysql, postgres, postgresql, mongodb, mongo, redis, cache, elasticsearch, nginx, proxy, traefik
- **Base images**: Cannot remove base images without specific tags
- **Privileged containers**: Cannot create privileged containers
- **System networks**: Cannot create networks with reserved names

## Performance Considerations

### Batch Operations

For multiple operations, reuse the DockerManager instance:

```python
# Good: Reuse connection
dm = DockerManager()
for container_name in container_list:
    dm.stop_container(container_name)

# Avoid: Multiple connections
for container_name in container_list:
    dm = DockerManager()  # Creates new connection each time
    dm.stop_container(container_name)
```

### Large Log Retrieval

For large log files, use pagination:

```python
# Get logs in chunks
def get_all_logs(container_name, chunk_size=1000):
    all_logs = []
    offset = 0
    
    while True:
        logs = dm.get_logs(container_name, lines=chunk_size)
        if not logs:
            break
        all_logs.append(logs)
        offset += chunk_size
    
    return '\n'.join(all_logs)
```

## Thread Safety

The DockerManager class is not thread-safe. For concurrent operations, create separate instances:

```python
import threading

def worker(container_names):
    dm = DockerManager()  # Separate instance per thread
    for name in container_names:
        dm.stop_container(name)

# Create separate threads with separate DockerManager instances
threads = []
for chunk in container_chunks:
    thread = threading.Thread(target=worker, args=(chunk,))
    threads.append(thread)
    thread.start()
```
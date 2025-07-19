# Integrating Docker API with Claude Code Development Flow

Great news! The Docker API is working perfectly on your server. Now let's integrate this with Claude Code to enhance your development workflow:

## 1. Create a Docker Control Module

First, let's create a Python module that Claude Code can use to interact with your Docker server:

```python
# docker_control.py
import docker
import json
import os

class DockerManager:
    def __init__(self, host="192.168.0.135:2375"):
        self.client = docker.DockerClient(base_url=f"tcp://{host}")
    
    def list_containers(self, all=False):
        """List running containers or all containers if all=True"""
        containers = self.client.containers.list(all=all)
        return [{"id": c.id[:12], "name": c.name, "image": c.image.tags[0] if c.image.tags else c.image.id[:12], "status": c.status} for c in containers]
    
    def run_container(self, image, name=None, ports=None, volumes=None, environment=None, command=None, detach=True):
        """Run a new container"""
        container = self.client.containers.run(
            image, 
            name=name,
            ports=ports,
            volumes=volumes,
            environment=environment,
            command=command,
            detach=detach
        )
        return {"id": container.id[:12], "name": container.name}
    
    def stop_container(self, container_id_or_name):
        """Stop a container"""
        container = self.client.containers.get(container_id_or_name)
        container.stop()
        return {"id": container.id[:12], "name": container.name, "status": "stopped"}
    
    def remove_container(self, container_id_or_name, force=False):
        """Remove a container"""
        container = self.client.containers.get(container_id_or_name)
        container.remove(force=force)
        return {"id": container.id[:12], "status": "removed"}
    
    def get_logs(self, container_id_or_name, lines=100):
        """Get container logs"""
        container = self.client.containers.get(container_id_or_name)
        logs = container.logs(tail=lines).decode('utf-8')
        return logs
    
    def build_image(self, path, tag):
        """Build a Docker image from a Dockerfile"""
        image, build_logs = self.client.images.build(path=path, tag=tag)
        return {"id": image.id[:12], "tag": tag}
    
    def system_info(self):
        """Get Docker system information"""
        return self.client.info()
```

## 2. Create Claude Code Hooks for Docker

Set up custom hooks in your `.claude/hooks/` directory:

```python
# .claude/hooks/docker_pre_tool_use.py
#!/usr/bin/env python3
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from docker_control import DockerManager

def validate_docker_operation(operation, params):
    """Validate Docker operations before execution"""
    # Add your validation logic here
    # For example, prevent removing certain containers
    if operation == "remove_container" and params.get("container_id_or_name") in ["database", "redis"]:
        return False, "Cannot remove critical containers"
    return True, "Operation validated"

try:
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    
    # Check for Docker operations
    if "docker_operation" in tool_input:
        operation = tool_input.get("docker_operation")
        params = tool_input.get("docker_params", {})
        
        is_valid, message = validate_docker_operation(operation, params)
        if not is_valid:
            print(f"Docker operation validation failed: {message}", file=sys.stderr)
            sys.exit(2)  # Block with feedback to Claude
    
    # Exit normally if no issues found
    sys.exit(0)
    
except Exception as e:
    print(f"Docker hook error: {str(e)}", file=sys.stderr)
    sys.exit(1)
```

## 3. Add Docker Command Templates

Create command templates for Claude Code:

```markdown
# .claude/commands/docker.md
I'll help you manage your Docker environment on 192.168.0.135. What would you like to do?

Here are the available Docker operations:

1. **List Containers**
   - Show running containers or all containers

2. **Run Container**
   - Start a new container from an image
   - Configure ports, volumes, environment variables

3. **Build Image**
   - Build a new Docker image from a Dockerfile

4. **Manage Containers**
   - Stop, start, restart, or remove containers
   - View container logs

5. **System Information**
   - Show Docker system stats and information

Let me know which operation you'd like to perform, and I'll help you execute it.
```

## 4. Create Development Environment Templates

Add templates for common development environments:

```markdown
# .claude/commands/dev_environment.md
I'll set up a complete development environment using Docker. Based on your project, I'll:

1. Analyze your project requirements
2. Create appropriate Docker containers
3. Configure networking between services
4. Set up volumes for code persistence
5. Provide commands to start/stop the environment

Let me know what type of project you're working on, and I'll create a custom environment.
```

## 5. Update Settings.json to Include Docker Hooks

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Execute",
        "filePattern": "docker_*.py",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/docker_pre_tool_use.py"
          }
        ]
      },
      // Other existing hooks...
    ]
  }
}
```

## 6. Example Development Workflows with Claude Code

### Workflow 1: Quick Container Management

```
User: /docker list all containers

Claude: Let me check what containers are running on your Docker server.

[Executes docker_control.py with list_containers()]

Here are all containers on your Docker server (192.168.0.135):

| CONTAINER ID | NAME           | IMAGE              | STATUS    |
|--------------|----------------|-------------------- |-----------|
| 3f7a8e2d1b0c | mysql-db       | mysql:8.0          | running   |
| 9c4e2f1a8d7b | redis-cache    | redis:alpine       | running   |
| 5b3a1c9e7d2f | nginx-proxy    | nginx:latest       | exited    |

Would you like to manage any of these containers?
```

### Workflow 2: Setting Up a Development Environment

```
User: /dev_environment I need a Node.js API with MongoDB and Redis

Claude: I'll set up a development environment with Node.js, MongoDB, and Redis.

First, let me create a docker-compose.yml file for your project:

[Creates docker-compose.yml with node, mongodb, redis services]

Now I'll start the environment for you:

[Executes docker_control.py to run the services]

✅ Development environment is now running!

- Node.js API: http://192.168.0.135:3000
- MongoDB: mongodb://192.168.0.135:27017
- Redis: redis://192.168.0.135:6379

I've mounted the ./src directory into the Node.js container, so you can edit your code locally and it will automatically reflect in the container.

Would you like me to create a sample Node.js API that connects to both services?
```

### Workflow 3: Debugging Container Issues

```
User: My API container seems to be crashing. Can you help debug?

Claude: I'll help you debug the API container issue.

First, let me check the container logs:

[Executes docker_control.py to get container logs]

I see the error in the logs:

```
Error: Cannot connect to MongoDB at mongodb://mongo:27017
Connection refused
```

This looks like a networking issue between your containers. Let's check if MongoDB is running:

[Checks MongoDB container status]

I see the problem - your MongoDB container is not running. Let's fix that:

[Starts MongoDB container]

Now let's restart your API container:

[Restarts API container]

✅ Success! Your API container is now running correctly.

I recommend adding a retry mechanism in your API code for database connections. Would you like me to show you how to implement that?
```

## 7. Add a Docker Dashboard Script

Create a useful monitoring script Claude Code can use:

```python
# docker_dashboard.py
from docker_control import DockerManager
import time
import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_dashboard(refresh_seconds=5):
    """Display real-time Docker dashboard"""
    docker = DockerManager()
    
    try:
        while True:
            clear_screen()
            print("=== DOCKER DASHBOARD ===")
            print(f"Docker Host: 192.168.0.135:2375")
            print(f"Refreshing every {refresh_seconds} seconds. Press Ctrl+C to exit.")
            print("\n=== CONTAINERS ===")
            
            containers = docker.list_containers(all=True)
            if containers:
                print(f"{'CONTAINER ID':<15} {'NAME':<20} {'IMAGE':<30} {'STATUS':<15}")
                print("-" * 80)
                for container in containers:
                    print(f"{container['id']:<15} {container['name']:<20} {container['image']:<30} {container['status']:<15}")
            else:
                print("No containers found.")
                
            info = docker.system_info()
            print(f"\n=== SYSTEM INFO ===")
            print(f"Containers: {info['Containers']} (Running: {info['ContainersRunning']}, Paused: {info['ContainersPaused']}, Stopped: {info['ContainersStopped']})")
            print(f"Images: {info['Images']}")
            print(f"Server Version: {info['ServerVersion']}")
            print(f"Memory: {info['MemTotal'] / (1024**3):.2f} GB")
            
            time.sleep(refresh_seconds)
    except KeyboardInterrupt:
        print("\nExiting dashboard...")

if __name__ == "__main__":
    refresh = 5 if len(sys.argv) < 2 else int(sys.argv[1])
    display_dashboard(refresh)
```

This integration allows Claude Code to seamlessly control your Docker environment, helping you manage containers, debug issues, and set up complete development environments with simple natural language commands.
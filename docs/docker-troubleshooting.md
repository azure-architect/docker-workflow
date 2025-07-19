# Docker Integration Troubleshooting Guide

This guide helps resolve common issues with the Docker integration system.

## Installation Issues

### Docker Library Not Found

**Error:**
```
Docker library not installed. Install with: pip install docker
```

**Solution:**
```bash
pip install docker
```

**Alternative Solutions:**
```bash
# If using virtual environment
source venv/bin/activate
pip install docker

# If using conda
conda install docker-py

# If permission issues
pip install --user docker
```

### Import Errors

**Error:**
```
ImportError: No module named 'docker'
```

**Solutions:**
1. Verify installation:
   ```bash
   python -c "import docker; print(docker.__version__)"
   ```

2. Check Python path:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

3. Reinstall package:
   ```bash
   pip uninstall docker docker-py
   pip install docker
   ```

## Connection Issues

### Cannot Connect to Docker Server

**Error:**
```
ConnectionError: Cannot connect to Docker server: HTTPConnectionPool(host='192.168.0.135', port=2375)
```

**Diagnostic Steps:**

1. **Check Docker Server Status:**
   ```bash
   # On the Docker server (192.168.0.135)
   sudo systemctl status docker
   
   # Check if Docker daemon is listening on 2375
   sudo netstat -tlnp | grep 2375
   ```

2. **Test Network Connectivity:**
   ```bash
   # From your client machine
   telnet 192.168.0.135 2375
   
   # Alternative test
   curl http://192.168.0.135:2375/version
   ```

3. **Check Docker Daemon Configuration:**
   ```bash
   # On Docker server, check daemon configuration
   sudo cat /etc/docker/daemon.json
   
   # Should include:
   {
     "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
   }
   ```

4. **Firewall Issues:**
   ```bash
   # On Docker server, check firewall
   sudo ufw status
   sudo iptables -L
   
   # Allow Docker port if needed
   sudo ufw allow 2375
   ```

**Solutions:**

1. **Enable Docker Remote API:**
   ```bash
   # Method 1: Edit systemd service
   sudo systemctl edit docker.service
   
   # Add:
   [Service]
   ExecStart=
   ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375
   
   sudo systemctl daemon-reload
   sudo systemctl restart docker
   ```

2. **Alternative: Edit daemon.json:**
   ```bash
   sudo nano /etc/docker/daemon.json
   
   # Add:
   {
     "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
   }
   
   sudo systemctl restart docker
   ```

### SSL/TLS Errors

**Error:**
```
docker.errors.TLSParameterError: TLS configuration is required
```

**Solution:**
The system is configured for unencrypted communication. If your Docker server requires TLS:

```python
from docker_control import DockerManager

# For TLS-enabled Docker server
import docker
client = docker.DockerClient(
    base_url="tcp://192.168.0.135:2376",
    tls=True
)
```

## Runtime Issues

### Container Not Found

**Error:**
```
ValueError: Container container_name not found
```

**Diagnostic Steps:**
```python
# List all containers to verify name
dm = DockerManager()
containers = dm.list_containers(all=True)
for c in containers:
    print(f"Name: {c['name']}, ID: {c['id']}")
```

**Solutions:**
- Use exact container name (case-sensitive)
- Use container ID instead of name
- Check if container exists with `list_containers(all=True)`

### Permission Denied

**Error:**
```
docker.errors.APIError: 403 Client Error: Forbidden
```

**Solutions:**
1. **Check Docker server permissions:**
   ```bash
   # On Docker server
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Verify daemon socket permissions:**
   ```bash
   ls -la /var/run/docker.sock
   sudo chmod 666 /var/run/docker.sock  # Temporary fix
   ```

### Out of Disk Space

**Error:**
```
docker.errors.APIError: no space left on device
```

**Solutions:**
```bash
# Check disk usage
df -h

# Clean up Docker resources
docker system prune -a
docker volume prune
docker image prune -a

# Check Docker disk usage
docker system df
```

## Safety Hook Issues

### Operation Blocked by Safety Hooks

**Error:**
```
Docker operation validation failed: Cannot remove critical container 'database' - contains 'database'
```

**Understanding:**
This is intentional protection. Critical containers are protected by design.

**Solutions:**
1. **Review the operation** - Ensure you really want to remove this container
2. **Use alternative names** - Rename containers to avoid critical keywords
3. **Modify hook configuration** (advanced):
   ```python
   # Edit .claude/hooks/docker_pre_tool_use.py
   # Remove entries from CRITICAL_CONTAINERS set
   ```

### Hook Execution Failures

**Error:**
```
Hook execution failed: [python .claude/hooks/docker_pre_tool_use.py]
```

**Diagnostic Steps:**
```bash
# Test hook manually
echo '{"tool_name": "Bash", "tool_input": {"command": "docker ps"}}' | python .claude/hooks/docker_pre_tool_use.py
```

**Solutions:**
1. **Check hook permissions:**
   ```bash
   chmod +x .claude/hooks/docker_pre_tool_use.py
   ```

2. **Verify Python path:**
   ```bash
   which python
   head -1 .claude/hooks/docker_pre_tool_use.py
   ```

## Performance Issues

### Slow Container Operations

**Symptoms:**
- Container listing takes > 10 seconds
- Operations timeout frequently

**Diagnostic Steps:**
```python
import time
from docker_control import DockerManager

dm = DockerManager()
start = time.time()
containers = dm.list_containers()
print(f"List operation took: {time.time() - start:.2f} seconds")
```

**Solutions:**
1. **Check network latency:**
   ```bash
   ping 192.168.0.135
   ```

2. **Optimize Docker server:**
   ```bash
   # On Docker server
   docker system prune
   sudo systemctl restart docker
   ```

3. **Reduce container count:**
   - Remove unused containers
   - Archive old containers

### Memory Issues

**Error:**
```
MemoryError: Unable to allocate memory
```

**Solutions:**
1. **Increase system memory**
2. **Reduce log retrieval size:**
   ```python
   # Instead of getting all logs
   logs = dm.get_logs("container", lines=100)  # Limit lines
   ```

3. **Process containers in batches:**
   ```python
   containers = dm.list_containers(all=True)
   for batch in chunks(containers, 10):  # Process 10 at a time
       process_batch(batch)
   ```

## Dashboard Issues

### Dashboard Won't Start

**Error:**
```
Failed to start dashboard: Cannot connect to Docker server
```

**Solutions:**
1. **Verify Docker connection first:**
   ```bash
   python docker_control.py health
   ```

2. **Check terminal compatibility:**
   ```bash
   # Try with specific terminal
   TERM=xterm python docker_dashboard.py
   ```

3. **Run with debug output:**
   ```bash
   python docker_dashboard.py --refresh 10  # Slower refresh
   ```

### Display Issues

**Symptoms:**
- Garbled text
- Missing Unicode characters
- Incorrect colors

**Solutions:**
1. **Set proper terminal encoding:**
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

2. **Use alternative terminal:**
   - Try different terminal emulator
   - Use SSH with proper encoding

3. **Disable Unicode:**
   ```python
   # Modify dashboard to use ASCII-only characters
   # Edit docker_dashboard.py, replace Unicode symbols
   ```

## Development Environment Issues

### Environment Creation Fails

**Error:**
```
RuntimeError: Container creation failed: port already in use
```

**Solutions:**
1. **Check port conflicts:**
   ```bash
   # Find what's using the port
   sudo netstat -tlnp | grep :8080
   sudo lsof -i :8080
   ```

2. **Use different ports:**
   ```python
   dm.run_container(
       "nginx:latest",
       ports={"80": 8081}  # Use different host port
   )
   ```

3. **Stop conflicting services:**
   ```bash
   # Stop containers using the port
   docker stop $(docker ps -q --filter "publish=8080")
   ```

### Volume Mount Issues

**Error:**
```
docker.errors.APIError: invalid mount config
```

**Solutions:**
1. **Check path exists:**
   ```bash
   ls -la /host/path
   ```

2. **Use absolute paths:**
   ```python
   volumes = {
       "/absolute/host/path": {"bind": "/container/path", "mode": "rw"}
   }
   ```

3. **Check permissions:**
   ```bash
   # Ensure Docker can access the path
   sudo chown -R $USER:docker /host/path
   chmod -R 755 /host/path
   ```

## Debugging Tips

### Enable Detailed Logging

```python
import logging

# Enable debug logging for Docker library
logging.basicConfig(level=logging.DEBUG)
docker_logger = logging.getLogger('docker')
docker_logger.setLevel(logging.DEBUG)

# Enable debug logging for our module
logging.getLogger('docker_control').setLevel(logging.DEBUG)
```

### Inspect Docker API Calls

```python
import docker

# Create client with debug
client = docker.DockerClient(
    base_url="tcp://192.168.0.135:2375",
    timeout=30
)

# Manual API calls for debugging
try:
    version = client.version()
    print(f"Docker version: {version}")
except Exception as e:
    print(f"Version check failed: {e}")
```

### Test Individual Components

```python
# Test connection only
from docker_control import DockerManager
try:
    dm = DockerManager()
    print("✅ Connection successful")
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Test specific operations
try:
    containers = dm.list_containers()
    print(f"✅ Listed {len(containers)} containers")
except Exception as e:
    print(f"❌ List failed: {e}")
```

## Getting Help

### Diagnostic Information Collection

When reporting issues, include:

```bash
# System information
python --version
pip show docker

# Docker server information
python docker_control.py info

# Network connectivity
ping 192.168.0.135
telnet 192.168.0.135 2375

# Health check
python docker_control.py health
```

### Common Diagnostic Commands

```bash
# Check Docker daemon logs (on server)
sudo journalctl -u docker.service -f

# Check if Docker API is accessible
curl http://192.168.0.135:2375/version

# Test container operations
python -c "
from docker_control import DockerManager
dm = DockerManager()
print('Health:', dm.health_check())
print('Containers:', len(dm.list_containers(all=True)))
"
```

### Support Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Python SDK**: https://docker-py.readthedocs.io/
- **Project Issues**: Check existing project documentation
- **Docker Community**: https://forums.docker.com/

## Recovery Procedures

### Complete System Reset

If all else fails, reset the Docker integration:

```bash
# 1. Stop all containers
python -c "
from docker_control import DockerManager
dm = DockerManager()
containers = dm.list_containers(all=True)
for c in containers:
    try:
        dm.stop_container(c['name'])
        dm.remove_container(c['name'], force=True)
    except:
        pass
"

# 2. Clean Docker system
docker system prune -a --volumes

# 3. Restart Docker daemon (on server)
sudo systemctl restart docker

# 4. Test connection
python docker_control.py health
```

### Reinstall Docker Integration

```bash
# 1. Remove Python cache
rm -rf __pycache__ .mypy_cache

# 2. Reinstall Docker library
pip uninstall docker
pip install docker

# 3. Test components
python docker_control.py health
python -c "from docker_control import DockerManager; print('Import successful')"
```
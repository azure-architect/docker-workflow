#!/usr/bin/env python3
"""
Docker Control Module for Claude Code Integration

Provides comprehensive Docker API control capabilities for managing containers,
images, and development environments on remote Docker servers.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

try:
    import docker  # type: ignore
except ImportError:
    print("Docker library not installed. Install with: pip install docker")
    sys.exit(1)


class DockerManager:
    """
    Comprehensive Docker management interface for Claude Code integration.

    Connects to remote Docker server and provides safe container operations
    with built-in validation and error handling.
    """

    def __init__(self, host: str = "192.168.0.135:2375") -> None:
        """
        Initialize Docker client connection.

        Args:
            host: Docker server host in format "ip:port"
        """
        self.host = host
        self.base_url = f"tcp://{host}"
        self.client: docker.DockerClient
        self._connect()

    def _connect(self) -> None:
        """Establish connection to Docker server with error handling."""
        try:
            self.client = docker.DockerClient(base_url=self.base_url)
            # Test connection
            self.client.ping()
            logging.info(f"Successfully connected to Docker server at {self.host}")
        except Exception as e:
            logging.error(
                f"Failed to connect to Docker server at {self.host}: {str(e)}"
            )
            raise ConnectionError(f"Cannot connect to Docker server: {str(e)}")

    def _ensure_connected(self) -> None:
        """Ensure Docker client is connected, reconnect if necessary."""
        try:
            self.client.ping()
        except Exception:
            logging.warning("Docker connection lost, attempting to reconnect...")
            self._connect()

    def list_containers(self, all: bool = False) -> List[Dict[str, str]]:
        """
        List running containers or all containers.

        Args:
            all: If True, include stopped containers

        Returns:
            List of container information dictionaries
        """
        self._ensure_connected()

        try:
            containers = self.client.containers.list(all=all)
            result = []

            for container in containers:
                # Get image tag or ID
                image_name = "unknown"
                if container.image.tags:
                    image_name = container.image.tags[0]
                else:
                    image_name = container.image.id[:12]

                result.append(
                    {
                        "id": container.id[:12],
                        "name": container.name,
                        "image": image_name,
                        "status": container.status,
                        "created": container.attrs.get("Created", "unknown"),
                        "ports": self._format_ports(container.ports),
                    }
                )

            return result

        except Exception as e:
            logging.error(f"Failed to list containers: {str(e)}")
            raise RuntimeError(f"Container listing failed: {str(e)}")

    def run_container(
        self,
        image: str,
        name: Optional[str] = None,
        ports: Optional[Dict[str, int]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        environment: Optional[Dict[str, str]] = None,
        command: Optional[str] = None,
        detach: bool = True,
        remove: bool = False,
    ) -> Dict[str, str]:
        """
        Run a new container with comprehensive configuration options.

        Args:
            image: Docker image name and tag
            name: Container name (optional)
            ports: Port mapping dictionary {container_port: host_port}
            volumes: Volume mapping dictionary
            environment: Environment variables
            command: Command to run in container
            detach: Run container in background
            remove: Remove container when it exits

        Returns:
            Container information dictionary
        """
        self._ensure_connected()

        try:
            # Validate image exists or can be pulled
            try:
                self.client.images.get(image)
            except docker.errors.ImageNotFound:
                logging.info(f"Image {image} not found locally, attempting to pull...")
                self.client.images.pull(image)

            container = self.client.containers.run(
                image=image,
                name=name,
                ports=ports,
                volumes=volumes,
                environment=environment,
                command=command,
                detach=detach,
                remove=remove,
            )

            if detach:
                return {
                    "id": container.id[:12],
                    "name": container.name,
                    "image": image,
                    "status": "running",
                }
            else:
                return {
                    "id": "non-detached",
                    "output": (
                        container.decode("utf-8")
                        if isinstance(container, bytes)
                        else str(container)
                    ),
                }

        except Exception as e:
            logging.error(f"Failed to run container {image}: {str(e)}")
            raise RuntimeError(f"Container creation failed: {str(e)}")

    def stop_container(
        self, container_id_or_name: str, timeout: int = 10
    ) -> Dict[str, str]:
        """
        Stop a running container.

        Args:
            container_id_or_name: Container ID or name
            timeout: Seconds to wait before killing container

        Returns:
            Container status information
        """
        self._ensure_connected()

        try:
            container = self.client.containers.get(container_id_or_name)
            container.stop(timeout=timeout)

            return {
                "id": container.id[:12],
                "name": container.name,
                "status": "stopped",
                "action": "stopped",
            }

        except docker.errors.NotFound:
            raise ValueError(f"Container {container_id_or_name} not found")
        except Exception as e:
            logging.error(f"Failed to stop container {container_id_or_name}: {str(e)}")
            raise RuntimeError(f"Container stop failed: {str(e)}")

    def start_container(self, container_id_or_name: str) -> Dict[str, str]:
        """
        Start a stopped container.

        Args:
            container_id_or_name: Container ID or name

        Returns:
            Container status information
        """
        self._ensure_connected()

        try:
            container = self.client.containers.get(container_id_or_name)
            container.start()

            return {
                "id": container.id[:12],
                "name": container.name,
                "status": "running",
                "action": "started",
            }

        except docker.errors.NotFound:
            raise ValueError(f"Container {container_id_or_name} not found")
        except Exception as e:
            logging.error(f"Failed to start container {container_id_or_name}: {str(e)}")
            raise RuntimeError(f"Container start failed: {str(e)}")

    def remove_container(
        self, container_id_or_name: str, force: bool = False
    ) -> Dict[str, str]:
        """
        Remove a container.

        Args:
            container_id_or_name: Container ID or name
            force: Force removal of running container

        Returns:
            Removal status information
        """
        self._ensure_connected()

        try:
            container = self.client.containers.get(container_id_or_name)
            container_info = {"id": container.id[:12], "name": container.name}

            container.remove(force=force)

            return {**container_info, "status": "removed", "action": "removed"}

        except docker.errors.NotFound:
            raise ValueError(f"Container {container_id_or_name} not found")
        except Exception as e:
            logging.error(
                f"Failed to remove container {container_id_or_name}: {str(e)}"
            )
            raise RuntimeError(f"Container removal failed: {str(e)}")

    def get_logs(
        self, container_id_or_name: str, lines: int = 100, follow: bool = False
    ) -> str:
        """
        Get container logs.

        Args:
            container_id_or_name: Container ID or name
            lines: Number of lines to retrieve
            follow: Stream logs in real-time

        Returns:
            Container logs as string
        """
        self._ensure_connected()

        try:
            container = self.client.containers.get(container_id_or_name)
            logs = container.logs(tail=lines, follow=follow, stream=False)
            return logs.decode("utf-8", errors="replace")

        except docker.errors.NotFound:
            raise ValueError(f"Container {container_id_or_name} not found")
        except Exception as e:
            logging.error(f"Failed to get logs for {container_id_or_name}: {str(e)}")
            raise RuntimeError(f"Log retrieval failed: {str(e)}")

    def build_image(
        self, path: str, tag: str, dockerfile: str = "Dockerfile"
    ) -> Dict[str, str]:
        """
        Build a Docker image from a Dockerfile.

        Args:
            path: Build context path
            tag: Image tag
            dockerfile: Dockerfile name

        Returns:
            Build result information
        """
        self._ensure_connected()

        try:
            image, build_logs = self.client.images.build(
                path=path, tag=tag, dockerfile=dockerfile, rm=True
            )

            # Collect build output
            log_output = []
            for log in build_logs:
                if "stream" in log:
                    log_output.append(log["stream"].strip())

            return {
                "id": image.id[:12],
                "tag": tag,
                "status": "built",
                "logs": "\n".join(log_output),
            }

        except Exception as e:
            logging.error(f"Failed to build image {tag}: {str(e)}")
            raise RuntimeError(f"Image build failed: {str(e)}")

    def system_info(self) -> Dict[str, Any]:
        """
        Get Docker system information.

        Returns:
            System information dictionary
        """
        self._ensure_connected()

        try:
            info = self.client.info()

            # Extract key information
            return {
                "containers": info.get("Containers", 0),
                "containers_running": info.get("ContainersRunning", 0),
                "containers_paused": info.get("ContainersPaused", 0),
                "containers_stopped": info.get("ContainersStopped", 0),
                "images": info.get("Images", 0),
                "server_version": info.get("ServerVersion", "unknown"),
                "memory_total": info.get("MemTotal", 0),
                "memory_available": info.get("MemTotal", 0)
                - info.get("MemTotal", 0)
                + info.get("MemAvailable", 0),
                "cpus": info.get("NCPU", 0),
                "docker_root_dir": info.get("DockerRootDir", "unknown"),
                "operating_system": info.get("OperatingSystem", "unknown"),
                "architecture": info.get("Architecture", "unknown"),
            }

        except Exception as e:
            logging.error(f"Failed to get system info: {str(e)}")
            raise RuntimeError(f"System info retrieval failed: {str(e)}")

    def _format_ports(self, ports: Dict[str, Any]) -> str:
        """Format container ports for display."""
        if not ports:
            return "none"

        port_list = []
        for container_port, host_bindings in ports.items():
            if host_bindings:
                for binding in host_bindings:
                    host_port = binding.get("HostPort", "?")
                    port_list.append(f"{host_port}:{container_port}")
            else:
                port_list.append(container_port)

        return ", ".join(port_list) if port_list else "none"

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of Docker environment.

        Returns:
            Health check results
        """
        results: Dict[str, Any] = {
            "connection": False,
            "server_reachable": False,
            "containers_accessible": False,
            "images_accessible": False,
            "error_details": [],
        }

        try:
            # Test connection
            self._ensure_connected()
            results["connection"] = True

            # Test server ping
            self.client.ping()
            results["server_reachable"] = True

            # Test container listing
            self.client.containers.list()
            results["containers_accessible"] = True

            # Test image listing
            self.client.images.list()
            results["images_accessible"] = True

        except Exception as e:
            error_details = results["error_details"]
            if isinstance(error_details, list):
                error_details.append(str(e))

        return results


def main() -> None:
    """CLI interface for Docker control module."""
    if len(sys.argv) < 2:
        print("Usage: python docker_control.py <command> [args...]")
        print("Commands: list, run, stop, start, remove, logs, build, info, health")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        docker_manager = DockerManager()
        command = sys.argv[1]

        if command == "list":
            all_containers = "--all" in sys.argv
            containers = docker_manager.list_containers(all=all_containers)
            print(json.dumps(containers, indent=2))

        elif command == "health":
            health = docker_manager.health_check()
            print(json.dumps(health, indent=2))

        elif command == "info":
            info = docker_manager.system_info()
            print(json.dumps(info, indent=2))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

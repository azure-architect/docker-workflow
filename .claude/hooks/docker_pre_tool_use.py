#!/usr/bin/env python3
"""
Docker-specific pre-tool validation hook for Claude Code.

Validates Docker operations before execution to prevent dangerous operations
and ensure safe container management.
"""

import json
import os
import sys
from typing import Any, Dict, Tuple

# Critical containers that should never be removed
CRITICAL_CONTAINERS = {
    "database",
    "db",
    "mysql",
    "postgres",
    "postgresql",
    "mongodb",
    "mongo",
    "redis",
    "cache",
    "elasticsearch",
    "nginx",
    "proxy",
    "traefik",
}

# Dangerous Docker operations that require extra validation
DANGEROUS_OPERATIONS = {"remove_container", "remove_image", "prune", "system_prune"}


def validate_docker_operation(
    operation: str, params: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Validate Docker operations before execution.

    Args:
        operation: Docker operation name
        params: Operation parameters

    Returns:
        Tuple of (is_valid, message)
    """

    # Validate container removal operations
    if operation == "remove_container":
        container_name = params.get("container_id_or_name", "")

        # Check if trying to remove critical containers
        for critical in CRITICAL_CONTAINERS:
            if critical.lower() in container_name.lower():
                return (
                    False,
                    f"Cannot remove critical container '{container_name}' - contains '{critical}'",
                )

        # Require explicit force flag for running containers
        if not params.get("force", False):
            return True, "Container removal validated (stopped containers only)"
        else:
            return True, "Container removal validated with force flag"

    # Validate image operations
    elif operation == "remove_image":
        image_name = params.get("image", "")

        # Prevent removal of base images
        base_images = [
            "ubuntu",
            "alpine",
            "debian",
            "centos",
            "python",
            "node",
            "nginx",
        ]
        for base in base_images:
            if base in image_name.lower() and ":" not in image_name:
                return (
                    False,
                    f"Cannot remove base image '{image_name}' without specific tag",
                )

    # Validate container creation
    elif operation == "run_container":
        image = params.get("image", "")

        # Warn about potentially dangerous images
        if any(dangerous in image.lower() for dangerous in ["latest", "untrusted"]):
            return True, f"Warning: Using potentially unsafe image '{image}'"

        # Check for privileged mode
        if params.get("privileged", False):
            return False, "Privileged container creation not allowed for security"

    # Validate network operations
    elif operation == "create_network":
        network_name = params.get("name", "")

        # Prevent conflicts with system networks
        system_networks = ["bridge", "host", "none", "docker0"]
        if network_name in system_networks:
            return False, f"Cannot create network with reserved name '{network_name}'"

    # All other operations are allowed
    return True, f"Docker operation '{operation}' validated"


def main() -> None:
    """Main hook entry point."""
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only validate if this is a Docker-related operation
        if tool_name == "Bash" and "docker" in tool_input.get("command", ""):
            # Parse Docker command for dangerous operations
            command = tool_input.get("command", "")

            # Check for dangerous Docker commands
            if any(
                dangerous in command
                for dangerous in ["docker rm", "docker rmi", "docker system prune"]
            ):
                print(
                    "Docker command contains potentially dangerous operations. Please use docker_control.py for safer container management.",
                    file=sys.stderr,
                )
                sys.exit(2)  # Block with feedback

        # Check for docker_control.py operations
        elif "docker_operation" in tool_input:
            operation = tool_input.get("docker_operation")
            params = tool_input.get("docker_params", {})

            is_valid, message = validate_docker_operation(operation, params)

            if not is_valid:
                print(f"Docker operation validation failed: {message}", file=sys.stderr)
                sys.exit(2)  # Block with feedback to Claude
            else:
                # Log validation success (optional)
                print(f"Docker validation: {message}", file=sys.stderr)

        # Exit normally if no issues found
        sys.exit(0)

    except json.JSONDecodeError:
        print("Invalid JSON input to Docker hook", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Docker hook error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Docker Dashboard - Real-time monitoring for Docker environments.

Provides a live dashboard showing container status, system resources,
and health information for the Docker server.
"""

import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

try:
    from docker_control import DockerManager
except ImportError:
    print(
        "Error: docker_control.py not found. Please ensure it's in the same directory."
    )
    sys.exit(1)


class DockerDashboard:
    """Real-time Docker dashboard with monitoring capabilities."""

    def __init__(self, host: str = "192.168.0.135:2375") -> None:
        """Initialize dashboard with Docker connection."""
        self.docker_manager = DockerManager(host)
        self.running = True
        self.last_update = datetime.now()

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully."""
        print("\n\nShutting down dashboard...")
        self.running = False

    def _clear_screen(self) -> None:
        """Clear the terminal screen using subprocess."""
        try:
            if os.name == "nt":
                subprocess.run(["cls"], shell=True, check=False)
            else:
                subprocess.run(["clear"], check=False)
        except Exception:
            # Fallback to ANSI escape sequences
            print("\033[2J\033[H", end="")

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable units."""
        float_value = float(bytes_value)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if float_value < 1024.0:
                return f"{float_value:.1f} {unit}"
            float_value /= 1024.0
        return f"{float_value:.1f} PB"

    def _format_uptime(self, created: str) -> str:
        """Calculate and format container uptime."""
        try:
            # Simple uptime calculation - would need proper parsing for production
            return "Running"
        except Exception:
            return "Unknown"

    def _get_container_summary(self) -> Dict[str, Any]:
        """Get summary statistics for containers."""
        try:
            containers = self.docker_manager.list_containers(all=True)
            summary = {
                "running": 0,
                "stopped": 0,
                "paused": 0,
                "total": len(containers),
            }

            for container in containers:
                status = container.get("status", "").lower()
                if "running" in status:
                    summary["running"] += 1
                elif "paused" in status:
                    summary["paused"] += 1
                else:
                    summary["stopped"] += 1

            return summary
        except Exception as e:
            return {
                "error": str(e),
                "running": 0,
                "stopped": 0,
                "paused": 0,
                "total": 0,
            }

    def _display_header(self, refresh_seconds: int) -> None:
        """Display dashboard header with connection info."""
        print("=" * 80)
        print("🐳 DOCKER DASHBOARD")
        print("=" * 80)
        print(f"Docker Host: {self.docker_manager.host}")
        print(f"Last Update: {self.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Refresh Rate: {refresh_seconds}s | Press Ctrl+C to exit")
        print("=" * 80)

    def _display_system_info(self) -> None:
        """Display Docker system information."""
        try:
            info = self.docker_manager.system_info()
            print("\n📊 SYSTEM INFORMATION")
            print("-" * 50)
            print(f"Server Version: {info.get('server_version', 'Unknown')}")
            print(f"Operating System: {info.get('operating_system', 'Unknown')}")
            print(f"Architecture: {info.get('architecture', 'Unknown')}")
            print(f"CPUs: {info.get('cpus', 'Unknown')}")

            if info.get("memory_total", 0) > 0:
                total_mem = self._format_bytes(info["memory_total"])
                print(f"Total Memory: {total_mem}")

            print(f"Total Images: {info.get('images', 0)}")

        except Exception as e:
            print(f"\n❌ System Info Error: {str(e)}")

    def _display_container_summary(self) -> None:
        """Display container summary statistics."""
        summary = self._get_container_summary()

        print("\n📋 CONTAINER SUMMARY")
        print("-" * 50)

        if "error" in summary:
            print(f"❌ Error: {summary['error']}")
        else:
            print(f"Total Containers: {summary['total']}")
            print(f"🟢 Running: {summary['running']}")
            print(f"🔴 Stopped: {summary['stopped']}")
            print(f"⏸️  Paused: {summary['paused']}")

    def _display_containers(self) -> None:
        """Display detailed container information."""
        try:
            containers = self.docker_manager.list_containers(all=True)

            print("\n🐳 CONTAINERS")
            print("-" * 80)

            if not containers:
                print("No containers found.")
                return

            # Header
            print(f"{'ID':<12} {'NAME':<20} {'IMAGE':<25} {'STATUS':<15} {'PORTS':<15}")
            print("-" * 80)

            # Container details
            for container in containers:
                container_id = container.get("id", "Unknown")[:12]
                name = container.get("name", "Unknown")[:20]
                image = container.get("image", "Unknown")[:25]
                status = container.get("status", "Unknown")[:15]
                ports = container.get("ports", "none")[:15]

                # Color code by status
                status_icon = "🟢" if "running" in status.lower() else "🔴"
                print(
                    f"{container_id:<12} {name:<20} {image:<25} {status_icon} {status:<13} {ports:<15}"
                )

        except Exception as e:
            print(f"\n❌ Container List Error: {str(e)}")

    def _display_health_status(self) -> None:
        """Display Docker server health status."""
        try:
            health = self.docker_manager.health_check()

            print("\n🏥 HEALTH STATUS")
            print("-" * 50)

            status_items = [
                ("Connection", health.get("connection", False)),
                ("Server Reachable", health.get("server_reachable", False)),
                ("Containers Accessible", health.get("containers_accessible", False)),
                ("Images Accessible", health.get("images_accessible", False)),
            ]

            for item, status in status_items:
                icon = "✅" if status else "❌"
                print(f"{icon} {item}")

            if health.get("error_details"):
                print("\n🚨 Errors:")
                for error in health["error_details"]:
                    print(f"  - {error}")

        except Exception as e:
            print(f"\n❌ Health Check Error: {str(e)}")

    def display_dashboard(self, refresh_seconds: int = 5) -> None:
        """
        Display real-time Docker dashboard.

        Args:
            refresh_seconds: Seconds between dashboard updates
        """
        try:
            while self.running:
                self._clear_screen()
                self.last_update = datetime.now()

                # Display all dashboard sections
                self._display_header(refresh_seconds)
                self._display_system_info()
                self._display_container_summary()
                self._display_containers()
                self._display_health_status()

                print(f"\n{'='*80}")
                print("Dashboard will refresh automatically. Press Ctrl+C to exit.")

                # Sleep with interrupt handling
                for _ in range(refresh_seconds):
                    if not self.running:
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            print("\n\nDashboard stopped by user.")
        except Exception as e:
            print(f"\n❌ Dashboard Error: {str(e)}")
        finally:
            print("Dashboard shutdown complete.")


def main() -> None:
    """CLI interface for Docker dashboard."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Docker Dashboard - Real-time monitoring"
    )
    parser.add_argument(
        "--refresh",
        "-r",
        type=int,
        default=5,
        help="Refresh interval in seconds (default: 5)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="192.168.0.135:2375",
        help="Docker host (default: 192.168.0.135:2375)",
    )

    args = parser.parse_args()

    # Validate refresh interval
    if args.refresh < 1:
        print("Error: Refresh interval must be at least 1 second")
        sys.exit(1)

    try:
        dashboard = DockerDashboard(host=args.host)
        print(f"Starting Docker Dashboard for {args.host}...")
        print("Press Ctrl+C to exit\n")
        time.sleep(2)  # Brief pause before starting

        dashboard.display_dashboard(refresh_seconds=args.refresh)

    except Exception as e:
        print(f"Failed to start dashboard: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

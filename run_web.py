"""OraCLI 10G Web Launcher.

Automatically ensures the virtual environment is active, checks port availability,
and starts the FastAPI + React unified server.
"""

import socket
import subprocess
import sys
from pathlib import Path


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a TCP port is currently occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def find_free_port(start_port: int = 8000, host: str = "127.0.0.1") -> int:
    """Find an available port starting from start_port."""
    port = start_port
    while port < start_port + 100:
        if not is_port_in_use(port, host):
            return port
        port += 1
    return start_port


def main():
    project_root = Path(__file__).resolve().parent

    # Parse port argument if provided
    port = 8000
    if "--port" in sys.argv:
        try:
            port_idx = sys.argv.index("--port") + 1
            port = int(sys.argv[port_idx])
        except (IndexError, ValueError):
            pass

    # If default port 8000 is occupied, auto-fallback or alert
    if is_port_in_use(port):
        free_port = find_free_port(port + 1)
        print(f"[!] Note: Port {port} is already in use by another process.")
        print(f"[*] Automatically switching to available port: {free_port}")
        port = free_port

    # Check if we are running in the project virtual environment
    in_venv = sys.prefix != sys.base_prefix

    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = project_root / ".venv" / "bin" / "python"

    # If not in venv and venv exists, re-exec with venv python
    if not in_venv and venv_python.exists():
        print(f"[*] Activating virtual environment: {venv_python}")
        cmd = [
            str(venv_python),
            "-m",
            "uvicorn",
            "app.api.server:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ]
        try:
            sys.exit(subprocess.call(cmd, cwd=str(project_root)))
        except KeyboardInterrupt:
            print("\nServer stopped.")
            sys.exit(0)

    # Otherwise run uvicorn in current interpreter
    try:
        import uvicorn

        from app.api.server import app

        print("=" * 60)
        print("  OraCLI 10G Web - Educational Environment")
        print(f"  Server running at: http://127.0.0.1:{port}")
        print("=" * 60)
        uvicorn.run(app, host="127.0.0.1", port=port)
    except ImportError as e:
        print(f"\n[!] Missing dependency: {e}")
        print("\nPlease run:")
        print("    .\\.venv\\Scripts\\activate")
        print(f"    python -m uvicorn app.api.server:app --host 127.0.0.1 --port {port}")
        print("\nOr directly:")
        print(f"    .\\.venv\\Scripts\\python.exe -m uvicorn app.api.server:app --port {port}")
        sys.exit(1)


if __name__ == "__main__":
    main()

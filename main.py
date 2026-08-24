"""OraCLI 10G - Oracle 10g SQL*Plus-Compatible Educational Environment CLI Launcher."""

import subprocess
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parent

    # Check if we are running in the project virtual environment
    in_venv = sys.prefix != sys.base_prefix

    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = project_root / ".venv" / "bin" / "python"

    # If not in venv and venv exists, re-exec with venv python
    if not in_venv and venv_python.exists():
        cmd = [str(venv_python), "-m", "app.cli.terminal"] + sys.argv[1:]
        try:
            sys.exit(subprocess.call(cmd, cwd=str(project_root)))
        except KeyboardInterrupt:
            sys.exit(0)

    # Otherwise run directly in current interpreter
    try:
        from app.cli.terminal import main as cli_main

        cli_main()
    except ImportError as e:
        print(f"\n[!] Missing dependency: {e}")
        print("\nPlease activate the virtual environment or run with .venv:")
        print("    .\\.venv\\Scripts\\activate")
        print("    python main.py")
        print("\nOr directly:")
        print("    .\\.venv\\Scripts\\python.exe main.py")
        sys.exit(1)


if __name__ == "__main__":
    main()

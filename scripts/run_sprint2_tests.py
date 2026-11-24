#!/usr/bin/env python3
"""Run UWI Connect pytest tests against an isolated temporary SQLite database.

Use this instead of bare `pytest tests`: inherited test_scenario.py calls
`seed(reset=True)`, which can reset the configured development database.

Examples:
    py scripts/run_sprint2_tests.py tests/test_sprint2_workflows.py -v
    py scripts/run_sprint2_tests.py tests -v
    py scripts/run_sprint2_tests.py tests --cov=app --cov-report=term-missing
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    arguments = sys.argv[1:] or ["tests", "-v"]
    with tempfile.TemporaryDirectory(prefix="stacksync_pytest_") as tmp:
        db_path = (Path(tmp) / "pytest_database.db").resolve()
        env = os.environ.copy()
        # Using URI path (forward slashes) works on both Windows and Linux.
        env["DATABASE_URI"] = "sqlite:///" + db_path.as_posix()
        env.setdefault("ENV", "development")
        env.setdefault("SECRET_KEY", "stacksync-local-test-only-key")
        command = [sys.executable, "-m", "pytest", *arguments]
        print("Database: temporary isolated SQLite file (removed after test run)", flush=True)
        print("Command:", " ".join(command), flush=True)
        return subprocess.call(command, cwd=repo_root, env=env)


if __name__ == "__main__":
    raise SystemExit(main())

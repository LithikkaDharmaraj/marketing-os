#!/usr/bin/env python3
"""Run initial database migration."""
import subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from shared.config import get_settings

settings = get_settings()

print(f"Running migration against: {settings.database_url_sync}")
result = subprocess.run(
    ["psql", settings.database_url_sync, "-f", "migrations/versions/0001_initial_schema.sql"],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
    sys.exit(1)
print("Database initialized successfully.")

#!/usr/bin/env python3

import argparse
import os
import platform
import shutil
import sqlite3
import sys
from pathlib import Path


def install_hints() -> list[str]:
    system = platform.system().lower()
    if system == "darwin":
        return [
            "brew install python sqlite",
        ]
    if system == "linux":
        return [
            "sudo apt-get update && sudo apt-get install -y python3 sqlite3",
        ]
    return [
        "Install Python 3.9+ and SQLite 3.x, then re-run this check.",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the local environment required by the HRDB skill.")
    parser.add_argument("--db", default="./hrdb.db", help="Target SQLite database path.")
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []

    if sys.version_info < (3, 9):
        failures.append(f"Python 3.9+ required, found {platform.python_version()}.")

    sqlite_version = sqlite3.sqlite_version
    sqlite_cli = shutil.which("sqlite3")
    if sqlite_cli is None:
        warnings.append("sqlite3 CLI not found; Python's sqlite3 module is available, but CLI inspection commands will be unavailable.")

    db_path = Path(args.db).expanduser()
    parent = db_path.parent
    if not parent.exists():
        warnings.append(f"Database parent directory does not exist yet: {parent}")
    else:
        if not os.access(parent, os.W_OK):
            failures.append(f"Database parent directory is not writable: {parent}")

    print("HRDB environment check")
    print(f"- Python: {platform.python_version()}")
    print(f"- sqlite3 module: {sqlite_version}")
    print(f"- sqlite3 CLI: {'found' if sqlite_cli else 'missing'}")
    print(f"- Database path: {db_path}")

    if warnings:
        print("- Warnings:")
        for item in warnings:
            print(f"  - {item}")

    if failures:
        print("- Status: failed")
        print("- Install hints:")
        for hint in install_hints():
            print(f"  - {hint}")
        for item in failures:
            print(f"- Failure: {item}")
        return 1

    print("- Status: ok")
    if warnings:
        print("- Next step: fix warnings if you need CLI-based inspection, otherwise you can continue.")
    else:
        print("- Next step: run scripts/inspect_schema.py or scripts/init_db.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

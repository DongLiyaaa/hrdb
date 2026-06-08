#!/usr/bin/env python3

import argparse
import json
import sqlite3
from pathlib import Path


CANONICAL_PATTERNS = {
    "message_id": {"message_id", "msg_id", "id"},
    "message_created_at": {"message_created_at", "created_at", "sent_at", "event_time"},
    "sender_id": {"sender_id", "sender_open_id", "user_id", "employee_id"},
    "sender_name": {"sender_name", "user_name", "display_name", "name"},
    "chat_id": {"chat_id", "conversation_id", "room_id", "thread_id"},
    "chat_name": {"chat_name", "conversation_name", "room_name"},
    "content_text": {"content_text", "text", "body", "message_text"},
}


def fetch_tables(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return [row[0] for row in cur.fetchall()]


def fetch_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.execute(f"PRAGMA table_info({json.dumps(table)})")
    return [row[1] for row in cur.fetchall()]


def classify(tables: list[str], table_columns: dict[str, list[str]]) -> tuple[str, dict[str, str]]:
    if not tables:
        return "bootstrap-new-db", {}

    if {"feishu_messages", "period_insight_reports"}.issubset(set(tables)):
        return "hrdb-ready", {}

    mapping: dict[str, str] = {}
    for logical_name, candidates in CANONICAL_PATTERNS.items():
        for table, columns in table_columns.items():
            match = next((column for column in columns if column in candidates), None)
            if match:
                mapping[logical_name] = f"{table}.{match}"
                break

    if len(mapping) >= 4:
        return "adapt-existing-db", mapping
    return "unknown-custom-db", mapping


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a SQLite schema and recommend how HRDB should work with it.")
    parser.add_argument("--db", required=True, help="SQLite database path.")
    args = parser.parse_args()

    db_path = Path(args.db).expanduser()
    if not db_path.exists():
        print(f"Database does not exist: {db_path}")
        print("Recommended mode: bootstrap-new-db")
        return 0

    conn = sqlite3.connect(str(db_path))
    try:
        tables = fetch_tables(conn)
        table_columns = {table: fetch_columns(conn, table) for table in tables}
        mode, mapping = classify(tables, table_columns)
    finally:
        conn.close()

    print("HRDB schema inspection")
    print(f"- Database: {db_path}")
    print(f"- Recommended mode: {mode}")
    print(f"- Tables found: {len(tables)}")
    for table in tables:
        preview = ", ".join(table_columns[table][:8])
        print(f"  - {table}: {preview}")

    if mapping:
        print("- Canonical field candidates:")
        for logical_name, source in mapping.items():
            print(f"  - {logical_name}: {source}")

    if mode == "adapt-existing-db":
        print("- Guidance: adapt queries or create compatibility views instead of applying the bundled schema.")
    elif mode == "hrdb-ready":
        print("- Guidance: the database already matches the HRDB baseline schema.")
    elif mode == "bootstrap-new-db":
        print("- Guidance: initialize a fresh baseline schema with scripts/init_db.py.")
    else:
        print("- Guidance: inspect the source tables manually and define a narrow compatibility mapping before reporting.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

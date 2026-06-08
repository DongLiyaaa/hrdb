#!/usr/bin/env python3

import argparse
import json
import sqlite3
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = SKILL_DIR / "references" / "schema_base.sql"


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


def fetch_indexes(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='index' AND name LIKE 'idx_%'
        ORDER BY name
        """
    )
    return [row[0] for row in cur.fetchall()]


def validate_database(conn: sqlite3.Connection) -> dict:
    tables = fetch_tables(conn)
    indexes = fetch_indexes(conn)
    return {
        "tables": tables,
        "indexes": indexes,
        "table_count": len(tables),
        "index_count": len(indexes),
        "ok": {"feishu_messages", "period_insight_reports"}.issubset(set(tables)) and len(indexes) >= 10,
    }


def load_schema() -> str:
    return SCHEMA_PATH.read_text(encoding="utf-8")


def write_runtime_config(
    db_path: Path,
    timezone: str,
    analysis_push_cron: str,
    bound_user_open_id: str,
    bound_user_user_id: str,
    bound_user_name: str,
    analysis_push_target_type: str,
    analysis_push_target: str,
    taxonomy_profile: str,
    import_command: str,
) -> Path:
    config_path = db_path.with_name("hrdb_runtime_config.json")
    push_target_mode = "custom" if analysis_push_target else "initial_bound_user"
    push_target_id = analysis_push_target or bound_user_open_id

    payload = {
        "skill_name": "hrdb",
        "database_path": str(db_path.resolve()),
        "schema_mode": "bootstrap-new-db",
        "taxonomy_profile": taxonomy_profile,
        "initial_bound_user": {
            "open_id": bound_user_open_id,
            "user_id": bound_user_user_id,
            "name": bound_user_name,
        },
        "sqlite_import_schedule": {
            "enabled": True,
            "mode": "daemon",
            "frequency": "realtime",
            "interval_seconds": 5,
            "timezone": timezone,
            "command": import_command,
        },
        "analysis_push_schedule": {
            "enabled": True,
            "frequency": "weekly",
            "day_of_week": "saturday",
            "time": "10:30",
            "timezone": timezone,
            "cron": analysis_push_cron,
            "push_target_mode": push_target_mode,
            "push_target_type": analysis_push_target_type,
            "push_target_id": push_target_id,
        },
    }
    config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return config_path


def initialize_database(db_path: Path) -> dict:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        existing_tables = fetch_tables(conn)
        if existing_tables and not {"feishu_messages", "period_insight_reports"}.issubset(set(existing_tables)):
            raise SystemExit(
                "Existing non-HRDB tables detected. Run scripts/inspect_schema.py and adapt the schema instead of applying the bootstrap SQL."
            )

        conn.executescript(load_schema())
        conn.commit()
        result = validate_database(conn)
        result["database_path"] = str(db_path.resolve())
        return result
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a fresh HRDB-compatible SQLite database.")
    parser.add_argument("--db", default="./hrdb.db", help="SQLite database path.")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="Timezone for schedules.")
    parser.add_argument("--analysis-push-cron", default="30 10 * * 6", help="Cron for pushing analysis reports.")
    parser.add_argument("--bound-user-open-id", default="", help="Open ID of the initial bound Feishu user.")
    parser.add_argument("--bound-user-user-id", default="", help="User ID of the initial bound Feishu user.")
    parser.add_argument("--bound-user-name", default="", help="Name of the initial bound Feishu user.")
    parser.add_argument(
        "--import-command",
        default="",
        help="Command executed by the realtime ingest daemon every 5 seconds. Use {database_path} as a placeholder if needed.",
    )
    parser.add_argument(
        "--analysis-push-target-type",
        default="feishu_user",
        choices=["feishu_user", "feishu_chat", "webhook"],
        help="Report push target type.",
    )
    parser.add_argument("--analysis-push-target", default="", help="Custom push target. Defaults to the initial bound user.")
    parser.add_argument(
        "--taxonomy-profile",
        default="general",
        choices=["general", "ecommerce"],
        help="Default reporting taxonomy profile.",
    )
    args = parser.parse_args()

    db_path = Path(args.db).expanduser()
    result = initialize_database(db_path)
    runtime_config_path = write_runtime_config(
        db_path=db_path,
        timezone=args.timezone,
        analysis_push_cron=args.analysis_push_cron,
        bound_user_open_id=args.bound_user_open_id,
        bound_user_user_id=args.bound_user_user_id,
        bound_user_name=args.bound_user_name,
        analysis_push_target_type=args.analysis_push_target_type,
        analysis_push_target=args.analysis_push_target,
        taxonomy_profile=args.taxonomy_profile,
        import_command=args.import_command,
    )

    print("HRDB bootstrap completed")
    print(f"- Database path: {result['database_path']}")
    print(f"- Tables: {', '.join(result['tables'])}")
    print(f"- Index count: {result['index_count']}")
    print(f"- Runtime config: {runtime_config_path.resolve()}")
    if not result["ok"]:
        print("- Status: incomplete")
        return 1

    if not (args.bound_user_open_id or args.analysis_push_target):
        print("- Warning: no default push target configured yet.")
    print("- Status: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

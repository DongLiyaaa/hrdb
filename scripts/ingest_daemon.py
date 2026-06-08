#!/usr/bin/env python3

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


RUNNING = True


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def companion_paths(db_path: Path) -> dict[str, Path]:
    return {
        "config": db_path.with_name("hrdb_runtime_config.json"),
        "pid": db_path.with_name("hrdb_ingest_daemon.pid"),
        "log": db_path.with_name("hrdb_ingest_daemon.log"),
        "state": db_path.with_name("hrdb_ingest_daemon_state.json"),
    }


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def save_config(config_path: Path, payload: dict) -> None:
    config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_state(state_path: Path) -> dict:
    if not state_path.exists():
        return {
            "status": "stopped",
            "success_count": 0,
            "error_count": 0,
            "last_started_at": None,
            "last_finished_at": None,
            "last_exit_code": None,
            "last_duration_seconds": None,
            "last_error": None,
        }
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(state_path: Path, payload: dict) -> None:
    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def process_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def read_pid(pid_path: Path) -> int | None:
    if not pid_path.exists():
        return None
    try:
        return int(pid_path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def resolve_command(db_path: Path, config: dict, cli_command: str) -> str:
    command = cli_command or config.get("sqlite_import_schedule", {}).get("command", "")
    if not command:
        return ""
    return command.format(
        database_path=str(db_path.resolve()),
        config_path=str(companion_paths(db_path)["config"].resolve()),
    )


def resolve_interval(config: dict, cli_interval: int | None) -> int:
    if cli_interval is not None:
        return cli_interval
    interval = config.get("sqlite_import_schedule", {}).get("interval_seconds", 5)
    return max(1, int(interval))


def persist_runtime_settings(db_path: Path, interval_seconds: int, command: str) -> None:
    paths = companion_paths(db_path)
    config = load_config(paths["config"])
    if not config:
        config = {
            "skill_name": "hrdb",
            "database_path": str(db_path.resolve()),
            "sqlite_import_schedule": {},
            "analysis_push_schedule": {},
        }
    config.setdefault("sqlite_import_schedule", {})
    config["sqlite_import_schedule"].update(
        {
            "enabled": True,
            "mode": "daemon",
            "frequency": "realtime",
            "interval_seconds": interval_seconds,
            "command": command,
        }
    )
    save_config(paths["config"], config)


def append_log(log_path: Path, message: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{utc_now()}] {message}\n")


def handle_signal(signum, _frame) -> None:
    global RUNNING
    RUNNING = False


def run_loop(db_path: Path, import_command: str, interval_seconds: int) -> int:
    global RUNNING
    RUNNING = True
    paths = companion_paths(db_path)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    paths["pid"].write_text(str(os.getpid()), encoding="utf-8")
    state = load_state(paths["state"])
    state["status"] = "running"
    save_state(paths["state"], state)
    append_log(paths["log"], f"daemon started; interval={interval_seconds}s")

    try:
        while RUNNING:
            started_at = time.monotonic()
            state = load_state(paths["state"])
            state["status"] = "running"
            state["last_started_at"] = utc_now()
            save_state(paths["state"], state)

            completed = subprocess.run(
                import_command,
                shell=True,
                text=True,
                capture_output=True,
            )

            duration = round(time.monotonic() - started_at, 3)
            state = load_state(paths["state"])
            state["last_finished_at"] = utc_now()
            state["last_exit_code"] = completed.returncode
            state["last_duration_seconds"] = duration

            if completed.returncode == 0:
                state["success_count"] = int(state.get("success_count", 0)) + 1
                state["last_error"] = None
                append_log(paths["log"], f"ingest ok ({duration}s)")
            else:
                state["error_count"] = int(state.get("error_count", 0)) + 1
                stderr = (completed.stderr or completed.stdout or "").strip()
                state["last_error"] = stderr[:1000]
                append_log(paths["log"], f"ingest failed exit={completed.returncode} detail={stderr[:400]}")

            save_state(paths["state"], state)

            slept = 0.0
            while RUNNING and slept < interval_seconds:
                time.sleep(min(0.5, interval_seconds - slept))
                slept += 0.5
    finally:
        state = load_state(paths["state"])
        state["status"] = "stopped"
        save_state(paths["state"], state)
        if paths["pid"].exists():
            paths["pid"].unlink()
        append_log(paths["log"], "daemon stopped")

    return 0


def command_start(args) -> int:
    db_path = Path(args.db).expanduser()
    paths = companion_paths(db_path)
    existing_pid = read_pid(paths["pid"])
    if existing_pid and process_is_alive(existing_pid):
        print(f"HRDB ingest daemon already running: pid={existing_pid}")
        return 0

    config = load_config(paths["config"])
    interval_seconds = resolve_interval(config, args.interval_seconds)
    command = resolve_command(db_path, config, args.import_command)
    if not command:
        print("No import command configured. Pass --import-command or set sqlite_import_schedule.command in hrdb_runtime_config.json.")
        return 1

    persist_runtime_settings(db_path, interval_seconds, args.import_command or config.get("sqlite_import_schedule", {}).get("command", ""))

    log_path = paths["log"]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        process = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "run",
                "--db",
                str(db_path),
                "--interval-seconds",
                str(interval_seconds),
                "--import-command",
                args.import_command or config.get("sqlite_import_schedule", {}).get("command", ""),
            ],
            stdin=subprocess.DEVNULL,
            stdout=handle,
            stderr=handle,
            start_new_session=True,
        )

    print(f"HRDB ingest daemon started: pid={process.pid}")
    print(f"- Database: {db_path.resolve()}")
    print(f"- Interval: {interval_seconds}s")
    print(f"- Log: {log_path.resolve()}")
    return 0


def command_run(args) -> int:
    db_path = Path(args.db).expanduser()
    config = load_config(companion_paths(db_path)["config"])
    interval_seconds = resolve_interval(config, args.interval_seconds)
    command = resolve_command(db_path, config, args.import_command)
    if not command:
        print("No import command configured. Pass --import-command or set sqlite_import_schedule.command in hrdb_runtime_config.json.")
        return 1
    return run_loop(db_path, command, interval_seconds)


def command_status(args) -> int:
    db_path = Path(args.db).expanduser()
    paths = companion_paths(db_path)
    pid = read_pid(paths["pid"])
    state = load_state(paths["state"])
    alive = bool(pid and process_is_alive(pid))

    print("HRDB ingest daemon status")
    print(f"- Database: {db_path.resolve()}")
    print(f"- Running: {'yes' if alive else 'no'}")
    if pid:
        print(f"- PID: {pid}")
    print(f"- Success count: {state.get('success_count', 0)}")
    print(f"- Error count: {state.get('error_count', 0)}")
    print(f"- Last started at: {state.get('last_started_at')}")
    print(f"- Last finished at: {state.get('last_finished_at')}")
    print(f"- Last exit code: {state.get('last_exit_code')}")
    if state.get("last_error"):
        print(f"- Last error: {state['last_error']}")
    print(f"- Log: {paths['log'].resolve()}")
    return 0


def command_stop(args) -> int:
    db_path = Path(args.db).expanduser()
    paths = companion_paths(db_path)
    pid = read_pid(paths["pid"])
    if not pid or not process_is_alive(pid):
        print("HRDB ingest daemon is not running.")
        if paths["pid"].exists():
            paths["pid"].unlink()
        return 0

    os.kill(pid, signal.SIGTERM)
    deadline = time.time() + 10
    while time.time() < deadline:
        if not process_is_alive(pid):
            print(f"HRDB ingest daemon stopped: pid={pid}")
            return 0
        time.sleep(0.2)

    print(f"Failed to stop HRDB ingest daemon within timeout: pid={pid}")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run or manage the HRDB realtime ingest daemon.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_shared_arguments(target):
        target.add_argument("--db", default="./hrdb.db", help="SQLite database path.")
        target.add_argument("--import-command", default="", help="Command executed every cycle. Supports {database_path} and {config_path}.")
        target.add_argument("--interval-seconds", type=int, default=None, help="Realtime ingest interval in seconds. Default: 5.")

    start = subparsers.add_parser("start", help="Start the ingest daemon in the background.")
    add_shared_arguments(start)
    start.set_defaults(handler=command_start)

    run = subparsers.add_parser("run", help="Run the ingest daemon in the foreground.")
    add_shared_arguments(run)
    run.set_defaults(handler=command_run)

    status = subparsers.add_parser("status", help="Show daemon status.")
    status.add_argument("--db", default="./hrdb.db", help="SQLite database path.")
    status.set_defaults(handler=command_status)

    stop = subparsers.add_parser("stop", help="Stop the background daemon.")
    stop.add_argument("--db", default="./hrdb.db", help="SQLite database path.")
    stop.set_defaults(handler=command_stop)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

# Realtime Daemon

HRDB now defaults to realtime ingestion through a background daemon.

## Default behavior

- mode: `daemon`
- frequency: `realtime`
- interval: `5` seconds
- state files: next to the database

Generated companion files:

- `hrdb_runtime_config.json`
- `hrdb_ingest_daemon.pid`
- `hrdb_ingest_daemon.log`
- `hrdb_ingest_daemon_state.json`

## Required import command

The daemon does not fetch Feishu data by itself. It repeatedly executes the configured import command.

Supported placeholders:

- `{database_path}`
- `{config_path}`

Example:

```bash
python3 scripts/ingest_daemon.py start \
  --db ./hrdb.db \
  --import-command "python3 your_ingest_job.py --db {database_path}"
```

## Operations

- start:
  - launches a detached background process
- run:
  - runs the loop in the foreground
- status:
  - shows pid, success count, error count, and last run status
- stop:
  - sends `SIGTERM` and waits for clean shutdown

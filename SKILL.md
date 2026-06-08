---
name: hrdb
description: Use when analyzing Feishu or other work-chat data stored in SQLite to produce weekly or monthly AI-usage, collaboration, and management insight reports, especially when the workspace needs privacy-constrained reporting, schema inspection, or a bootstrap database that should adapt to existing tables instead of replacing them.
---

# HRDB

HRDB is a SQLite-first skill for enterprise chat analysis. It is designed for Feishu data, but the default workflow is adaptation-first: inspect the existing database, map it to HRDB's canonical fields, and only use the bundled bootstrap schema when the user is starting fresh. The default ingest mode is a background daemon that runs every 5 seconds.

## Prerequisite Check (Required)

Run this before any initialization or reporting step:

```bash
python3 scripts/check_env.py --db <db_path>
```

Replace `<db_path>` with the real database path in the current environment. Do not assume a fixed path unless the user explicitly provided one.

If the check fails, stop and report the missing dependency with the install command shown by the script.

## Working Modes

Choose one mode after inspecting the database:

1. `adapt-existing-db` (recommended)
   - Use when the user already has SQLite tables.
   - Run:
   ```bash
   python3 scripts/inspect_schema.py --db <existing_db_path>
   ```
   - Prefer query adaptation or compatibility views over destructive migration.

2. `bootstrap-new-db`
   - Use only when the database is empty, missing, or the user explicitly asks for a fresh HRDB-compatible schema.
   - Run:
   ```bash
   python3 scripts/init_db.py --db <db_path>
   ```

3. `generate-report`
   - Use after the data source is either HRDB-ready or mapped to the canonical fields.
   - Follow the report scope and privacy rules below.

## Core Rules

- Inspect the existing schema before applying bundled SQL.
- Do not overwrite or reshape a user's existing schema just to match HRDB.
- Use the bundled schema as a bootstrap contract, not as a mandatory migration target.
- Keep analysis work-related. Do not infer sensitive identity, private attributes, or non-work personality traits.
- If the data is sparse or ambiguous, say so explicitly.
- Prefer generalized labels unless the user clearly operates in a domain-specific workflow. See `references/taxonomy_profiles.md`.

## Canonical Field Checklist

When adapting an existing database, map these logical fields first:

- message identifier
- message timestamp
- sender identifier
- sender display name
- conversation or chat identifier
- conversation display name
- normalized text content
- AI-related flag or signal
- optional labels for topic, issue, maturity, value, risk, and tone

If a source database covers these fields, adaptation is usually better than re-initialization.

## Recommended Workflow

1. Run `scripts/check_env.py`.
2. Run `scripts/inspect_schema.py` on the target database.
3. Choose `adapt-existing-db` unless the database is empty or the user wants a fresh bootstrap.
4. If bootstrapping, use `scripts/init_db.py`, then store runtime settings in the generated config file.
5. Start realtime ingest with `scripts/ingest_daemon.py` after setting the import command.
6. For analysis, generate employee, chat, department, company, or topic scopes from the mapped canonical fields.
7. When producing weekly or monthly reports, compare only against periods that actually exist in the data.

## Realtime Ingest Daemon

The default sync mode is a background daemon:

- frequency: `realtime`
- interval: `5` seconds
- mode: `daemon`

Set `sqlite_import_schedule.command` in `hrdb_runtime_config.json`, or pass `--import-command` when starting the daemon.

Template:

```bash
python3 scripts/ingest_daemon.py start --db <db_path> --import-command "<real_import_command>"
python3 scripts/ingest_daemon.py status --db <db_path>
python3 scripts/ingest_daemon.py stop --db <db_path>
```

## Reporting Rules

- Employee-level output:
  - Focus on work patterns, recurring blockers, AI usage quality, handoff quality, and training opportunities.
- Chat-level output:
  - Focus on signal-to-noise, action-item closure, decision quality, repeated blockers, and coordination gaps.
- Organization-level output:
  - Focus on adoption, maturity, bottlenecks, reusable SOP opportunities, and risk concentration.
- Never use the report as a stand-alone basis for punishment, termination, or compensation decisions.

## References

- Base bootstrap schema: `references/schema_base.sql`
- Schema strategy and mode selection: `references/schema_profiles.md`
- Taxonomy profiles and label examples: `references/taxonomy_profiles.md`
- Example runtime config: `references/config.example.yaml`
- Realtime daemon behavior: `references/runtime_daemon.md`

## AI Execution Checklist

Treat this as plain-text guidance for AI execution. Replace all placeholders with real values from the current environment before running anything.

1. Determine the real skill root, working directory, database path, timezone, and import command.
2. Verify Python, SQLite, and write permission.
3. If a database already exists, inspect it before deciding on bootstrap.
4. Choose between `adapt-existing-db` and `bootstrap-new-db` based on the actual schema.
5. If bootstrapping, generate runtime config and confirm its contents.
6. Before starting the daemon, make sure `<real_import_command>` is valid and safe to run repeatedly.
7. Start the daemon only after replacing `<db_path>` and `<real_import_command>` with real values.
8. After startup, verify daemon status, runtime files, and logs.

## Command Templates

```bash
python3 scripts/check_env.py --db <db_path>
python3 scripts/inspect_schema.py --db <existing_db_path>
python3 scripts/init_db.py --db <db_path> --timezone <timezone>
python3 scripts/ingest_daemon.py start --db <db_path> --import-command "<real_import_command>"
```

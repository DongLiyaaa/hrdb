# HRDB

HRDB is a Codex skill for analyzing Feishu or other work-chat data stored in SQLite.

HRDB 是一个给 Codex 用的 skill，用来分析存进 SQLite 的飞书或工作聊天数据。

## What It Helps You Do | 它能帮你做什么

- Inspect your existing SQLite schema before changing anything.
  在改动任何数据结构之前，先检查你现有的 SQLite 数据库。
- Bootstrap a standard HRDB database if you do not have one yet.
  如果你还没有数据库，可以初始化一个标准 HRDB 数据库。
- Run realtime ingestion with a background daemon every 5 seconds.
  用后台守护进程每 5 秒执行一次实时入库。
- Generate employee, chat, department, and company-level insight reports.
  生成员工、群聊、部门、公司等维度的分析报告。
- Keep reporting work-related and privacy-constrained.
  保持分析范围聚焦工作内容，并遵守隐私约束。

## Simple Onboarding | 简单入门

This project is designed so AI or an operator can adapt it to the real environment first.

这个项目的设计目标是：先让 AI 或操作者根据真实环境做检查，再决定怎么执行。

Do not treat example database names or command placeholders as fixed values.

不要把示例数据库名或命令占位符当成固定值直接照抄。

## AI Checklist | 给 AI 的检查清单

Use this as plain-text guidance for AI execution.

把下面这段当成 AI 执行前的明文检查清单。

1. Identify the actual skill root, working directory, database path, and import command in the current environment.
   先识别当前环境里的 skill 根目录、工作目录、数据库路径、导入命令。
2. Check whether Python, SQLite, and filesystem write permission are available.
   检查 Python、SQLite、文件写权限是否可用。
3. If a SQLite database already exists, inspect its schema first.
   如果已经存在 SQLite 数据库，先检查它的表结构。
4. Decide between `adapt-existing-db` and `bootstrap-new-db` based on the real database state.
   根据真实数据库状态，在 `adapt-existing-db` 和 `bootstrap-new-db` 之间做选择。
5. If bootstrapping is needed, initialize the database and generate runtime config.
   如果需要初始化，就创建数据库并生成运行时配置。
6. Before starting realtime ingestion, confirm the actual import command that should run every 5 seconds.
   启动实时入库之前，确认每 5 秒执行一次的真实导入命令是什么。
7. Start the daemon only after the database path and import command have been replaced with real values.
   只有在数据库路径和导入命令都替换成真实值之后，才启动守护进程。
8. After startup, verify daemon status, runtime files, and recent logs.
   启动后检查守护状态、运行时文件和最新日志。

## Command Templates | 命令模板

Replace placeholders with real values before running.

运行前先把占位符替换成真实值。

```bash
python3 scripts/check_env.py --db <db_path>
python3 scripts/inspect_schema.py --db <existing_db_path>
python3 scripts/init_db.py --db <db_path> --timezone <timezone>
python3 scripts/ingest_daemon.py start --db <db_path> --import-command "<real_import_command>"
python3 scripts/ingest_daemon.py status --db <db_path>
```

## Recommended Reading Order | 建议阅读顺序

- `SKILL.md`
- `references/schema_profiles.md`
- `references/config.example.yaml`
- `references/runtime_daemon.md`

## Repository Layout | 仓库结构

- `SKILL.md`: main skill instructions
  `SKILL.md`：主技能说明
- `scripts/`: executable helper scripts
  `scripts/`：可执行脚本
- `references/`: schema, config, and daemon notes
  `references/`：schema、配置和守护说明
- `agents/openai.yaml`: agent-facing metadata
  `agents/openai.yaml`：给 agent 用的元数据

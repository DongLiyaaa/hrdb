# HRDB

HRDB helps you track people through data statistics from Feishu messages, group chats, and AI usage records.

HRDB 主要用于通过飞书消息、群聊记录和 AI 使用数据的统计分析，持续跟踪人员情况。

## About | 简介

HRDB is mainly designed to help you track people through data statistics.

HRDB 主要就是通过数据统计来帮助你持续跟踪人员情况。

It focuses on work activity, AI usage, issue patterns, collaboration signals, and trend changes.

重点关注工作活跃度、AI 使用情况、问题分布、协作表现和变化趋势。

## AI Checklist | 给 AI 的检查清单

Use this project as an environment-adaptive workflow, not a fixed command list.

把这个项目当成“根据现场环境自适应执行的流程”，不要当成固定命令清单。

1. Identify the real skill root, working directory, database path, timezone, and import command.
   先识别真实的 skill 根目录、工作目录、数据库路径、时区和导入命令。
2. Check Python, SQLite, and write permission.
   检查 Python、SQLite 和写权限是否可用。
3. If a database already exists, inspect the schema first.
   如果已经有数据库，先检查表结构。
4. Decide whether to adapt the existing database or bootstrap a new one.
   判断应该适配现有数据库，还是初始化新库。
5. Before starting realtime ingestion, confirm the real command that should run every 5 seconds.
   启动实时入库前，确认每 5 秒执行的真实导入命令。
6. Replace all placeholders with real values before running anything.
   执行前先把所有占位符替换成真实值。

## Command Templates | 命令模板

```bash
python3 scripts/check_env.py --db <db_path>
python3 scripts/inspect_schema.py --db <existing_db_path>
python3 scripts/init_db.py --db <db_path> --timezone <timezone>
python3 scripts/ingest_daemon.py start --db <db_path> --import-command "<real_import_command>"
python3 scripts/ingest_daemon.py status --db <db_path>
```

## Repository Layout | 仓库结构

- `SKILL.md`: main skill instructions
  `SKILL.md`：主技能说明
- `scripts/`: executable helper scripts
  `scripts/`：可执行脚本
- `references/`: schema, config, and daemon notes
  `references/`：schema、配置和守护说明
- `agents/openai.yaml`: agent-facing metadata
  `agents/openai.yaml`：给 agent 用的元数据

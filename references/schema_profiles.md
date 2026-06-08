# Schema Strategy

## Default rule

Use adaptation first. The bundled SQL is a bootstrap schema for new deployments, not a mandatory target for existing databases.

## Mode selection

- `adapt-existing-db`
  - Existing SQLite database already contains message-like tables.
  - Preferred action: inspect tables, map source columns to HRDB canonical fields, and write compatibility queries or views.

- `bootstrap-new-db`
  - Database is empty, missing, or explicitly intended to be initialized for HRDB.
  - Preferred action: run `scripts/init_db.py` to create the two-table baseline schema and runtime config.

- `hrdb-ready`
  - Database already contains `feishu_messages` and `period_insight_reports`.
  - Preferred action: reuse the schema as-is and continue with ingestion or reporting.

## Canonical mapping hints

Typical source column candidates:

- message id: `message_id`, `msg_id`, `id`
- timestamp: `message_created_at`, `created_at`, `sent_at`, `event_time`
- sender id: `sender_open_id`, `sender_id`, `user_id`, `employee_id`
- sender name: `sender_name`, `user_name`, `display_name`
- chat id: `chat_id`, `conversation_id`, `room_id`, `thread_id`
- chat name: `chat_name`, `conversation_name`, `room_name`
- text: `content_text`, `text`, `body`, `message_text`

## Non-destructive adaptation

Preferred options, in order:

1. Query adaptation inside the report logic.
2. Compatibility views that expose HRDB-like names.
3. One-time data copy into HRDB tables, only when the user explicitly wants a separate reporting database.

Avoid destructive in-place migrations unless the user requests them.

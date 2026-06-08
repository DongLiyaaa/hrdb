PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS feishu_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_key TEXT,
    source_platform TEXT NOT NULL DEFAULT 'feishu',

    message_id TEXT NOT NULL UNIQUE,
    chat_id TEXT,
    chat_name TEXT,
    chat_type TEXT,
    thread_id TEXT,
    parent_id TEXT,

    sender_id TEXT,
    sender_open_id TEXT,
    sender_user_id TEXT,
    sender_name TEXT NOT NULL,
    sender_type TEXT NOT NULL DEFAULT 'user',
    department_name TEXT,
    job_title TEXT,

    msg_type TEXT NOT NULL DEFAULT 'text',
    content_raw TEXT,
    content_text TEXT,
    content_cleaned TEXT,
    mentions_json TEXT,
    attachments_json TEXT,

    is_ai_related INTEGER NOT NULL DEFAULT 0,
    ai_agent_name TEXT,
    skill_name TEXT,

    domain_label TEXT,
    topic_label TEXT,
    issue_label TEXT,
    task_maturity_label TEXT,
    message_value_label TEXT,
    usage_intent_label TEXT,
    tone_label TEXT,
    risk_label TEXT,

    is_valid_work_message INTEGER NOT NULL DEFAULT 0,
    is_decision_signal INTEGER NOT NULL DEFAULT 0,
    is_action_item INTEGER NOT NULL DEFAULT 0,
    is_risk_signal INTEGER NOT NULL DEFAULT 0,

    analysis_confidence REAL,
    analysis_json TEXT,

    message_created_at DATETIME NOT NULL,
    message_updated_at DATETIME,
    analyzed_at DATETIME,
    ingested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS period_insight_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL,
    tenant_key TEXT,
    source_platform TEXT NOT NULL DEFAULT 'feishu',

    period_type TEXT NOT NULL,
    period_key TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    scope_type TEXT NOT NULL,
    scope_id TEXT,
    scope_name TEXT,
    department_name TEXT,

    total_messages INTEGER NOT NULL DEFAULT 0,
    valid_work_messages INTEGER NOT NULL DEFAULT 0,
    ai_related_messages INTEGER NOT NULL DEFAULT 0,
    ai_session_count INTEGER NOT NULL DEFAULT 0,
    valid_ai_task_count INTEGER NOT NULL DEFAULT 0,

    active_days INTEGER DEFAULT 0,
    active_actor_count INTEGER DEFAULT 0,

    valid_work_ratio REAL,
    ai_related_ratio REAL,
    noise_ratio REAL,

    decision_signal_count INTEGER NOT NULL DEFAULT 0,
    action_item_count INTEGER NOT NULL DEFAULT 0,
    risk_signal_count INTEGER NOT NULL DEFAULT 0,

    top_topics_json TEXT,
    top_issues_json TEXT,
    metrics_json TEXT,
    insights_json TEXT,
    comparison_json TEXT,
    capability_json TEXT,
    risk_json TEXT,
    suggestions_json TEXT,

    report_markdown TEXT,
    generated_by TEXT DEFAULT 'AI Agent',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_feishu_messages_created_at
ON feishu_messages(message_created_at);

CREATE INDEX IF NOT EXISTS idx_feishu_messages_sender
ON feishu_messages(sender_open_id);

CREATE INDEX IF NOT EXISTS idx_feishu_messages_sender_id
ON feishu_messages(sender_id);

CREATE INDEX IF NOT EXISTS idx_feishu_messages_chat
ON feishu_messages(chat_id);

CREATE INDEX IF NOT EXISTS idx_feishu_messages_topic
ON feishu_messages(topic_label);

CREATE INDEX IF NOT EXISTS idx_feishu_messages_issue
ON feishu_messages(issue_label);

CREATE INDEX IF NOT EXISTS idx_feishu_messages_ai
ON feishu_messages(is_ai_related);

CREATE INDEX IF NOT EXISTS idx_period_reports_period
ON period_insight_reports(period_type, period_key);

CREATE INDEX IF NOT EXISTS idx_period_reports_scope
ON period_insight_reports(scope_type, scope_id);

CREATE INDEX IF NOT EXISTS idx_period_reports_report_id
ON period_insight_reports(report_id);

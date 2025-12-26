CREATE TABLE telegram_users (
    telegram_user_id TEXT PRIMARY KEY,
    agent_service_user_id TEXT,
    user_first_name TEXT,
    onboarded_successfully BOOLEAN,
    created_at TEXT,
    updated_at TEXT
);

CREATE INDEX idx_agent_service_user_id ON telegram_users(agent_service_user_id);

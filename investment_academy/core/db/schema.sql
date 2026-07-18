CREATE TABLE IF NOT EXISTS chapter_progress (
    chapter_id TEXT PRIMARY KEY,
    completed INTEGER NOT NULL DEFAULT 0,
    quiz_score REAL NOT NULL DEFAULT 0.0,
    quiz_attempts INTEGER NOT NULL DEFAULT 0,
    last_accessed TEXT,
    time_spent_seconds INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lab_progress (
    lab_id TEXT PRIMARY KEY,
    completed INTEGER NOT NULL DEFAULT 0,
    exercises_done TEXT NOT NULL DEFAULT '[]',
    last_accessed TEXT
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_count INTEGER NOT NULL,
    score REAL NOT NULL,
    answers TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    current_phase TEXT NOT NULL DEFAULT 'p1',
    preferred_timeframe TEXT NOT NULL DEFAULT 'day',
    sandbox_balance REAL NOT NULL DEFAULT 100000.0,
    achievements TEXT NOT NULL DEFAULT '[]',
    risk_profile TEXT NOT NULL DEFAULT 'moderate'
);

CREATE TABLE IF NOT EXISTS psychology_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    scores TEXT NOT NULL,
    overall_risk_level TEXT NOT NULL,
    proceeded_to_trade INTEGER NOT NULL DEFAULT 0,
    self_notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS trading_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    setup_type TEXT NOT NULL DEFAULT '',
    entry_reason TEXT NOT NULL DEFAULT '',
    exit_reason TEXT NOT NULL DEFAULT '',
    pnl_pct REAL NOT NULL DEFAULT 0.0,
    emotional_state TEXT NOT NULL DEFAULT '',
    lesson_learned TEXT NOT NULL DEFAULT '',
    mistake_flag INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS spas_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etf_code TEXT NOT NULL,
    etf_name TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    probability REAL NOT NULL DEFAULT 0.5,
    direction TEXT NOT NULL DEFAULT 'neutral',
    position_pct REAL NOT NULL DEFAULT 0.0,
    stop_loss REAL NOT NULL DEFAULT 0.0,
    take_profit REAL NOT NULL DEFAULT 0.0,
    psychology_score INTEGER NOT NULL DEFAULT 0,
    psychology_level TEXT NOT NULL DEFAULT '',
    inputs_json TEXT NOT NULL DEFAULT '{}',
    result_json TEXT NOT NULL DEFAULT '{}'
);

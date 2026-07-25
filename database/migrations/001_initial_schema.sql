-- EduGenie initial schema (SQLite / PostgreSQL compatible subset).
-- Mirrors backend/app/database/models.py. Applied automatically at startup via
-- SQLAlchemy create_all; kept here as the reference DDL for managed databases.

CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    name        VARCHAR(120)  NOT NULL,
    email       VARCHAR(255)  NOT NULL UNIQUE,
    password    VARCHAR(255)  NOT NULL,
    created_at  TIMESTAMP     NOT NULL
);

CREATE TABLE IF NOT EXISTS user_queries (
    query_id    INTEGER PRIMARY KEY,
    user_id     INTEGER      NULL REFERENCES users (user_id) ON DELETE CASCADE,
    query_type  VARCHAR(32)  NOT NULL,
    query_text  TEXT         NOT NULL,
    created_at  TIMESTAMP    NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_responses (
    response_id   INTEGER PRIMARY KEY,
    query_id      INTEGER     NOT NULL UNIQUE REFERENCES user_queries (query_id) ON DELETE CASCADE,
    response_text TEXT        NOT NULL,
    model_used    VARCHAR(64) NOT NULL,
    created_at    TIMESTAMP   NOT NULL
);

CREATE TABLE IF NOT EXISTS quizzes (
    quiz_id        INTEGER PRIMARY KEY,
    query_id       INTEGER NOT NULL REFERENCES user_queries (query_id) ON DELETE CASCADE,
    question_text  TEXT    NOT NULL,
    option_a       TEXT    NOT NULL,
    option_b       TEXT    NOT NULL,
    option_c       TEXT    NOT NULL,
    option_d       TEXT    NOT NULL,
    correct_answer TEXT    NOT NULL,
    created_at     TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS summaries (
    summary_id    INTEGER PRIMARY KEY,
    query_id      INTEGER NOT NULL REFERENCES user_queries (query_id) ON DELETE CASCADE,
    original_text TEXT    NOT NULL,
    summary_text  TEXT    NOT NULL,
    created_at    TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS learning_paths (
    path_id               INTEGER PRIMARY KEY,
    query_id              INTEGER NOT NULL REFERENCES user_queries (query_id) ON DELETE CASCADE,
    topic                 VARCHAR(255) NOT NULL,
    difficulty_level      VARCHAR(32)  NOT NULL,
    recommended_resources TEXT         NOT NULL,
    created_at            TIMESTAMP    NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_user_queries_user_id    ON user_queries (user_id);
CREATE INDEX IF NOT EXISTS ix_user_queries_query_type ON user_queries (query_type);
CREATE INDEX IF NOT EXISTS ix_quizzes_query_id        ON quizzes (query_id);
CREATE INDEX IF NOT EXISTS ix_summaries_query_id      ON summaries (query_id);
CREATE INDEX IF NOT EXISTS ix_learning_paths_query_id ON learning_paths (query_id);

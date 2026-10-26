-- Database tables for the Chelsea 2025/26 project.
-- Star schema: 2 fact tables (matches, player stats per match) and dimension tables.
-- Safe to run more than once.

-- ---------- dimensions ----------

CREATE TABLE IF NOT EXISTS dim_season (
    season_id   SERIAL PRIMARY KEY,
    season_name VARCHAR(10) NOT NULL UNIQUE,
    start_date  DATE NOT NULL,
    end_date    DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id     INTEGER PRIMARY KEY,   -- YYYYMMDD, e.g. 20250817
    full_date   DATE NOT NULL UNIQUE,
    year        SMALLINT NOT NULL,
    month       SMALLINT NOT NULL,
    month_name  VARCHAR(10) NOT NULL,
    day         SMALLINT NOT NULL,
    day_name    VARCHAR(10) NOT NULL,
    day_of_week SMALLINT NOT NULL,     -- 1 = Monday ... 7 = Sunday
    is_weekend  BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_competition (
    competition_id   SERIAL PRIMARY KEY,
    competition_name VARCHAR(50) NOT NULL UNIQUE,
    competition_type VARCHAR(20) NOT NULL
);

-- every team Chelsea played against
CREATE TABLE IF NOT EXISTS dim_opponent (
    opponent_id   SERIAL PRIMARY KEY,
    opponent_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_player (
    player_id   SERIAL PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL UNIQUE,
    position    VARCHAR(20)            -- Goalkeeper / Defender / Midfielder / Forward
);

-- ---------- facts ----------

-- one row per Chelsea match. goals, xG and possession are from Chelsea's side.
CREATE TABLE IF NOT EXISTS fact_match (
    match_id       SERIAL PRIMARY KEY,
    season_id      INTEGER NOT NULL REFERENCES dim_season (season_id),
    competition_id INTEGER NOT NULL REFERENCES dim_competition (competition_id),
    date_id        INTEGER NOT NULL REFERENCES dim_date (date_id),
    opponent_id    INTEGER NOT NULL REFERENCES dim_opponent (opponent_id),
    is_home        BOOLEAN NOT NULL,
    goals_for      SMALLINT NOT NULL CHECK (goals_for >= 0),
    goals_against  SMALLINT NOT NULL CHECK (goals_against >= 0),
    xg_for         NUMERIC(6, 3),      -- only Premier League games have xG
    xg_against     NUMERIC(6, 3),
    possession     NUMERIC(4, 1) CHECK (possession BETWEEN 0 AND 100),
    attendance     INTEGER CHECK (attendance >= 0),
    referee        VARCHAR(100),
    -- the same game can't be loaded twice
    UNIQUE (competition_id, date_id, opponent_id)
);

-- one row per Chelsea player per match (Premier League only, from Understat)
CREATE TABLE IF NOT EXISTS fact_player_match (
    player_match_id SERIAL PRIMARY KEY,
    match_id     INTEGER NOT NULL REFERENCES fact_match (match_id) ON DELETE CASCADE,
    player_id    INTEGER NOT NULL REFERENCES dim_player (player_id),
    started      BOOLEAN NOT NULL,
    minutes      SMALLINT NOT NULL CHECK (minutes BETWEEN 0 AND 130),
    goals        SMALLINT NOT NULL DEFAULT 0 CHECK (goals >= 0),
    assists      SMALLINT NOT NULL DEFAULT 0 CHECK (assists >= 0),
    shots        SMALLINT NOT NULL DEFAULT 0 CHECK (shots >= 0),
    key_passes   SMALLINT NOT NULL DEFAULT 0 CHECK (key_passes >= 0),
    xg           NUMERIC(6, 3) NOT NULL DEFAULT 0,
    xa           NUMERIC(6, 3) NOT NULL DEFAULT 0,
    yellow_cards SMALLINT NOT NULL DEFAULT 0 CHECK (yellow_cards BETWEEN 0 AND 2),
    red_cards    SMALLINT NOT NULL DEFAULT 0 CHECK (red_cards BETWEEN 0 AND 1),
    own_goals    SMALLINT NOT NULL DEFAULT 0 CHECK (own_goals >= 0),
    UNIQUE (match_id, player_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_match_date ON fact_match (date_id);
CREATE INDEX IF NOT EXISTS idx_fact_match_opponent ON fact_match (opponent_id);
CREATE INDEX IF NOT EXISTS idx_fact_player_match_player ON fact_player_match (player_id);

-- ---------- starting data ----------

INSERT INTO dim_season (season_name, start_date, end_date)
VALUES ('2025/26', '2025-08-01', '2026-05-31')
ON CONFLICT (season_name) DO NOTHING;

INSERT INTO dim_competition (competition_name, competition_type)
VALUES ('Premier League', 'League'),
       ('UEFA Champions League', 'Europe'),
       ('FA Cup', 'Cup'),
       ('EFL Cup', 'Cup')
ON CONFLICT (competition_name) DO NOTHING;

-- every day of the season
INSERT INTO dim_date (date_id, full_date, year, month, month_name, day, day_name, day_of_week, is_weekend)
SELECT
    to_char(d, 'YYYYMMDD')::INTEGER,
    d,
    EXTRACT(YEAR FROM d),
    EXTRACT(MONTH FROM d),
    trim(to_char(d, 'Month')),
    EXTRACT(DAY FROM d),
    trim(to_char(d, 'Day')),
    EXTRACT(ISODOW FROM d),
    EXTRACT(ISODOW FROM d) IN (6, 7)
FROM generate_series('2025-08-01'::DATE, '2026-05-31'::DATE, INTERVAL '1 day') AS d
ON CONFLICT (date_id) DO NOTHING;

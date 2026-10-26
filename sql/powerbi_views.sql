-- Views that Power BI reads (powerbi/ChelseaAnalytics.pbip).
-- They rename columns to nicer names and work out result, points etc. once here,
-- so the DAX in Power BI stays simple. Safe to run more than once.

CREATE SCHEMA IF NOT EXISTS powerbi;

CREATE OR REPLACE VIEW powerbi.dim_date AS
SELECT
    date_id                          AS date_key,
    full_date                        AS date,
    year,
    month                            AS month_number,
    month_name,
    to_char(full_date, 'Mon')        AS month_short,
    to_char(full_date, 'Mon YYYY')   AS month_year,
    year * 100 + month               AS month_year_sort,
    ((month + 4) % 12) + 1           AS season_month_number,  -- Aug = 1, Sep = 2 ... May = 10
    day_name,
    day_of_week,
    is_weekend
FROM dim_date;

CREATE OR REPLACE VIEW powerbi.dim_competition AS
SELECT
    competition_id   AS competition_key,
    competition_name AS competition,
    competition_type,
    CASE competition_name
        WHEN 'Premier League'        THEN 'PL'
        WHEN 'UEFA Champions League' THEN 'UCL'
        ELSE competition_name
    END AS competition_short,
    CASE competition_name
        WHEN 'Premier League'        THEN 1
        WHEN 'UEFA Champions League' THEN 2
        WHEN 'FA Cup'                THEN 3
        WHEN 'EFL Cup'               THEN 4
        ELSE 9
    END AS competition_sort
FROM dim_competition;

CREATE OR REPLACE VIEW powerbi.dim_opponent AS
SELECT opponent_id AS opponent_key, opponent_name AS opponent
FROM dim_opponent;

-- Home / Away, used by both fact tables so one slicer filters both
CREATE OR REPLACE VIEW powerbi.dim_venue AS
SELECT 'Home'::TEXT AS venue, 1 AS venue_sort
UNION ALL
SELECT 'Away'::TEXT, 2;

CREATE OR REPLACE VIEW powerbi.dim_player AS
SELECT
    player_id   AS player_key,
    player_name AS player,
    COALESCE(position, 'Unknown') AS position_group,
    CASE position
        WHEN 'Goalkeeper' THEN 1
        WHEN 'Defender'   THEN 2
        WHEN 'Midfielder' THEN 3
        WHEN 'Forward'    THEN 4
        ELSE 5
    END AS position_sort
FROM dim_player;

CREATE OR REPLACE VIEW powerbi.fact_match AS
SELECT
    m.match_id       AS match_key,
    m.date_id        AS date_key,
    m.competition_id AS competition_key,
    m.opponent_id    AS opponent_key,
    CASE WHEN m.is_home THEN 'Home' ELSE 'Away' END AS venue,
    d.full_date      AS match_date,
    to_char(d.full_date, 'DD Mon')
        || CASE WHEN m.is_home THEN ' v ' ELSE ' @ ' END
        || o.opponent_name                  AS match_label,
    m.goals_for || '-' || m.goals_against   AS score,
    CASE
        WHEN m.goals_for > m.goals_against THEN 'W'
        WHEN m.goals_for = m.goals_against THEN 'D'
        ELSE 'L'
    END AS result,
    CASE
        WHEN m.goals_for > m.goals_against THEN 1
        WHEN m.goals_for = m.goals_against THEN 2
        ELSE 3
    END AS result_sort,
    CASE
        WHEN m.goals_for > m.goals_against THEN 3
        WHEN m.goals_for = m.goals_against THEN 1
        ELSE 0
    END AS points,
    m.goals_for,
    m.goals_against,
    m.goals_for - m.goals_against AS goal_difference,
    m.xg_for,
    m.xg_against,
    m.possession     AS possession_pct,
    m.attendance,
    m.referee
FROM fact_match m
JOIN dim_date d     ON d.date_id = m.date_id
JOIN dim_opponent o ON o.opponent_id = m.opponent_id;

CREATE OR REPLACE VIEW powerbi.fact_player_match AS
SELECT
    pm.player_match_id AS player_match_key,
    pm.match_id        AS match_key,
    pm.player_id       AS player_key,
    m.date_id          AS date_key,
    m.competition_id   AS competition_key,
    m.opponent_id      AS opponent_key,
    CASE WHEN m.is_home THEN 'Home' ELSE 'Away' END AS venue,
    pm.minutes,
    1                                      AS appearances,
    CASE WHEN pm.started THEN 1 ELSE 0 END AS starts,
    CASE WHEN pm.started THEN 0 ELSE 1 END AS sub_appearances,
    pm.goals,
    pm.assists,
    pm.xg,
    pm.xa,
    pm.shots,
    pm.key_passes,
    pm.yellow_cards,
    pm.red_cards,
    pm.own_goals
FROM fact_player_match pm
JOIN fact_match m ON m.match_id = pm.match_id;

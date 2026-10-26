-- Checks to run after loading the data:
--   psql -U postgres -d chelsea -f sql/data_quality_checks.sql
-- Checks 1-7 should all return 0 rows. Check 8 is just counts to eyeball.

\echo '1. Same game loaded twice (same date and opponent)'
SELECT date_id, opponent_id, COUNT(*)
FROM fact_match
GROUP BY date_id, opponent_id
HAVING COUNT(*) > 1;

\echo '2. Same player twice in one game'
SELECT match_id, player_id, COUNT(*)
FROM fact_player_match
GROUP BY match_id, player_id
HAVING COUNT(*) > 1;

\echo '3. Games outside the 2025/26 season'
SELECT m.match_id, d.full_date
FROM fact_match m
JOIN dim_date d ON d.date_id = m.date_id
JOIN dim_season s ON s.season_id = m.season_id
WHERE d.full_date NOT BETWEEN s.start_date AND s.end_date;

\echo '4. Premier League games with no xG, or xG on a non-league game'
SELECT m.match_id, c.competition_name, m.xg_for
FROM fact_match m
JOIN dim_competition c ON c.competition_id = m.competition_id
WHERE (c.competition_name = 'Premier League') <> (m.xg_for IS NOT NULL);

\echo '5. Premier League games with no player stats'
SELECT m.match_id
FROM fact_match m
JOIN dim_competition c ON c.competition_id = m.competition_id
WHERE c.competition_name = 'Premier League'
  AND NOT EXISTS (SELECT 1 FROM fact_player_match pm WHERE pm.match_id = m.match_id);

\echo '6. Players scored more goals than the team did'
SELECT m.match_id, m.goals_for, SUM(pm.goals) AS player_goals
FROM fact_match m
JOIN fact_player_match pm ON pm.match_id = m.match_id
GROUP BY m.match_id, m.goals_for
HAVING SUM(pm.goals) > m.goals_for;

\echo '7. Each game should have 11 starters'
SELECT match_id, SUM(CASE WHEN started THEN 1 ELSE 0 END) AS starters
FROM fact_player_match
GROUP BY match_id
HAVING SUM(CASE WHEN started THEN 1 ELSE 0 END) <> 11;

\echo '8. Games per competition (should be PL 38, UCL 10, FA Cup 6, EFL Cup 5)'
SELECT c.competition_name, COUNT(*) AS games
FROM fact_match m
JOIN dim_competition c ON c.competition_id = m.competition_id
GROUP BY c.competition_name
ORDER BY games DESC;

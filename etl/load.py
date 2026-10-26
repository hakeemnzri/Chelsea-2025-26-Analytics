"""Save matches and player stats into the database.

Everything uses INSERT ... ON CONFLICT, so running the ETL again updates the
rows that are already there instead of adding duplicates.
"""
import logging

log = logging.getLogger(__name__)


def get_season(cur, season_name):
    cur.execute(
        "SELECT season_id, start_date, end_date FROM dim_season WHERE season_name = %s",
        (season_name,),
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError(f"Season {season_name} is not in dim_season, run setup_database.py first")
    return row


def get_competition_id(cur, name):
    cur.execute("SELECT competition_id FROM dim_competition WHERE competition_name = %s", (name,))
    row = cur.fetchone()
    if row is None:
        raise ValueError(f"Unknown competition: {name}")
    return row[0]


def get_opponent_id(cur, name):
    cur.execute(
        "INSERT INTO dim_opponent (opponent_name) VALUES (%s) ON CONFLICT (opponent_name) DO NOTHING",
        (name,),
    )
    cur.execute("SELECT opponent_id FROM dim_opponent WHERE opponent_name = %s", (name,))
    return cur.fetchone()[0]


def save_player(cur, name, position=None):
    cur.execute(
        """
        INSERT INTO dim_player (player_name, position) VALUES (%s, %s)
        ON CONFLICT (player_name) DO UPDATE
            SET position = COALESCE(EXCLUDED.position, dim_player.position)
        RETURNING player_id
        """,
        (name, position),
    )
    return cur.fetchone()[0]


def save_match(cur, season_id, match):
    """Insert or update one match and return its match_id.

    Understat and FBref both have the same Premier League games. Each one only
    fills in what it knows (Understat has xG, FBref has possession and attendance),
    so COALESCE keeps the other source's value instead of overwriting it with NULL.
    """
    date_id = int(match["date"].replace("-", ""))
    cur.execute(
        """
        INSERT INTO fact_match (season_id, competition_id, date_id, opponent_id, is_home,
                                goals_for, goals_against, xg_for, xg_against,
                                possession, attendance, referee)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (competition_id, date_id, opponent_id) DO UPDATE SET
            is_home       = EXCLUDED.is_home,
            goals_for     = EXCLUDED.goals_for,
            goals_against = EXCLUDED.goals_against,
            xg_for        = COALESCE(EXCLUDED.xg_for, fact_match.xg_for),
            xg_against    = COALESCE(EXCLUDED.xg_against, fact_match.xg_against),
            possession    = COALESCE(EXCLUDED.possession, fact_match.possession),
            attendance    = COALESCE(EXCLUDED.attendance, fact_match.attendance),
            referee       = COALESCE(EXCLUDED.referee, fact_match.referee)
        RETURNING match_id
        """,
        (
            season_id,
            get_competition_id(cur, match["competition"]),
            date_id,
            get_opponent_id(cur, match["opponent"]),
            match["is_home"],
            match["goals_for"],
            match["goals_against"],
            match.get("xg_for"),
            match.get("xg_against"),
            match.get("possession"),
            match.get("attendance"),
            match.get("referee"),
        ),
    )
    return cur.fetchone()[0]


def save_player_match(cur, match_id, player_id, stats):
    cur.execute(
        """
        INSERT INTO fact_player_match (match_id, player_id, started, minutes, goals, assists,
                                       shots, key_passes, xg, xa, yellow_cards, red_cards, own_goals)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (match_id, player_id) DO UPDATE SET
            started      = EXCLUDED.started,
            minutes      = EXCLUDED.minutes,
            goals        = EXCLUDED.goals,
            assists      = EXCLUDED.assists,
            shots        = EXCLUDED.shots,
            key_passes   = EXCLUDED.key_passes,
            xg           = EXCLUDED.xg,
            xa           = EXCLUDED.xa,
            yellow_cards = EXCLUDED.yellow_cards,
            red_cards    = EXCLUDED.red_cards,
            own_goals    = EXCLUDED.own_goals
        """,
        (
            match_id, player_id, stats["started"], stats["minutes"], stats["goals"],
            stats["assists"], stats["shots"], stats["key_passes"], stats["xg"], stats["xa"],
            stats["yellow_cards"], stats["red_cards"], stats["own_goals"],
        ),
    )


def save_season(conn, season_name, matches, players=()):
    """Save a list of matches (and the squad, if given). Returns how many rows were saved."""
    counts = {"matches": 0, "player_rows": 0, "skipped": 0}
    with conn.cursor() as cur:
        season_id, start, end = get_season(cur, season_name)

        for player in players:
            save_player(cur, player["name"], player["position"])

        for match in matches:
            if not (str(start) <= match["date"] <= str(end)):
                log.warning("Skipping %s v %s, it's outside the %s season", match["date"], match["opponent"], season_name)
                counts["skipped"] += 1
                continue

            match_id = save_match(cur, season_id, match)
            counts["matches"] += 1

            for stats in match.get("players", []):
                player_id = save_player(cur, stats["name"])
                save_player_match(cur, match_id, player_id, stats)
                counts["player_rows"] += 1

    return counts

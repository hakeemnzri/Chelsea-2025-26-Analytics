"""Loads a few games into a separate test database (chelsea_test), never the real one.
Needs PostgreSQL running with the login from .env, otherwise these tests are skipped.
"""
from pathlib import Path

import psycopg2
import pytest

from etl import load
from etl.database import connect

TEST_DB = "chelsea_test"
SCHEMA = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"

UNDERSTAT_GAME = {
    "date": "2025-08-22", "competition": "Premier League", "opponent": "West Ham",
    "is_home": False, "goals_for": 5, "goals_against": 1, "xg_for": 2.9, "xg_against": 0.8,
    "players": [{
        "name": "Cole Palmer", "started": True, "minutes": 90, "goals": 2, "assists": 0,
        "shots": 4, "key_passes": 2, "xg": 1.1, "xa": 0.2, "yellow_cards": 0,
        "red_cards": 0, "own_goals": 0,
    }],
}
# the same game from FBref: no xG, but it has possession, attendance and referee
FBREF_GAME = {
    "date": "2025-08-22", "competition": "Premier League", "opponent": "West Ham",
    "is_home": False, "goals_for": 5, "goals_against": 1,
    "possession": 60.0, "attendance": 62462, "referee": "Michael Oliver",
}
OLD_GAME = dict(FBREF_GAME, date="2024-08-22")


@pytest.fixture
def conn():
    try:
        admin = connect("postgres")
    except psycopg2.OperationalError:
        pytest.skip("PostgreSQL is not running")
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB,))
        if cur.fetchone() is None:
            cur.execute(f"CREATE DATABASE {TEST_DB}")
    admin.close()

    conn = connect(TEST_DB)
    with conn.cursor() as cur:
        cur.execute(SCHEMA.read_text(encoding="utf-8"))
        cur.execute("TRUNCATE fact_player_match, fact_match, dim_player, dim_opponent RESTART IDENTITY CASCADE")
    conn.commit()
    yield conn
    conn.close()


def count(conn, table):
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return cur.fetchone()[0]


def test_running_twice_does_not_duplicate(conn):
    for _ in range(2):
        load.save_season(conn, "2025/26", [UNDERSTAT_GAME], [{"name": "Cole Palmer", "position": "Midfielder"}])
        conn.commit()
    assert count(conn, "fact_match") == 1
    assert count(conn, "fact_player_match") == 1
    assert count(conn, "dim_player") == 1
    assert count(conn, "dim_opponent") == 1


def test_second_source_fills_in_without_erasing(conn):
    load.save_season(conn, "2025/26", [UNDERSTAT_GAME])
    load.save_season(conn, "2025/26", [FBREF_GAME])
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT xg_for, possession, attendance, referee FROM fact_match")
        xg_for, possession, attendance, referee = cur.fetchone()
    assert count(conn, "fact_match") == 1
    assert float(xg_for) == 2.9          # from Understat, still there
    assert float(possession) == 60.0     # added by FBref
    assert attendance == 62462
    assert referee == "Michael Oliver"


def test_game_outside_the_season_is_skipped(conn):
    counts = load.save_season(conn, "2025/26", [OLD_GAME])
    conn.commit()
    assert counts["skipped"] == 1
    assert count(conn, "fact_match") == 0


def test_unknown_position_is_not_overwritten(conn):
    load.save_season(conn, "2025/26", [], [{"name": "Cole Palmer", "position": "Midfielder"}])
    load.save_season(conn, "2025/26", [UNDERSTAT_GAME])  # match rows don't know the position
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT position FROM dim_player")
        assert cur.fetchone()[0] == "Midfielder"

"""Get Chelsea's 2025/26 data from Understat and FBref and load it into PostgreSQL.

Run from the project folder:  python scripts/run_etl.py
Add --refresh to download the Understat data again instead of using the saved copy.
"""
import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from etl import fbref, load, understat  # noqa: E402
from etl.database import connect  # noqa: E402

SEASON = "2025/26"
UNDERSTAT_YEAR = "2025"  # Understat names a season by the year it starts
FBREF_CSV = ROOT / "data" / "manual_exports" / "fbref_scores_fixtures_2025_2026.csv"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="download Understat data again")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # 1. Understat: Premier League games with xG and player stats
    team_data, match_data = understat.download_season(UNDERSTAT_YEAR, refresh=args.refresh)
    players, understat_matches = understat.parse_season(team_data, match_data)

    # 2. FBref: every competition, plus possession, attendance and referee
    if FBREF_CSV.exists():
        fbref_matches = fbref.read_fixtures(FBREF_CSV)
    else:
        print(f"No FBref file at {FBREF_CSV}, only loading Understat (see README)")
        fbref_matches = []

    # 3. load both in one transaction, if anything fails nothing is saved
    conn = connect()
    with conn:
        understat_counts = load.save_season(conn, SEASON, understat_matches, players)
        fbref_counts = load.save_season(conn, SEASON, fbref_matches)
    conn.close()

    print(f"Understat: {understat_counts}")
    print(f"FBref:     {fbref_counts}")


if __name__ == "__main__":
    main()

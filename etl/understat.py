"""Download Chelsea's season from Understat and turn it into match and player rows.

Understat's pages load their data from JSON endpoints, so I call those directly:
  https://understat.com/getTeamData/Chelsea/2025   -> fixtures + squad
  https://understat.com/getMatchData/<match id>    -> player stats for one match
Every response is saved in data/raw/understat/ so re-running doesn't download again.
"""
import json
import logging
import time
from pathlib import Path

import requests

from etl.teams import clean_team_name

log = logging.getLogger(__name__)

BASE_URL = "https://understat.com"
HEADERS = {
    # the site's own JavaScript sends this header, without it the request is treated as a page load
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (student football data project)",
}
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "understat"
SECONDS_BETWEEN_REQUESTS = 2

POSITIONS = {"GK": "Goalkeeper", "D": "Defender", "M": "Midfielder", "F": "Forward"}


def get_json(path, refresh=False):
    """Get one Understat endpoint, using the saved copy if there is one."""
    cache_file = CACHE_DIR / (path.replace("/", "_") + ".json")
    if cache_file.exists() and not refresh:
        return json.loads(cache_file.read_text(encoding="utf-8"))

    log.info("Downloading %s", path)
    response = requests.get(f"{BASE_URL}/{path}", headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()
    time.sleep(SECONDS_BETWEEN_REQUESTS)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(data), encoding="utf-8")
    return data


def download_season(season_year, refresh=False):
    """Download the team data and every played match. season_year is "2025" for 2025/26."""
    team_data = get_json(f"getTeamData/Chelsea/{season_year}", refresh)
    match_data = {}
    for fixture in team_data["dates"]:
        if fixture["isResult"]:
            match_data[fixture["id"]] = get_json(f"getMatchData/{fixture['id']}", refresh)
    return team_data, match_data


def to_int(value):
    return int(float(value)) if value not in (None, "") else 0


def to_float(value):
    return float(value) if value not in (None, "") else 0.0


def player_position(codes):
    """Understat gives codes like "F M S" (positions played this season), take the first one."""
    for code in (codes or "").split():
        if code in POSITIONS:
            return POSITIONS[code]
    return None


def parse_season(team_data, match_data):
    """Turn the downloaded JSON into a list of players and a list of matches."""
    players = [
        {"name": p["player_name"].strip(), "position": player_position(p["position"])}
        for p in team_data["players"]
    ]

    matches = []
    for fixture in team_data["dates"]:
        if not fixture["isResult"]:
            continue

        home = fixture["h"]["title"]
        away = fixture["a"]["title"]
        if "Chelsea" not in (home, away):
            log.warning("Skipping a game Chelsea didn't play: %s v %s", home, away)
            continue

        side = "h" if home == "Chelsea" else "a"
        other = "a" if side == "h" else "h"

        lineup = []
        rosters = match_data.get(fixture["id"], {}).get("rosters", {})
        for row in rosters.get(side, {}).values():
            lineup.append({
                "name": row["player"].strip(),
                "started": row["position"] != "Sub",
                "minutes": to_int(row["time"]),
                "goals": to_int(row["goals"]),
                "assists": to_int(row["assists"]),
                "shots": to_int(row["shots"]),
                "key_passes": to_int(row["key_passes"]),
                "xg": to_float(row["xG"]),
                "xa": to_float(row["xA"]),
                "yellow_cards": to_int(row["yellow_card"]),
                "red_cards": to_int(row["red_card"]),
                "own_goals": to_int(row.get("own_goals")),
            })

        matches.append({
            "date": fixture["datetime"][:10],
            "competition": "Premier League",
            "opponent": clean_team_name(fixture[other]["title"]),
            "is_home": side == "h",
            "goals_for": to_int(fixture["goals"][side]),
            "goals_against": to_int(fixture["goals"][other]),
            "xg_for": to_float(fixture["xG"][side]),
            "xg_against": to_float(fixture["xG"][other]),
            "players": lineup,
        })

    return players, matches

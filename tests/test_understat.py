from etl.understat import parse_season, player_position


def player_row(name, position, minutes, goals="0"):
    return {
        "player": name, "position": position, "time": str(minutes), "goals": goals,
        "assists": "0", "shots": "1", "key_passes": "0", "xG": "0.25", "xA": "0.1",
        "yellow_card": "0", "red_card": "0", "own_goals": "0",
    }


# a small made-up version of what Understat sends back
TEAM_DATA = {
    "players": [
        {"player_name": "Cole Palmer", "position": "M F S"},
        {"player_name": "Robert Sánchez", "position": "GK"},
        {"player_name": "Bench Player", "position": "S"},
    ],
    "dates": [
        {   # Chelsea away, played
            "id": "1", "isResult": True, "datetime": "2025-08-22 19:00:00",
            "h": {"title": "West Ham"}, "a": {"title": "Chelsea"},
            "goals": {"h": "1", "a": "5"}, "xG": {"h": "0.8", "a": "2.9"},
        },
        {   # not played yet
            "id": "2", "isResult": False, "datetime": "2026-05-24 15:00:00",
            "h": {"title": "Chelsea"}, "a": {"title": "Everton"},
            "goals": {"h": None, "a": None}, "xG": {"h": None, "a": None},
        },
        {   # a game without Chelsea should never get in
            "id": "3", "isResult": True, "datetime": "2025-08-23 14:00:00",
            "h": {"title": "Arsenal"}, "a": {"title": "Liverpool"},
            "goals": {"h": "1", "a": "1"}, "xG": {"h": "1.0", "a": "1.0"},
        },
    ],
}

MATCH_DATA = {
    "1": {"rosters": {
        "h": {"10": player_row("West Ham Player", "FW", 90)},
        "a": {
            "20": player_row("Cole Palmer", "AMC", 90, goals="2"),
            "21": player_row("Robert Sánchez", "GK", 90),
            "22": player_row("Bench Player", "Sub", 15),
        },
    }},
}


def test_only_played_chelsea_games_are_kept():
    players, matches = parse_season(TEAM_DATA, MATCH_DATA)
    assert len(matches) == 1
    assert len(players) == 3


def test_match_is_from_chelsea_side():
    _, matches = parse_season(TEAM_DATA, MATCH_DATA)
    match = matches[0]
    assert match["date"] == "2025-08-22"
    assert match["opponent"] == "West Ham"
    assert match["is_home"] is False
    assert match["goals_for"] == 5
    assert match["goals_against"] == 1
    assert match["xg_for"] == 2.9


def test_only_chelsea_players_get_stats():
    _, matches = parse_season(TEAM_DATA, MATCH_DATA)
    names = [p["name"] for p in matches[0]["players"]]
    assert names == ["Cole Palmer", "Robert Sánchez", "Bench Player"]


def test_subs_are_not_starters():
    _, matches = parse_season(TEAM_DATA, MATCH_DATA)
    started = {p["name"]: p["started"] for p in matches[0]["players"]}
    assert started == {"Cole Palmer": True, "Robert Sánchez": True, "Bench Player": False}


def test_numbers_are_converted_from_text():
    _, matches = parse_season(TEAM_DATA, MATCH_DATA)
    palmer = matches[0]["players"][0]
    assert palmer["goals"] == 2
    assert palmer["minutes"] == 90
    assert palmer["xg"] == 0.25


def test_player_position():
    assert player_position("M F S") == "Midfielder"
    assert player_position("GK") == "Goalkeeper"
    assert player_position("S") is None

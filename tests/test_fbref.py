from etl.fbref import read_fixtures

CSV = """Date,Time,Comp,Round,Day,Venue,Result,GF,GA,Opponent,Poss,Attendance,Captain,Formation,Opp Formation,Referee,Match Report,Notes
2025-08-17,14:00,Premier League,Matchweek 1,Sun,Home,D,0,0,Crystal Palace,71,39678,Reece James,4-2-3-1,3-4-3,Darren England,Match Report,
2025-08-22,20:00,Premier League,Matchweek 2,Fri,Away,W,5,1,West Ham,60,62462,Enzo Fernandez,4-2-3-1,3-4-1-2,Michael Oliver,Match Report,
2025-09-17,20:00,Champions Lg,League phase,Wed,Away,L,1,3,de Bayern Munich,45,75000,Reece James,4-2-3-1,4-2-3-1,Some Referee,Match Report,
2026-05-16,15:00,FA Cup,Final,Sat,Neutral,L,0,1,Manchester City,48,84000,Reece James,4-2-3-1,4-3-3,Final Referee,Match Report,
2026-05-20,20:00,Friendly,Friendly,Wed,Home,W,3,0,Some Team,60,,,,,,Match Report,
2026-05-24,16:00,Premier League,Matchweek 38,Sun,Home,,,,Everton,,,,,,,Head-to-Head,
"""


def read(tmp_path):
    path = tmp_path / "fixtures.csv"
    path.write_text(CSV, encoding="utf-8")
    return read_fixtures(path)


def test_reads_played_games_only(tmp_path):
    matches = read(tmp_path)
    # the friendly (unknown competition) and the unplayed game are skipped
    assert len(matches) == 4


def test_home_game(tmp_path):
    palace = read(tmp_path)[0]
    assert palace["opponent"] == "Crystal Palace"
    assert palace["is_home"] is True
    assert palace["goals_for"] == 0
    assert palace["possession"] == 71.0
    assert palace["attendance"] == 39678
    assert palace["referee"] == "Darren England"


def test_away_game_scores_are_from_chelsea_side(tmp_path):
    west_ham = read(tmp_path)[1]
    assert west_ham["is_home"] is False
    assert west_ham["goals_for"] == 5
    assert west_ham["goals_against"] == 1


def test_champions_league_name_and_country_code(tmp_path):
    bayern = read(tmp_path)[2]
    assert bayern["competition"] == "UEFA Champions League"
    assert bayern["opponent"] == "Bayern Munich"


def test_neutral_venue_counts_as_home(tmp_path):
    final = read(tmp_path)[3]
    assert final["competition"] == "FA Cup"
    assert final["is_home"] is True

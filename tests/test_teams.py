from etl.teams import clean_team_name


def test_different_spellings_give_the_same_name():
    assert clean_team_name("Manchester Utd") == "Manchester United"
    assert clean_team_name("Manchester United") == "Manchester United"
    assert clean_team_name("Nottingham") == "Nottingham Forest"
    assert clean_team_name("Wolverhampton Wanderers") == "Wolves"
    assert clean_team_name("Brighton & Hove Albion") == "Brighton"


def test_country_code_is_removed():
    assert clean_team_name("de Bayern Munich") == "Bayern Munich"
    assert clean_team_name("fr PSG") == "Paris Saint-Germain"
    assert clean_team_name("az Qarabağ") == "Qarabağ"


def test_unknown_team_is_kept_as_it_is():
    assert clean_team_name("Port Vale") == "Port Vale"
    assert clean_team_name("  Lincoln   City ") == "Lincoln City"

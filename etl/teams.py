import re

# Understat and FBref don't always spell team names the same way
# (e.g. "Manchester Utd" vs "Manchester United"). If the names don't match,
# the same game gets loaded twice, so every name goes through clean_team_name().
TEAM_NAMES = {
    "chelsea": "Chelsea",
    "arsenal": "Arsenal",
    "aston villa": "Aston Villa",
    "bournemouth": "Bournemouth",
    "afc bournemouth": "Bournemouth",
    "brentford": "Brentford",
    "brighton": "Brighton",
    "brighton & hove albion": "Brighton",
    "burnley": "Burnley",
    "crystal palace": "Crystal Palace",
    "everton": "Everton",
    "fulham": "Fulham",
    "leeds": "Leeds United",
    "leeds united": "Leeds United",
    "liverpool": "Liverpool",
    "manchester city": "Manchester City",
    "manchester united": "Manchester United",
    "manchester utd": "Manchester United",
    "newcastle": "Newcastle United",
    "newcastle united": "Newcastle United",
    "nottingham": "Nottingham Forest",
    "nottingham forest": "Nottingham Forest",
    "nott'ham forest": "Nottingham Forest",
    "sunderland": "Sunderland",
    "tottenham": "Tottenham",
    "west ham": "West Ham",
    "west ham united": "West Ham",
    "wolves": "Wolves",
    "wolverhampton wanderers": "Wolves",
    # Champions League
    "psg": "Paris Saint-Germain",
    "paris s-g": "Paris Saint-Germain",
    "pafos fc": "Pafos",
}


def clean_team_name(name):
    """Return the name this project uses for a team."""
    # FBref puts the country code in front of European teams, e.g. "de Bayern Munich"
    name = re.sub(r"^[a-z]{2,3}\s+(?=[A-Z])", "", name.strip())
    name = " ".join(name.split())
    return TEAM_NAMES.get(name.lower(), name)

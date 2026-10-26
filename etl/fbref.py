"""Read the "Scores & Fixtures" table exported from FBref.

FBref blocks scrapers, so this file is downloaded by hand with the site's
"Share & Export" -> "Get table as CSV" button (see README).
It has every competition, not just the Premier League.
"""
import csv
import logging

from etl.teams import clean_team_name

log = logging.getLogger(__name__)

COMPETITIONS = {
    "Premier League": "Premier League",
    "Champions Lg": "UEFA Champions League",
    "FA Cup": "FA Cup",
    "EFL Cup": "EFL Cup",
}


def read_fixtures(csv_path):
    matches = []
    with open(csv_path, encoding="utf-8-sig") as f:
        lines = f.readlines()

    # sometimes the export has extra lines above the header, so start at the header row
    start = next(i for i, line in enumerate(lines) if line.startswith("Date,"))

    for row in csv.DictReader(lines[start:]):
        if row["Comp"] not in COMPETITIONS:
            log.warning("Unknown competition %r on %s, skipping", row["Comp"], row["Date"])
            continue
        if row["GF"] == "" or row["GA"] == "":
            continue  # not played yet

        matches.append({
            "date": row["Date"],
            "competition": COMPETITIONS[row["Comp"]],
            "opponent": clean_team_name(row["Opponent"]),
            # the FA Cup final was at Wembley ("Neutral"), I count it as a home game
            "is_home": row["Venue"] != "Away",
            # GF/GA and Poss are always from Chelsea's side
            "goals_for": int(row["GF"]),
            "goals_against": int(row["GA"]),
            "possession": float(row["Poss"]) if row["Poss"] else None,
            "attendance": int(row["Attendance"].replace(",", "")) if row["Attendance"] else None,
            "referee": row["Referee"] or None,
        })

    return matches

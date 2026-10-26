# Chelsea 2025/26 Season Dashboard

A project where I collect Chelsea's 2025/26 match and player stats, store them in a
PostgreSQL database and make a Power BI dashboard from it.

It covers all 59 games (Premier League, Champions League, FA Cup and EFL Cup).
Player stats are only for the 38 Premier League games.

## Where the data comes from

- **Understat** (understat.com): Premier League results, xG and player stats for each game.
  The script downloads this automatically.
- **FBref** (fbref.com): every competition's results, plus possession, attendance and referee.
  FBref blocks scripts, so I export this one by hand (see below).

## How to run it

You need Python 3.12+, PostgreSQL and Power BI Desktop.

1. Install the packages:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and put your PostgreSQL password in it.
3. Export the FBref fixtures:
   - Open https://fbref.com/en/squads/cff3d9bb/2025-2026/Chelsea-Stats
   - Go to the **Scores & Fixtures** table, then Share & Export, then Get table as CSV.
   - Save the text as `data/manual_exports/fbref_scores_fixtures_2025_2026.csv`.
4. Create the database and load the data:
   ```
   python scripts/setup_database.py
   python scripts/run_etl.py
   ```
5. Open `powerbi/ChelseaAnalytics.pbip` in Power BI Desktop and click **Refresh**.
   Log in with your PostgreSQL username and password (choose "Database" login).

Running `run_etl.py` again is fine, it updates the existing rows instead of adding duplicates.
The Understat data is saved in `data/raw/` the first time, use `--refresh` to download it again.

## Checking it works

```
pytest
psql -U postgres -d chelsea -f sql/data_quality_checks.sql
```

The database tests use a separate `chelsea_test` database, so they don't touch the real data.

## Files

```
etl/understat.py        downloads and reads the Understat data
etl/fbref.py            reads the FBref CSV
etl/teams.py            makes team names the same in both sources
etl/load.py             saves everything into the database
scripts/                setup_database.py and run_etl.py
sql/schema.sql          the tables (star schema)
sql/powerbi_views.sql   views that Power BI uses
powerbi/                the Power BI dashboard (3 pages)
tests/                  pytest tests
```

## Things to know

- xG is only for Premier League games (Understat doesn't have cup games).
- Player stats are only for the Premier League for the same reason.
- The FA Cup final was at a neutral ground, I counted it as a home game.
- The "Points" card counts 3/1/0 for every game shown. Pick Premier League in the
  filter to see the real league points.

"""Create the database, the tables and the Power BI views.

Run from the project folder:  python scripts/setup_database.py
Safe to run again, it doesn't delete anything.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from etl.database import connect  # noqa: E402


def main():
    db_name = os.getenv("DB_NAME", "chelsea")

    # create the database itself if it doesn't exist yet (needs a connection to the default db)
    conn = connect("postgres")
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if cur.fetchone() is None:
            cur.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Created database {db_name}")
    conn.close()

    conn = connect()
    with conn, conn.cursor() as cur:
        for sql_file in ["schema.sql", "powerbi_views.sql"]:
            cur.execute((ROOT / "sql" / sql_file).read_text(encoding="utf-8"))
            print(f"Ran sql/{sql_file}")
    conn.close()
    print("Database is ready.")


if __name__ == "__main__":
    main()

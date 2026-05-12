import os
from pathlib import Path

import pandas as pd
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine


def _get_connection_string() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return url


def get_db():
    conn = psycopg2.connect(
        _get_connection_string(),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    try:
        yield conn
    finally:
        conn.close()


def init_db(csv_data_path: Path):
    try:
        df = pd.read_csv(csv_data_path)
        engine = create_engine(_get_connection_string())
        with engine.begin() as conn:
            df.to_sql("smartphone_usage", conn, if_exists="replace", index=False)
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

    return True

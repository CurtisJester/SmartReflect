from sqlite3 import connect, Row
from pathlib import Path
import pandas as pd
from config import get_database_path


def get_db():
    """
    Get a database connection from the database filepath provided.
    
    Returns:
        A database connection
    """
    conn = connect('src/backend/db/database.db', check_same_thread=False)
    conn.row_factory = Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(csv_data_path: Path):
    try: 
        df = pd.read_csv(csv_data_path)
        conn = connect('src/backend/db/database.db')
        df.to_sql("smartphone_usage", conn, if_exists="replace", index=False)
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

    return True

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def get_connection():
    """
    Returns a new psycopg2 connection using environment variables.
    """
    dbname = os.getenv("PGDATABASE", "CSE412Project")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
        cursor_factory=RealDictCursor
    )
    return conn
import psycopg2
from psycopg2.extras import RealDictCursor

DB_NAME = "CSE412Project"
DB_USER = "yourusername"
DB_PASSWORD = "yourpassword"   # if no password, leave empty strings
DB_HOST = "/tmp"               # UNIX socket for  local server
DB_PORT = "8888"               # the PGPORT we use (feel free to edit)

def get_db():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )
    return conn

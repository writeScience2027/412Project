import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    """
    Returns a new psycopg2 connection. Uses environment variables with sensible defaults.
    - Set PGDATABASE, PGUSER, PGPASSWORD, PGHOST, PGPORT in  environment if needed.
    """
    dbname = os.getenv("PGDATABASE", "CSE412Project")
    user = os.getenv("PGUSER", None)            # optional if using socket auth
    password = os.getenv("PGPASSWORD", None)    # optional
    host = os.getenv("PGHOST", "/tmp")          # confirmed default /tmp
    port = os.getenv("PGPORT", "8888")         # default 8888

    conn_args = {
        "dbname": dbname,
        "cursor_factory": RealDictCursor
    }
    if user:
        conn_args["user"] = user
    if password:
        conn_args["password"] = password
    if host:
        conn_args["host"] = host
    if port:
        conn_args["port"] = port

    conn = psycopg2.connect(**conn_args)
    return conn

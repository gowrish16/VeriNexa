import os
from contextlib import contextmanager
from typing import Optional
from dotenv import load_dotenv
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

load_dotenv()

_pool: Optional[ThreadedConnectionPool] = None


def get_connection_pool(minconn: int = 2, maxconn: int = 25) -> ThreadedConnectionPool:
    """Thread-safe connection pool for concurrent database operations."""
    global _pool
    if _pool is None or _pool.closed:
        database_url = os.getenv("DATABASE_URL")
        _pool = ThreadedConnectionPool(minconn, maxconn, dsn=database_url)
    return _pool


@contextmanager
def get_db_connection():
    """Context manager yielding a pooled connection and guaranteeing return on exit."""
    pool = get_connection_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def check_connection():
    """Health check validating PostgreSQL connectivity."""
    database_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0]

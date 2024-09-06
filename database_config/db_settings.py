import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import OperationalError

from database_config.config import DB_CONFIG


class Database:
    def __init__(self):
        self.cursor = None
        self.conn = None

    def __enter__(self):
        try:
            # Connect to the database
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        except OperationalError as e:
            print(f"Error connecting to the database: {e}")
            raise e
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()

        # Close cursor and connection
        if self.cursor is not None:
            self.cursor.close()

        if self.conn is not None:
            self.conn.close()

    def execute(self, query: str, params: tuple = None):
        """
        Execute a SQL query with optional parameters.
        """
        try:
            self.cursor.execute(query, params)
        except Exception as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()
            raise e

    def fetchone(self, query: str, params: tuple = None):
        """
        Execute a SQL query and fetch one row.
        """
        self.execute(query, params)
        return self.cursor.fetchone()

    def fetchall(self, query: str, params: tuple = None):
        """
        Execute a SQL query and fetch all rows.
        """
        self.execute(query, params)
        return self.cursor.fetchall()

    def commit(self):
        """
        Manually commit the current transaction.
        """
        self.conn.commit()

    def rollback(self):
        """
        Manually rollback the current transaction.
        """
        self.conn.rollback()


def execute_query(query, params: tuple = None, fetch: str = None):
    """
    Execute a SQL query with parameters and return the result.
    """
    try:
        with Database() as db:
            if fetch == "one":
                result = db.fetchone(query, params)
                return result if result else None

            elif fetch == "all":
                result = db.fetchall(query, params)
                return result if result else []

            else:
                db.execute(query, params)
                return None

    except psycopg2.Error as e:
        print(f"Error executing query: {e}")
        raise e

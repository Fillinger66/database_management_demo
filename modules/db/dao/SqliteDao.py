
"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
from modules.db.dao.AbstractDao import AbrstractDao
import sqlite3
import time
import threading

class SqliteDao(AbrstractDao):
    """
    Base class for Data Access Objects (DAO) for SQLite database.
    This class provides basic database operations such as checking table existence,
    executing queries, and handling database locks.
    Subclasses should implement specific DAO functionality."""
    def __init__(self,connection: sqlite3.Connection = None,verbose: bool = False):
        """
        Initialize the DAO with a database connection.  
            :param connection: SQLite connection object. If None, ensure to set it before use.
            :param verbose: If True, print debug information. Default is False.
        """
        super().__init__(connection=connection, verbose=verbose)
        self._write_lock = threading.Lock()
        self.verbose = verbose


    def _ensure_connected(self):
        if self.conn is None:
            raise Exception(f"{self.__class__.__name__}::Error -> not connected. Provide a connection during initialization or ensure it's set.")

    def is_table_exist(self, table_name: str):
        """Check if a table exists in the database."""
        self._ensure_connected()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?;
        """, (table_name,))
        result = cursor.fetchone()
        if self.verbose:
            print(f"{self.__class__.__name__}::Checking if table '{table_name}' exists: {result is not None}")
        return result is not None

    def execute_query(self, query: str, params=None, fetch_one=False, fetch_all=False):
        """Execute a query on the database. Does NOT commit changes."""
        self._ensure_connected()

        if self.verbose:
            print(f"{self.__class__.__name__}::Executing query: {query} with params: {params}")

        cursor = self.conn.cursor()
        if params is None:
            params = ()
        cursor.execute(query, params)
        
        result = None
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()

        if self.verbose:
            print(f"{self.__class__.__name__}::Query executed. Result: {result}")
        # Do not commit here, let the caller or context manager handle it
        return result
    
    def _execute_with_retry(self, query, params=None, max_retries=5, retry_delay=0.1):
        """Helper to execute a query with retry logic for locked databases."""
        self._ensure_connected()
        if self.verbose:
            print(f"{self.__class__.__name__}::Executing with retry: {query} with params: {params}")

        attempt = 0
        while attempt < max_retries:
            try:
                with self._write_lock: # Assuming all writes need this lock
                    with self.conn: # This context manager handles commit/rollback
                        self.conn.execute(query, params if params is not None else ())

                if self.verbose:
                    print(f"{self.__class__.__name__}::Query executed successfully on attempt {attempt + 1}.")
                return True
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    attempt += 1
                    if self.verbose:
                        print(f"{self.__class__.__name__}::Database is locked, retrying {attempt}/{max_retries}...")
                    time.sleep(retry_delay)
                else:
                    if self.verbose:
                        print(f"{self.__class__.__name__}::SQLite error: {e}")
                    raise # Re-raise unexpected errors
        if self.verbose:
            print(f"{self.__class__.__name__}::Failed to execute after retries.")
        return False
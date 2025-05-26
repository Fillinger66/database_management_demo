"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
import sqlite3
from modules.db.dao.SqliteDao import SqliteDao 

class SqliteDaoUser(SqliteDao):
    """
    Data Access Object for User Management.
    This class handles all database operations related to user management,
    including creating users, retrieving user IDs, and deleting users.
    """

    tablename = "users"
    _field_id = "id"
    _field_username = "username"
    _field_password_hash = "password_hash"
    _field_email = "email"
    _field_created_at = "created_at"

    
    def __init__(self, connection: sqlite3.Connection,verbose :bool=False):
        """
        Initialize the DaoUser object with a database connection.
            :param connection: SQLite connection object.
        """
        super().__init__(connection,verbose)

    def is_table_exist(self):
        """
        Check if the users table exists in the database.
            :return: True if the table exists, False otherwise.
        """
        return super().is_table_exist(self.tablename)

    def create_table_users(self):
        """
        Create the users table in the database if it does not exist.
        This method defines the schema for the users table.
        The table includes fields for user ID, username, password hash,
        email, and creation timestamp.
        """
        self._ensure_connected()
        with self.conn:
            self.conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.tablename} (
                    {self._field_id} INTEGER PRIMARY KEY AUTOINCREMENT,
                    {self._field_username} TEXT UNIQUE NOT NULL,
                    {self._field_password_hash} TEXT,
                    {self._field_email} TEXT UNIQUE NOT NULL,
                    {self._field_created_at} DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def insert_user(self, username, password_hash, email, max_retries=5, retry_delay=0.1):
        """
        Insert a new user into the users table.
            :param username: Username of the new user.
            :param password_hash: Password hash of the new user.
            :param email: Email of the new user.
            :param max_retries: Maximum number of retries in case of a locked database. Default 5.
            :param retry_delay: Delay between retries in seconds. Default 0.1 seconds.
            :return: True if the user was successfully inserted, False otherwise.
        """
        return self._execute_with_retry( 
                                query=f"""
                                    INSERT INTO {self.tablename}
                                    ({self._field_username}, {self._field_password_hash}, {self._field_email})
                                    VALUES (?, ?, ?)
                                    """, 
                                params=(username, password_hash, email,), 
                                max_retries=5, 
                                retry_delay=0.1)
        

    def get_user_id_by_username(self, username):
        """
        Retrieve the user ID for a given username.
            :param username: Username of the user.
            :return: User ID if found, None otherwise.
        """

        return self.execute_query(query= 
                                 f"""
                                SELECT {self._field_id}
                                FROM {self.tablename}
                                WHERE {self._field_username} = ?
                                """, 
                                params=(username,), 
                                fetch_one=True, 
                                fetch_all=False)
    
    def get_all(self):
        """
        Retrieve all users.
            :return: all users in the users table.
        """

        return self.execute_query(query= 
                                 f"""
                                SELECT * 
                                FROM {self.tablename}
                                """, 
                                params=None, 
                                fetch_one=False, 
                                fetch_all=True)
       

    def delete_user(self, user_id ,max_retries=5, retry_delay=0.1):
        """
        Delete a user from the users table.
            :param user_id: ID of the user to be deleted.
            :param max_retries: Maximum number of retries in case of a locked database. Default 5.
            :param retry_delay: Delay between retries in seconds. Default 0.1 seconds.
            :return: True if the user was successfully deleted, False otherwise.
        """

        return self._execute_with_retry(query=
                                        f"""
                                        DELETE FROM {self.tablename}
                                        WHERE {self._field_id} = ?
                                        """, 
                                        params=(user_id,), 
                                        max_retries=5, 
                                        retry_delay=0.1)

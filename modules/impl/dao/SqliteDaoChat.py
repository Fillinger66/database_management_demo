"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
import sqlite3
from modules.db.dao.SqliteDao import SqliteDao

class SqliteDaoChat(SqliteDao):
    """
    Data Access Object for Chat History Management.
    This class handles all database operations related to chat history,
    including creating chat history, retrieving chat messages, and deleting chat history.
    """

    tablename = "chat_history"
    _field_id = "id"
    _field_session_id = "session_id"
    _field_user_id = "user_id"
    _field_role = "role"
    _field_text = "text"

    
    def __init__(self, connection: sqlite3.Connection,verbose :bool=False):
        """
        Initialize the DaoChat object with a database connection.
            :param connection: SQLite connection object.
            :param verbose: If True, print debug information. Default is False.
        """
        super().__init__(connection,verbose)       

    def is_table_exist(self):
        """
        Check if the chat history table exists in the database.
            :return: True if the table exists, False otherwise.
        """
        return super().is_table_exist(self.tablename)

    def create_table_chat_history(self):
        """
        Create the chat history table if it does not exist.
        This method is called to initialize the database schema for chat history.
        """
        self._ensure_connected()
        with self.conn:
            # To avoid circular imports, import DaoUser locally just before use.
            from modules.impl.dao.SqliteDaoUser import SqliteDaoUser
            self.conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.tablename} (
                    {self._field_id} INTEGER PRIMARY KEY AUTOINCREMENT,
                    {self._field_session_id} TEXT,
                    {self._field_user_id} INTEGER,
                    {self._field_role} INTEGER,
                    {self._field_text} TEXT,
                    FOREIGN KEY({self._field_user_id}) REFERENCES {SqliteDaoUser.tablename}({SqliteDaoUser._field_id}) ON DELETE CASCADE
                )
            """)

    def insert_chat_history(self, user_id, session_id, role, text, max_retries=5, retry_delay=0.1):
        """
        Insert a chat message into the chat history.
            :param user_id: ID of the user sending the message.
            :param session_id: ID of the chat session.
            :param role: Role of the user (e.g., "user", "...").
            :param text: Text of the chat message.
            :param max_retries: Maximum number of retries for database lock. Default 5.
            :param retry_delay: Delay between retries in seconds. Default 0.1 seconds.
            :return: True if insertion was successful, False otherwise.
        """
        return self._execute_with_retry( 
                                query=f"""INSERT INTO {self.tablename}
                                ({self._field_user_id}, {self._field_session_id}, {self._field_role}, {self._field_text})
                                VALUES (?, ?, ?, ?)""", 
                                params=(user_id, session_id, role, text), 
                                max_retries=5, 
                                retry_delay=0.1)


    def get_chat_history_by_user_id(self, user_id):
        """
        Retrieve chat history for a specific user ID.
            :param user_id: ID of the user.
            :return: List of chat messages for the user.
        """
        return self.execute_query(query= 
                                 f"""
                                SELECT {self._field_role}, {self._field_text}
                                FROM {self.tablename}
                                WHERE {self._field_user_id} = ?
                                """, 
                                params=(user_id,), 
                                fetch_one=False, 
                                fetch_all=True)
        

    def get_chat_history_for_user_and_session(self, user_id, session_id):
        """
        Retrieve chat history for a specific user ID and session ID.
            :param user_id: ID of the user.
            :param session_id: ID of the chat session.
            :return: List of chat messages for the user in the session.
        """
        return self.execute_query(query= 
                                f"""
                                SELECT {self._field_role}, {self._field_text}
                                FROM {self.tablename}
                                WHERE {self._field_user_id} = ? AND {self._field_session_id} = ?
                                """, 
                                params=(user_id, session_id), 
                                fetch_one=False, 
                                fetch_all=True)

        
        

    def delete_chat_history(self, user_id, session_id, max_retries=5, retry_delay=0.1):
        """
        Delete chat history for a specific user ID and session ID.
            :param user_id: ID of the user.
            :param session_id: ID of the chat session.
            :param max_retries: Maximum number of retries for database lock. Default 5.
            :param retry_delay: Delay between retries in seconds. Default 0.1 seconds.
            :return: True if deletion was successful, False otherwise.
        """

        return self._execute_with_retry( 
                                query=
                                f"""
                                DELETE FROM {self.tablename}
                                WHERE {self._field_user_id} = ? AND {self._field_session_id} = ?
                                """, 
                                params=(user_id, session_id), 
                                max_retries=5, 
                                retry_delay=0.1)

    def get_all_chat_history_by_user(self, user_id):
        """
        Retrieve all chat history for a specific user ID.
            :param user_id: ID of the user.
            :return: List of all chat messages for the user.
        """
        return self.execute_query(query= 
                                f"""
                                SELECT {self._field_session_id}, {self._field_role}, {self._field_text}
                                FROM {self.tablename}
                                WHERE {self._field_user_id} = ?
                                ORDER BY {self._field_session_id}, {self._field_id}
                                """, 
                                params=(user_id,), 
                                fetch_one=False, 
                                fetch_all=True)

    def get_distinct_sessions_for_user(self, user_id):
        """
        Retrieve distinct chat sessions for a specific user ID.
            :param user_id: ID of the user.
            :return: List of distinct session IDs for the user.
        """
        return self.execute_query(query= 
                               f"""
                                SELECT DISTINCT {self._field_session_id}
                                FROM {self.tablename}
                                WHERE {self._field_user_id} = ?
                                """,    
                                params=(user_id,), 
                                fetch_one=False, 
                                fetch_all=True)
       

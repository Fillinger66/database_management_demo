"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
from modules.db.factories.IDbFactory import IDbFactory
from modules.impl.connection.SqliteConnectionProvider import SqliteConnectionProvider
from modules.impl.dao.SqliteDaoChat import SqliteDaoChat
from modules.impl.dao.SqliteDaoUser import SqliteDaoUser


class SqliteDbFactory(IDbFactory):
    def __init__(self, database_path:str,verbose:bool=False):
        self.database_path = database_path
        self.verbose = verbose
        # Initialize the connection provider with the database path
        # This will create the directory if it does not exist  
        self._connection_provider = SqliteConnectionProvider(database_path)
        # Always ensure tables exist, safe due to "IF NOT EXISTS"
        self.initialize_database_tables()


    def get_connection(self):
        """
        Provides a new, configured SQLite connection 
        by delegating to the DbConnectionProvider.
        This method should be used by callers to manage their own connections
        or to pass to DAOs for a single transaction.
        """
        return self._connection_provider.get_connection()

    def initialize_database_tables(self):
        """
        Ensures all required tables exist in the database.
        This method can be safely called multiple times.
        """
        with self.get_connection() as conn: # Get a connection to initialize
            user_dao = SqliteDaoUser(connection=conn,verbose=self.verbose)
            user_dao.create_table_users()
            chat_dao = SqliteDaoChat(connection=conn,verbose=self.verbose)
            chat_dao.create_table_chat_history()
        print("Database tables ensured to exist.")

    def create_user(self, username, password_hash, email):
        """
        Create a new user in the database.
        A new connection is opened and closed for this single operation.
        """
        with self.get_connection() as conn:
            user_dao = SqliteDaoUser(connection=conn,verbose=self.verbose)
            return user_dao.insert_user(username, password_hash, email)

    def get_user_id(self, username):
        """
        Retrieve the user ID for a given username.
        :param username: Username of the user.
        :return: User ID if found, None otherwise.
        """
        with self.get_connection() as conn:
            user_dao = SqliteDaoUser(connection=conn,verbose=self.verbose)
            # DaoUser.get_user_id_by_username returns a sqlite3.Row object or None
            user_row = user_dao.get_user_id_by_username(username)
            if user_row:
                return user_row[SqliteDaoUser._field_id]
            return None

    def delete_user(self, user_id):
        """
        Delete a user from the users table.
        :param user_id: ID of the user to be deleted.
        :return: True if the user was successfully deleted, False otherwise.
        """
        with self.get_connection() as conn:
            user_dao = SqliteDaoUser(connection=conn,verbose=self.verbose)
            return user_dao.delete_user(user_id)

    def add_chat_message(self, user_id, session_id, role, text):
        """
        Add a chat message to the chat history.
        A new connection is opened and closed for this single operation.
        """
        with self.get_connection() as conn:
            chat_dao = SqliteDaoChat(connection=conn,verbose=self.verbose)
            return chat_dao.insert_chat_history(user_id, session_id, role, text)

    def get_chat_history(self, user_id, session_id):
        """
        Retrieve chat history for a specific user ID and session ID.
        :param user_id: ID of the user.
        :param session_id: ID of the chat session.
        :return: List of chat messages for the user in the session.
        """
        with self.get_connection() as conn:
            chat_dao = SqliteDaoChat(connection=conn,verbose=self.verbose)
            return chat_dao.get_chat_history_for_user_and_session(user_id, session_id)

    def get_chat_history_as_dicts(self, user_id: int, session_id: str) -> list[dict[str, any]]:
        """
        Retrieve chat history for a specific user ID and session ID,
        mapped into a list of dictionaries.

        :param user_id: ID of the user.
        :param session_id: ID of the chat session.
        :return: List of dictionaries, where each dictionary represents a chat message.
                 Keys correspond to column names in the database.
        """
        with self.get_connection() as conn:
            chat_dao = SqliteDaoChat(connection=conn, verbose=self.verbose)
            raw_messages = chat_dao.get_chat_history_for_user_and_session(user_id, session_id)

            # Convert sqlite3.Row objects to standard dictionaries
            chat_messages_dicts = []
            for row in raw_messages:
                chat_messages_dicts.append(dict(row)) # sqlite3.Row can be converted to dict
            return chat_messages_dicts

    def delete_chat_history(self, user_id, session_id):
        """
        Delete chat history for a specific user ID and session ID.
        :param user_id: ID of the user.
        :param session_id: ID of the chat session.
        :return: True if deletion was successful, False otherwise.
        """
        with self.get_connection() as conn:
            chat_dao = SqliteDaoChat(connection=conn,verbose=self.verbose)
            return chat_dao.delete_chat_history(user_id, session_id)

    def list_all_chat_history(self, user_id):
        """
        Retrieve all chat history for a specific user ID.
        :param user_id: ID of the user.
        :return: List of all chat messages for the user.
        """
        with self.get_connection() as conn:
            chat_dao = SqliteDaoChat(connection=conn,verbose=self.verbose)
            return chat_dao.get_all_chat_history_by_user(user_id)
            
    def list_chat_sessions(self, user_id):
        """
        Retrieve distinct chat sessions for a specific user ID.
        :param user_id: ID of the user.
        :return: List of distinct session IDs for the user.
        """
        with self.get_connection() as conn:
            chat_dao = SqliteDaoChat(connection=conn,verbose=self.verbose)
            # DaoChat.get_distinct_sessions_for_user already returns a list of session IDs
            return chat_dao.get_distinct_sessions_for_user(user_id)

    def register_user_with_initial_message(self, username, password_hash, email, initial_session_id, initial_message_role, initial_message_text):
        """
        Registers a new user and adds an initial chat message in a single transaction.
        """
        with self.get_connection() as conn:
            user_dao = SqliteDaoUser(connection=conn,verbose=self.verbose)
            chat_dao = SqliteDaoChat(connection=conn,verbose=self.verbose)
            try:
                user_inserted = user_dao.insert_user(username, password_hash, email)
                if not user_inserted:
                    raise Exception(f"Failed to insert user '{username}'.")

                user_id_row = user_dao.get_user_id_by_username(username)
                if user_id_row is None:
                    raise Exception(f"Failed to retrieve ID for new user '{username}'.")
                user_id = user_id_row[user_dao._field_id]

                message_added = chat_dao.insert_chat_history(user_id, initial_session_id, initial_message_role, initial_message_text)
                if not message_added:
                    raise Exception(f"Failed to add initial chat message for user '{username}'.")
                
                conn.commit() # Explicitly commit the transaction for this multi-DAO operation
                return True
            except Exception as e:
                conn.rollback() # Rollback if any part fails
                print(f"Transaction failed for user registration and initial message: {e}")
                return False
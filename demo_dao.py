import sqlite3
import os
import threading
import time
from random import randint
from typing import List, Dict, Any, Optional

# Assuming your DbConnectionProvider is in modules.db
from modules.impl.connection.SqliteConnectionProvider import SqliteConnectionProvider 

# Import your specific DAO implementations
from modules.impl.dao.SqliteDaoChat import SqliteDaoChat
from modules.impl.dao.SqliteDaoUser import SqliteDaoUser

# Define the database path for this test
DB_PATH = "database/test_dao.db"

def setup_db_and_daos(db_path: str, verbose: bool = False):
    """
    Sets up the database connection provider and initializes DAOs.
    Also ensures tables exist.
    """
    # Ensure the directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Initialize the connection provider
    conn_provider = SqliteConnectionProvider(database_path=db_path)
    
    # Get a connection to initialize tables
    with conn_provider.get_connection() as conn:
        user_dao = SqliteDaoUser(connection=conn, verbose=verbose)
        chat_dao = SqliteDaoChat(connection=conn, verbose=verbose)
        
        user_dao.create_table_users()
        chat_dao.create_table_chat_history()
        
    if verbose:
        print(f"Database tables initialized in {db_path}")
    
    return conn_provider # Return the provider so connections can be obtained later


def insert_messages_dao(conn_provider: SqliteConnectionProvider, user_id: int, session_id: str, num_messages: int, verbose: bool = False):
    """
    Function to be run by threads to insert multiple chat messages using the Chat DAO.
    Each thread gets its own connection for the operation.
    """
    for i in range(num_messages):
        with conn_provider.get_connection() as conn: # Get a new connection for each DAO operation
            chat_dao = SqliteDaoChat(connection=conn, verbose=verbose)
            role = "user"
            text = f"Concurrent message {i} from user {user_id} in session {session_id}"
            
            inserted = chat_dao.insert_chat_history(user_id, session_id, role, text)
            if verbose:
                print(f"{'Inserted' if inserted else 'Failed to insert'}: {text}")
            
        time.sleep(randint(0, 2) * 0.005) # Simulate some variable work

def menu_dao_test():
    # --- 1. Initial Setup ---
    print(f"--- DAO-only Test Script ---")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database file: {DB_PATH}")

    # Set up connection provider and ensure tables exist
    connection_provider = setup_db_and_daos(DB_PATH, verbose=True)

    while True:
        print("\n=== DAO Test Menu ===")
        print(" 1. Create a new user")
        print(" 2. Get user ID by username")
        print(" 3. Add chat message")
        print(" 4. Get chat history for user and session")
        print(" 5. Delete a user")
        print(" 6. Delete chat history for user and session")
        print(" 7. Insert multiple messages concurrently")
        print(" 8. List all chat history for a user ")
        print(" 9. List all distinct session IDs for a user")
        print(" 10. List all users")
        print(" 0. Quit")
        
        choice = input("Enter your choice: ").strip()

        # --- 2. Perform Operations ---
        if choice == "1":
            username = input("Username: ").strip()
            password_hash = input("Password hash: ").strip()
            email = input("Email: ").strip()
            
            with connection_provider.get_connection() as conn:
                user_dao = SqliteDaoUser(connection=conn, verbose=True)
                inserted = user_dao.insert_user(username, password_hash, email)
                if inserted:
                    # After successful insert, get the ID (assuming unique username/email)
                    user_data = user_dao.get_user_id_by_username(username)
                    user_id = user_data['id'] if user_data else None
                    print(f"User '{username}' created. ID: {user_id}")
                else:
                    print(f"Failed to create user '{username}'. (Might already exist)")

        elif choice == "2":
            username = input("Username to look up: ").strip()
            with connection_provider.get_connection() as conn:
                user_dao = SqliteDaoUser(connection=conn, verbose=True)
                user_data = user_dao.get_user_id_by_username(username)
                if user_data:
                    print(f"User found: ID={user_data['id']}")
                else:
                    print(f"User '{username}' not found.")

        elif choice == "3":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            session_id = input("Session ID: ").strip()
            role = input("Role (e.g., 'user', 'bot'): ").strip()
            text = input("Message text: ").strip()
            
            with connection_provider.get_connection() as conn:
                chat_dao = SqliteDaoChat(connection=conn, verbose=True)
                inserted = chat_dao.insert_chat_history(user_id, session_id, role, text)
                if inserted:
                    print(f"Message added for user {user_id}, session '{session_id}'.")
                else:
                    print("Failed to add message.")

        elif choice == "4":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            session_id = input("Session ID: ").strip()
            
            with connection_provider.get_connection() as conn:
                chat_dao = SqliteDaoChat(connection=conn, verbose=True)
                messages = chat_dao.get_chat_history_for_user_and_session(user_id, session_id)
                if messages:
                    print(f"Chat history for user {user_id} session '{session_id}':")
                    for msg in messages:
                        print(f"  [Role:{msg['role']}] {msg['text']}")
                else:
                    print("No messages found.")

        elif choice == "5":
            try:
                user_id = int(input("User ID to delete: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            
            with connection_provider.get_connection() as conn:
                user_dao = SqliteDaoUser(connection=conn, verbose=True)
                deleted = user_dao.delete_user(user_id)
                if deleted:
                    print(f"User {user_id} deleted.")
                else:
                    print(f"Failed to delete user {user_id}.")

        elif choice == "6":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            session_id = input("Session ID: ").strip()
            
            with connection_provider.get_connection() as conn:
                chat_dao = SqliteDaoChat(connection=conn, verbose=True)
                deleted = chat_dao.delete_chat_history(user_id, session_id)
                if deleted:
                    print("Chat history deleted.")
                else:
                    print("Failed to delete chat history.")

        elif choice == "7":
            try:
                num_threads = int(input("Number of threads: ").strip())
                messages_per_thread = int(input("Messages per thread: ").strip())
            except ValueError:
                print("Invalid input. Please enter integers.")
                continue

            user_ids_for_test = []
            session_ids_for_test = []

            print("Creating users for concurrent test...")
            with connection_provider.get_connection() as conn:
                user_dao_single = SqliteDaoUser(connection=conn, verbose=True)
                for i in range(num_threads):
                    username = f"test_user_{i}_{int(time.time())}"
                    email = f"test_user_{i}_{int(time.time())}@example.com"
                    password_hash = f"hash{i}"
                    
                    inserted = user_dao_single.insert_user(username, password_hash, email)
                    if inserted:
                        user_data = user_dao_single.get_user_id_by_username(username)
                        user_id = user_data['id'] if user_data else None
                        if user_id:
                            user_ids_for_test.append(user_id)
                            session_ids_for_test.append(f"session_dao_{i}")
                        else:
                            print(f"Warning: Could not retrieve ID for created user '{username}'. Skipping.")
                    else:
                        print(f"Warning: Failed to create user '{username}'. Skipping.")
            
            if len(user_ids_for_test) < num_threads:
                print(f"Could only create {len(user_ids_for_test)} out of {num_threads} users. Running test with available users.")
            
            threads = []
            start_time = time.time()
            for i in range(len(user_ids_for_test)):
                t = threading.Thread(target=insert_messages_dao, args=(connection_provider, user_ids_for_test[i], session_ids_for_test[i], messages_per_thread, False))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()
            end_time = time.time()

            print(f"Concurrent message insertion complete. Total time: {end_time - start_time:.2f} seconds.")
            print(f"Inserted {len(user_ids_for_test) * messages_per_thread} messages in total.")

        elif choice == "8":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            
            with connection_provider.get_connection() as conn:
                chat_dao = SqliteDaoChat(connection=conn, verbose=True)
                messages = chat_dao.get_all_chat_history_by_user(user_id)
                if messages:
                    print(f"All chat messages for user {user_id}:")
                    for msg in messages:
                        print(f"  [Session:{msg['session_id']}] [Role:{msg['role']}] {msg['text']}")
                else:
                    print("No messages found.")

        elif choice == "9":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            
            with connection_provider.get_connection() as conn:
                chat_dao = SqliteDaoChat(connection=conn, verbose=True)
                sessions = chat_dao.get_distinct_sessions_for_user(user_id)
                if sessions:
                    print(f"Distinct session IDs for user {user_id}:")
                    for session_row in sessions:
                        print(f"- {session_row[0]}") # sqlite3.Row returns a tuple for single column
                else:
                    print("No sessions found.")

        elif choice == "10":
            
            
            with connection_provider.get_connection() as conn:
                user_dao = SqliteDaoUser(connection=conn, verbose=True)
                users = user_dao.get_all()
                if users:
                    for user_row in users:
                        print(f"- {user_row[SqliteDaoUser._field_id]},  {user_row[SqliteDaoUser._field_username]}") # sqlite3.Row returns a tuple for single column
                else:
                    print("No user found.")

        elif choice == "0":
            print("Exiting.")
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    menu_dao_test()
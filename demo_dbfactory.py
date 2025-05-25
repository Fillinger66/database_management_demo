import threading
import time
from random import randint
import os
from  modules.impl.factories.SqliteDbFactory import SqliteDbFactory

# Define the database path
DB_PATH = "database/test_factory.db"

def insert_messages(factory: SqliteDbFactory, user_id, session_id, num_messages,verbose=False):
    """
    Function to be run by threads to insert multiple chat messages.
    """
    for i in range(num_messages):
        role = "user"
        text = f"Message {i} from user {user_id}"
        success = factory.add_chat_message(user_id, session_id, role, text)
        # In a high-concurrency scenario, printing for every message can be slow.
        # For a test, it's fine, but might be verbose.
        if verbose:
            print(f"{'Inserted' if success else 'Failed to insert'}: {text}") 
        # Simulate some variable work to increase chances of lock contention
        time.sleep(randint(0, 2) * 0.01) # Reduced sleep to make contention more likely

def menu():
    # Clean up old database before starting new test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database file: {DB_PATH}")

    factory = SqliteDbFactory(database_path=DB_PATH, verbose=True)

    while True:
        print("\n=== Database Factory Menu ===")
        print(" 1. Initialize database (create tables)")
        print(" 2. Create a new user")
        print(" 3. Get user ID by username")
        print(" 4. Add chat message")
        print(" 5. Get chat history for user and session")
        print(" 6. Delete a user")
        print(" 7. Delete chat history for user and session")
        print(" 8. Insert multiple messages concurrently (test threading)")
        print(" 9. List all chat history for a user")
        print("10. List all distinct session IDs for a user")
        print("11. Register user with initial message (transaction test)")
        print("12. List all chat messages for a user in a session (as dicts)")
        print(" 0. Quit")
        
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            # Corrected: Use initialize_database_tables
            factory.initialize_database_tables()
            print("Database initialized.")

        elif choice == "2":
            username = input("Username: ").strip()
            password_hash = input("Password hash: ").strip()
            email = input("Email: ").strip()
            if factory.create_user(username, password_hash, email):
                print(f"User '{username}' created.")
            else:
                print(f"Failed to create user '{username}'. (Username or email might already exist)")

        elif choice == "3":
            username = input("Username to look up: ").strip()
            # Corrected: Method name in factory
            user_id = factory.get_user_id(username)
            if user_id is not None:
                print(f"User ID for '{username}' is {user_id}")
            else:
                print(f"User '{username}' not found.")

        elif choice == "4":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            session_id = input("Session ID: ").strip()
            role = input("Role (e.g., 'user', 'bot'): ").strip()
            text = input("Message text: ").strip()
            
            if factory.add_chat_message(user_id, session_id, role, text):
                print("Message sent.")
            else:
                print("Failed to send message.")

        elif choice == "5":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            session_id = input("Session ID: ").strip()
           
            messages = factory.get_chat_history(user_id, session_id)
            if messages:
                print(f"Chat history for user {user_id} session '{session_id}':")
                for role, text in messages:
                    print(f"  [{role}] {text}")
            else:
                print("No messages found.")

        elif choice == "6":
            try:
                user_id = int(input("User ID to delete: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            
            if factory.delete_user(user_id):
                print(f"User {user_id} deleted.")
            else:
                print(f"Failed to delete user {user_id}.")

        elif choice == "7":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            session_id = input("Session ID: ").strip()
            
            if factory.delete_chat_history(user_id, session_id):
                print("Chat history deleted.")
            else:
                print("Failed to delete chat history.")

        elif choice == "8":
            try:
                num_threads = int(input("Number of threads: ").strip())
                messages_per_thread = int(input("Messages per thread: ").strip())
            except ValueError:
                print("Invalid input. Please enter integers.")
                continue

            user_ids = []
            session_ids = []

            # Create users for the threads
            print("Creating users for concurrent test...")
            for i in range(num_threads):
                username = f"thread_user_{i}_{int(time.time())}" # Add timestamp for uniqueness
                email = f"thread_user_{i}_{int(time.time())}@example.com"
                password_hash = f"hash{i}"
                if factory.create_user(username, password_hash, email):
                    user_id = factory.get_user_id(username)
                    if user_id is not None:
                        user_ids.append(user_id)
                        session_ids.append(f"session_{i}")
                    else:
                        print(f"Warning: Could not retrieve ID for user '{username}'. Skipping.")
                else:
                    print(f"Warning: Failed to create user '{username}'. Skipping.")
            
            if len(user_ids) < num_threads:
                print(f"Could only create {len(user_ids)} out of {num_threads} users. Running test with available users.")
            
            threads = []
            start_time = time.time()
            for i in range(len(user_ids)): # Iterate based on actual users created
                t = threading.Thread(target=insert_messages, args=(factory, user_ids[i], session_ids[i], messages_per_thread))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()
            end_time = time.time()

            print(f"Concurrent message insertion complete. Total time: {end_time - start_time:.2f} seconds.")
            print(f"Inserted {len(user_ids) * messages_per_thread} messages in total.")

        elif choice == "9":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            # Corrected: Method name in factory
            messages = factory.list_all_chat_history(user_id)
            if messages:
                print(f"All chat messages for user {user_id}:")
                for session_id, role, text in messages:
                    print(f"  [Session {session_id}] [{role}] {text}")
            else:
                print("No messages found.")

        elif choice == "10":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            # Corrected: Method name in factory
            sessions = factory.list_chat_sessions(user_id)
            if sessions:
                print(f"Distinct session IDs for user {user_id}:")
                for session in sessions:
                    print(f"- {session}")
            else:
                print("No sessions found.")

        elif choice == "11":
            username = input("Username for transaction: ").strip()
            password_hash = input("Password hash for transaction: ").strip()
            email = input("Email for transaction: ").strip()
            initial_session_id = input("Initial session ID for transaction: ").strip()
            initial_message_role = input("Initial message role for transaction: ").strip()
            initial_message_text = input("Initial message text for transaction: ").strip()
            
            if factory.register_user_with_initial_message(
                username, password_hash, email, initial_session_id, initial_message_role, initial_message_text
            ):
                print(f"Successfully registered user '{username}' and added initial message in a single transaction.")
            else:
                print(f"Failed to register user '{username}' and add initial message (transaction rolled back).")
        
        
        elif choice == "12":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            session_id = input("Session ID: ").strip()
            
            messages: list[dict[str, any]] = factory.get_chat_history_as_dicts(user_id, session_id)
            if messages:
                print(f"Chat history for user {user_id} session '{session_id}' (as dicts):")
                for msg_dict in messages:
                    # Print the dictionary directly or format it as needed
                    print(f"  {msg_dict}") 
            else:
                print("No messages found.")

        elif choice == "0":
            print("Exiting.")
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    menu()
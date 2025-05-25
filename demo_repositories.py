import threading
import time
from random import randint
import os
from typing import List, Dict, Any, Optional

# Import the necessary components from your layered architecture
from modules.db.connection.IDbConnectionProvider import IDbConnectionProvider         # Interface for connection
from modules.impl.connection.SqliteConnectionProvider import SqliteConnectionProvider # Concrete SQLite connection provider
from modules.impl.factories.SqliteRepositoryFactory import SqliteRepositoryFactory    # Factory for repositories
from modules.impl.repositories.IUserRepository import IUserRepository                 # Interface for User Repository
from modules.impl.repositories.IChatRepository import IChatRepository                 # Interface for Chat Repository
from modules.impl.models.User import User                                             # User model
from modules.impl.models.ChatMessage import ChatMessage                               # ChatMessage model

# Define the database path
DB_PATH = "database/test_repository.db" # Using a different DB file for the new demo

def insert_messages_repo(chat_repo: IChatRepository, user_id: int, session_id: str, num_messages: int, verbose: bool = False):
    """
    Function to be run by threads to insert multiple chat messages using the ChatRepository.
    """
    for i in range(num_messages):
        role = "user"
        text = f"Message {i} from user {user_id} in session {session_id}"
        
        # Create a ChatMessage object
        message = ChatMessage(user_id=user_id, session_id=session_id, role=role, text=text)
        
        # Use the repository to add the message
        message_id = chat_repo.add(message)
        
        if verbose:
            print(f"{'Inserted' if message_id else 'Failed to insert'}: {text} (ID: {message_id})") 
        
        time.sleep(randint(0, 2) * 0.01) # Simulate some variable work

def init_data(repo_factory: SqliteRepositoryFactory):
    """
    Initialize some test data in the database using the Repository Factory.
    This is just for demonstration purposes.
    """
    user_repo: IUserRepository = repo_factory.get_user_repository()
    chat_repo: IChatRepository = repo_factory.get_chat_repository()

    # Create a test user
    test_user = User(username="test_user", password_hash="hash123", email="test@email.com")
    user_id = user_repo.add(test_user)

    chat_message = ChatMessage(
        user_id=user_id,
        session_id="123",
        role="user",
        text="Hello, this is a test message."
    )
    chat_repo.add(chat_message)
    chat_message = ChatMessage(
        user_id=user_id,
        session_id="123",
        role="model",
        text="Hello, this is a test response."
    )
    chat_repo.add(chat_message)

def menu_repo():
    # Clean up old database before starting new test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database file: {DB_PATH}")

    # Initialize the lowest-level connection provider with SQLite provider
    db_connection_provider: IDbConnectionProvider = SqliteConnectionProvider(database_path=DB_PATH)
    
    # Initialize the Repository Factory with the connection provider
    repo_factory = SqliteRepositoryFactory(db_connection_provider)
    
    # Initialize database tables via the RepositoryFactory (which delegates to DAOs)
    repo_factory.initialize_database_tables()
    print("Database tables ensured to exist for Repository Demo.")
    # Initialize some test data
    init_data(repo_factory)

    # Get repository instances
    user_repo: IUserRepository = repo_factory.get_user_repository()
    chat_repo: IChatRepository = repo_factory.get_chat_repository()

    while True:
        print("\n=== Repository Layer Demo Menu ===")
        print(" 1.  Create a new user")
        print(" 2.  Get user by username")
        print(" 3.  Add chat message")
        print(" 4.  Get chat history for user and session")
        print(" 5.  Delete a user")
        print(" 6.  Delete chat history for user and session")
        print(" 7.  Insert multiple messages concurrently (test threading)")
        print(" 8.  List all chat history for a user")
        print(" 9.  List all distinct session IDs for a user")
        print(" 10. List all users")
        print(" 11. List all chat messages")
        print(" 0. Quit")
        
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            try:
                username = input("Username: ").strip()
                password_hash = input("Password hash: ").strip()
                email = input("Email: ").strip()
                
                new_user = User(username=username, password_hash=password_hash, email=email)
                user_id = user_repo.add(new_user) # add method updates new_user.id
                if user_id:
                    print(f"User '{new_user.username}' created with ID: {new_user.id}.")
                else:
                    print(f"Failed to create user '{new_user.username}'. (Username or email might already exist)")
            except ValueError as e:
                print(f"Error creating user: {e}")

        elif choice == "2":
            username = input("Username to look up: ").strip()
            user: Optional[User] = user_repo.get_by_username(username)
            if user:
                print(f"User found: ID={user.id}, Username='{user.username}', Email='{user.email}'")
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
            
            new_message = ChatMessage(user_id=user_id, session_id=session_id, role=role, text=text)
            message_id = chat_repo.add_message(new_message)
            if message_id:
                print(f"Message sent with ID: {new_message.id}.")
            else:
                print("Failed to send message.")

        elif choice == "4":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            session_id = input("Session ID: ").strip()
            
            messages: List[ChatMessage] = chat_repo.get_messages_by_session_id(user_id,session_id) # Assuming this method takes only session_id
            # If get_messages_by_session_id also requires user_id, adjust call here:
            # messages: List[ChatMessage] = chat_repo.get_messages_by_session_id(user_id, session_id)

            if messages:
                print(f"Chat history for user {user_id} session '{session_id}':")
                for msg in messages:
                    print(f"  [ID:{msg.id}] [User:{msg.user_id}] [Session:{msg.session_id}] [{msg.role}] {msg.text})")
            else:
                print("No messages found.")

        elif choice == "5":
            try:
                user_id = int(input("User ID to delete: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            
            if user_repo.delete(user_id):
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
            
            # Assuming a delete_messages_by_session_id method exists in ChatRepository
            if chat_repo.delete_messages_by_session_id(session_id):
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

            user_ids = []
            session_ids = []

            print("Creating users for concurrent test...")
            for i in range(num_threads):
                username = f"thread_user_{i}_{int(time.time())}"
                email = f"thread_user_{i}_{int(time.time())}@example.com"
                password_hash = f"hash{i}"
                
                new_user = User(username=username, password_hash=password_hash, email=email)
                user_id = user_repo.add(new_user)
                if user_id:
                    user_ids.append(new_user.id) # Use the ID updated in the User object
                    session_ids.append(f"session_repo_{i}")
                else:
                    print(f"Warning: Failed to create user '{username}'. Skipping.")
            
            if len(user_ids) < num_threads:
                print(f"Could only create {len(user_ids)} out of {num_threads} users. Running test with available users.")
            
            threads = []
            start_time = time.time()
            for i in range(len(user_ids)):
                # Pass the chat_repo instance, user_id, session_id
                t = threading.Thread(target=insert_messages_repo, args=(chat_repo, user_ids[i], session_ids[i], messages_per_thread, True))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()
            end_time = time.time()

            print(f"Concurrent message insertion complete. Total time: {end_time - start_time:.2f} seconds.")
            print(f"Inserted {len(user_ids) * messages_per_thread} messages in total.")

        elif choice == "8":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            
            # Assuming get_all_chat_history_by_user method exists in ChatRepository
            messages: List[ChatMessage] = chat_repo.get_all_chat_history_by_user(user_id)
            if messages:
                print(f"All chat messages for user {user_id}:")
                for msg in messages:
                    print(f"  [ID:{msg.id}] [Session:{msg.session_id}] [{msg.role}] {msg.text} (Time: {msg.timestamp})")
            else:
                print("No messages found.")

        elif choice == "9":
            try:
                user_id = int(input("User ID: ").strip())
            except ValueError:
                print("Invalid User ID. Please enter an integer.")
                continue
            
            # Assuming get_distinct_sessions_for_user method exists in ChatRepository
            sessions: List[str] = chat_repo.get_distinct_sessions_for_user(user_id)
            if sessions:
                print(f"Distinct session IDs for user {user_id}:")
                for session in sessions:
                    print(f"- {session}")
            else:
                print("No sessions found.")

        elif choice == "10":
            # List all users
            users: List[User] = user_repo.get_all()
            if users:
                print("All users:")
                for user in users:
                    print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
            else:
                print("No users found.")
        elif choice == "11":
            # List all chat messages
            messages: List[ChatMessage] = chat_repo.get_all()
            if messages:
                print("All chat messages:")
                for msg in messages:
                    print(f"ID: {msg.id}, User ID: {msg.user_id}, Session ID: {msg.session_id}, Role: {msg.role}, Text: {msg.text}")
            else:
                print("No chat messages found.")
        elif choice == "0":
            print("Exiting.")
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    menu_repo()
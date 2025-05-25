# modules/data/factories/RepositoryFactory.py
"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
"""
Factory Class: RepositoryFactory

This factory is responsible for creating and providing instances of
the Repository layer. It acts as an abstraction over the lower-level
DbFactory, making it easier for higher layers (like the application or service layer)
to obtain pre-configured repository objects.

Key principles demonstrated:
- Dependency Inversion Principle (DIP): It takes a DbFactory (or its connection)
  as a dependency, allowing for flexible wiring of the database access.
- Encapsulation: Hides the complexity of creating DAOs and wiring them
  to repositories from consumers.
- Layered Architecture: Clearly separates the concern of providing
  repositories from the concern of managing database connections and DAOs.

By using this factory, components only need to interact with repository interfaces
and this factory, without directly touching the DAos or the database connection management.
"""

import threading

# Import the necessary DAOs and Repositories
from modules.db.factories.IDbFactory import IDbFactory # We will depend on DbFactory
from modules.impl.dao.SqliteDaoUser import SqliteDaoUser # Need DaoUser for UserRepository
from modules.impl.dao.SqliteDaoChat import SqliteDaoChat # Need DaoChat for ChatRepository

from modules.impl.repositories.impl.SqliteUserRepository import UserRepository
from modules.impl.repositories.impl.SqliteChatRepository import SqliteChatRepository

from modules.db.connection.IDbConnectionProvider import IDbConnectionProvider

class SqliteRepositoryFactory(IDbFactory):
    _instance = None
    _lock = threading.Lock()
    _db_connection_provider: IDbConnectionProvider = None # Type hint the interface now

    def __new__(cls, db_connection_provider: IDbConnectionProvider): # Accept the interface
        """
        Singleton pattern for RepositoryFactory.
        It takes an instance of IDbConnectionProvider as a dependency.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SqliteRepositoryFactory, cls).__new__(cls)
                    cls._instance._db_connection_provider = db_connection_provider
        elif cls._instance._db_connection_provider != db_connection_provider:
            print(f"Warning: RepositoryFactory already initialized with a different IDbConnectionProvider instance.")
        return cls._instance

    def get_connection(self):
        """
        Provides a new, configured SQLite connection by delegating to the DbConnectionProvider.
        This method should be used by callers to manage their own connections
        or to pass to DAOs for a single transaction.
        """
        return self._db_connection_provider.get_connection()
    
    # Example of a method, no changes needed inside
    def get_user_repository(self) -> UserRepository:
        connection = self._db_connection_provider.get_connection() 
        dao_user = SqliteDaoUser(connection=connection) 
        return UserRepository(dao_user)
    
    def get_chat_repository(self) -> SqliteChatRepository:
        connection = self._db_connection_provider.get_connection()
        dao_chat = SqliteDaoChat(connection=connection)
        return SqliteChatRepository(dao_chat)
    
    def initialize_database_tables(self):
        print("Initializing database tables via RepositoryFactory (delegating to DAOs)...")
        with self._db_connection_provider.get_connection() as conn:
            user_dao = SqliteDaoUser(connection=conn)
            chat_dao = SqliteDaoChat(connection=conn)
            user_dao.create_table_users()
            chat_dao.create_table_chat_history()
        print("All tables initialized by RepositoryFactory.")
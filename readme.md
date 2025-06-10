# Database Management Demo - Project Explanation

## Overview

This project demonstrates different approaches to database management in Python using a layered architecture pattern. It showcases three main architectural patterns:

1. **Data Access Object (DAO) Pattern**
2. **Factory Pattern with Facade**
3. **Repository Pattern with Domain Models**

The project is structured to demonstrate clean architecture principles, separation of concerns, and [dependency inversion](https://en.wikipedia.org/wiki/Dependency_inversion_principle).

*To demonstrate the used of each layer, I used SQLite Database*

## Project Structure

```
modules/
├── db/                          # Abstract interfaces and base classes
│   ├── connection/
│   │   └── IDbConnectionProvider.py
│   ├── dao/
│   │   ├── AbstractDao.py
│   │   └── SqliteDao.py
│   ├── factories/
│   │   └── IDbFactory.py
│   └── repositories/
│       └── IRepository.py
└── impl/                        # Concrete implementations
    ├── connection/
    ├── dao/
    ├── factories/
    ├── models/
    └── repositories/

demo_dao.py                      # DAO Pattern demonstration
demo_dbfactory.py                # Factory Pattern demonstration  
demo_repositories.py             # Repository Pattern demonstration
```

## Analysis of the "db" Folder

The `db` folder contains the abstract interfaces and base classes that define the contracts for database operations. This follows the [**Dependency Inversion Principle**](https://en.wikipedia.org/wiki/Dependency_inversion_principle) where high-level modules depend on abstractions rather than concrete implementations.

### 1. Connection Layer

#### [`IDbConnectionProvider`](modules/db/connection/IDbConnectionProvider.py)

**Purpose**: Abstract interface for database connection providers.

**Key Features**:
- Defines the contract for providing database connections
- Database-agnostic interface (supports SQLite, MySQL, PostgreSQL, etc.)
- Enables easy swapping of database technologies without code changes

**Methods**:
- `get_connection()`: Returns a database connection object

**Usage**: Higher-level components depend on this interface rather than specific connection implementations, promoting loose coupling.

### 2. Data Access Object (DAO) Layer

#### [`AbstractDao`](modules/db/dao/AbstractDao.py)

**Purpose**: Abstract base class defining core DAO functionalities.

**Key Features**:
- Generic database interaction primitives
- Thread-safe operations with built-in locking
- Database-agnostic design

**Core Methods**:
- `_ensure_connected()`: Validates database connection state
- `is_table_exist(table_name)`: Checks table existence
- `execute_query()`: Executes read queries without committing
- `_execute_with_retry()`: Executes write queries with retry logic for concurrency

**Design Pattern**: Template Method Pattern - defines the skeleton of algorithms while letting subclasses override specific steps.

#### [`SqliteDao`](modules/db/dao/SqliteDao.py)

**Purpose**: SQLite-specific implementation of AbstractDao.

**Key Features**:
- SQLite-specific error handling and retry logic
- Connection validation and table existence checking
- Thread-safe write operations with automatic retry on database locks

**Specialized Functionality**:
- Handles SQLite's "database is locked" errors
- Uses SQLite's `sqlite_master` table for metadata queries
- Context manager support for automatic commit/rollback

### 3. Factory Layer

#### [`IDbFactory`](modules/db/factories/IDbFactory.py)

**Purpose**: Abstract factory for database initialization and connection provisioning.

**Key Features**:
- Standardizes database setup procedures
- Provides connection management interface
- Ensures database schema initialization

**Methods**:
- `get_connection()`: Provides database connections
- `initialize_database_tables()`: Sets up required database schema

**Design Pattern**: Abstract Factory Pattern - creates families of related objects without specifying their concrete classes.

### 4. Repository Layer

#### [`IRepository`](modules/db/repositories/IRepository.py)

**Purpose**: Generic repository interface for CRUD operations.

**Key Features**:
- Type-safe generic interface using TypeVar
- Standard CRUD operations for any entity type
- Domain-driven design support

**CRUD Operations**:
- `add(entity)`: Creates new entities
- `get_by_id(id)`: Retrieves entities by ID
- `update(entity)`: Updates existing entities
- `delete(id)`: Removes entities
- `get_all()`: Retrieves all entities

**Design Pattern**: Repository Pattern - encapsulates data access logic and provides a more object-oriented view of the persistence layer.

## Demo Applications

The project includes three interactive demonstration scripts that showcase each architectural pattern in action:

### 1. DAO Pattern Demo (`demo_dao.py`)

**Purpose**: Demonstrates direct database operations using Data Access Objects.

**Key Features**:
- Direct interaction with SQLite DAOs
- Low-level database operations
- Connection-per-operation pattern
- Thread-safe concurrent operations

**Menu Options**:
- User management (create, lookup, delete)
- Chat message operations (add, retrieve, delete)
- Concurrent message insertion testing
- Raw database interactions

**Architecture Demonstrated**:
```python
# Direct DAO usage
with connection_provider.get_connection() as conn:
    user_dao = SqliteDaoUser(connection=conn)
    chat_dao = SqliteDaoChat(connection=conn)
    user_dao.insert_user(username, password_hash, email)
```

**Benefits Shown**:
- Fine-grained control over database operations
- Explicit connection management
- Database-specific optimizations
- Low-level transaction control

### 2. Factory Pattern Demo (`demo_dbfactory.py`)

**Purpose**: Demonstrates the Factory pattern with Facade for simplified database operations.

**Key Features**:
- High-level database operations through factory interface
- Automatic connection management
- Transaction support
- Simplified API for common operations

**Menu Options**:
- User registration and management
- Chat operations with session management
- Transaction-based user registration with initial message
- Concurrent operations testing
- Chat history retrieval as dictionaries

**Architecture Demonstrated**:
```python
# Factory-based operations
factory = SqliteDbFactory(database_path=DB_PATH)
factory.initialize_database_tables()
factory.create_user(username, password_hash, email)
factory.add_chat_message(user_id, session_id, role, text)
```

**Benefits Shown**:
- Simplified API for business operations
- Automatic resource management
- Transaction encapsulation
- Reduced boilerplate code

### 3. Repository Pattern Demo (`demo_repositories.py`)

**Purpose**: Demonstrates domain-driven design using the Repository pattern.

**Key Features**:
- Domain object-oriented operations
- Strong typing with domain models
- Business logic encapsulation
- Clean separation between domain and data layers

**Menu Options**:
- Domain object manipulation (User, ChatMessage)
- Repository-based CRUD operations
- Session-based chat management
- Concurrent domain operations
- Entity relationship management

**Architecture Demonstrated**:
```python
# Repository pattern usage
user = User(username="john", email="john@example.com")
user_id = user_repository.add(user)

message = ChatMessage(user_id=user_id, session_id="123", 
                     role="user", text="Hello")
chat_repository.add(message)
```

**Benefits Shown**:
- Type-safe domain operations
- Object-oriented data access
- Business rule enforcement
- Clean domain model separation

## Architectural Benefits

### 1. **Separation of Concerns**
- **Connection Layer**: Manages database connections
- **DAO Layer**: Handles raw database operations
- **Repository Layer**: Provides domain-oriented data access
- **Factory Layer**: Manages object creation and initialization

### 2. **Dependency Inversion**
```python
# High-level modules depend on abstractions
user_repo: IUserRepository = factory.get_user_repository()
# Not on concrete implementations
# user_repo = SqliteUserRepository(dao)
```

### 3. **Open/Closed Principle**
- Open for extension: New database types can be added
- Closed for modification: Existing code doesn't need changes

### 4. **Testability**
- Interfaces can be easily mocked for unit testing
- Dependencies are injected rather than hard-coded

## Usage Patterns Comparison

### 1. **DAO Pattern Usage (Low-Level)**
```python
# Direct database operations
with connection_provider.get_connection() as conn:
    user_dao = SqliteDaoUser(connection=conn)
    user_dao.insert_user(username, password_hash, email)
```

### 2. **Factory Pattern Usage (Mid-Level)**
```python
# Simplified business operations
factory = SqliteDbFactory(database_path)
factory.create_user(username, password_hash, email)
```

### 3. **Repository Pattern Usage (High-Level)**
```python
# Domain-oriented operations
user = User(username="john", email="john@example.com")
user_id = user_repository.add(user)
```

## Demo Features Comparison

| Feature | DAO Demo | Factory Demo | Repository Demo |
|---------|----------|--------------|-----------------|
| **Abstraction Level** | Low | Medium | High |
| **Code Complexity** | High | Medium | Low |
| **Type Safety** | Basic | Medium | Strong |
| **Business Logic** | Manual | Encapsulated | Domain-Driven |
| **Connection Mgmt** | Explicit | Automatic | Automatic |
| **Transaction Support** | Manual | Built-in | Built-in |
| **Concurrency Testing** | ✓ | ✓ | ✓ |
| **Domain Models** | ✗ | Partial | ✓ |

## Threading and Concurrency

All demos include built-in support for concurrent operations:

- **Thread-safe DAO operations** with retry logic
- **Connection-per-operation** pattern for isolation
- **Database lock handling** with exponential backoff
- **Concurrent insertion testing** across all patterns

## Running the Demos

Each demo can be run independently:

```bash
# DAO Pattern Demo
python demo_dao.py

# Factory Pattern Demo  
python demo_dbfactory.py

# Repository Pattern Demo
python demo_repositories.py
```

## Extensibility

The modular design allows for easy extension:

1. **New Database Types**: Implement new connection providers and DAOs
2. **New Entity Types**: Create new repository interfaces and implementations
3. **New Business Logic**: Add domain methods to model classes

## Best Practices Demonstrated

1. **Interface Segregation**: Small, focused interfaces
2. **Single Responsibility**: Each class has one reason to change
3. **Composition over Inheritance**: Using dependency injection
4. **Error Handling**: Graceful degradation and retry mechanisms
5. **Resource Management**: Proper connection lifecycle management
6. **Progressive Abstraction**: From low-level DAOs to high-level repositories

This architecture provides a robust, scalable, and maintainable approach to database management while demonstrating clean architecture principles and design patterns across multiple abstraction levels.

# License

**This project is licensed under the **Educational and Non-Commercial Use License**.
See the [LICENSE](LICENSE) file for full details.**

---

<br>

**Made for educational purposes.**
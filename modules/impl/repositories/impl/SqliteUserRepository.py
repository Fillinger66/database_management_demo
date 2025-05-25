"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
from typing import List, Optional
import sqlite3 # Just for type hinting the connection for DaoUser

# Import the interface and the DAO
from modules.impl.repositories.IUserRepository import IUserRepository
from modules.impl.dao.SqliteDaoUser import SqliteDaoUser
from modules.impl.models.User import User 

class UserRepository(IUserRepository):
    """
    Concrete implementation of IUserRepository using DaoUser for SQLite persistence.
    Maps database rows to User domain models and vice-versa.
    """
    def __init__(self, dao_user: SqliteDaoUser):
        if not isinstance(dao_user, SqliteDaoUser):
            raise TypeError("dao_user must be an instance of DaoUser")
        self._dao_user = dao_user

    def _map_row_to_user(self, row: sqlite3.Row) -> Optional[User]:
        """Helper to map a sqlite3.Row object to a User domain model."""
        if row:
            # Note: sqlite3.Row allows dictionary-like access
            return User(
                id=row[SqliteDaoUser._field_id],
                username=row[SqliteDaoUser._field_username],
                password_hash=row[SqliteDaoUser._field_password_hash],
                email=row[SqliteDaoUser._field_email],
                created_at=row[SqliteDaoUser._field_created_at]
            )
        return None

    def add(self, user: User) -> Optional[int]:
        success = self._dao_user.insert_user(user.username, user.password_hash, user.email)
        if success:
            # After insertion, we need the last inserted ID.
            # SQLite's cursor.lastrowid is usually available after an INSERT.
            # We need to expose this from DaoUser's _execute_with_retry if possible,
            # or fetch it separately. For now, let's assume we can query it.
            # A cleaner way would be for DaoUser to return lastrowid.
            last_id_row = self._dao_user.execute_query("SELECT last_insert_rowid()", fetch_one=True)
            if last_id_row:
                user.id = last_id_row[0] # Update the user object with the new ID
                return user.id
        return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        query = f"""SELECT 
                    {self._dao_user._field_id}, {self._dao_user._field_username},
                    {self._dao_user._field_password_hash}, {self._dao_user._field_email}, 
                    {self._dao_user._field_created_at} 
                    FROM {self._dao_user.tablename} WHERE {self._dao_user._field_id} = ?"""
        row = self._dao_user.execute_query(query, (user_id,), fetch_one=True)
        return self._map_row_to_user(row)

    def get_by_username(self, username: str) -> Optional[User]:
        # DaoUser.get_user_id_by_username only returns ID, which is not enough for the full User object.
        # We need a new method in DaoUser or a direct query here to get all fields.
        query = f"""SELECT 
                    {self._dao_user._field_id}, {self._dao_user._field_username},
                    {self._dao_user._field_password_hash}, {self._dao_user._field_email},
                    {self._dao_user._field_created_at} 
                    FROM {self._dao_user.tablename}
                    WHERE {self._dao_user._field_username} = ?"""
        row = self._dao_user.execute_query(query, (username,), fetch_one=True)
        return self._map_row_to_user(row)

    def update(self, user: User) -> bool:
        # Implement update logic using dao_user._execute_with_retry
        if user.id is None:
            raise ValueError("User ID must be provided for update.")
        query = f"""UPDATE {self._dao_user.tablename} 
                    SET {self._dao_user._field_username} = ?, 
                        {self._dao_user._field_password_hash} = ?, 
                        {self._dao_user._field_email} = ? 
                    WHERE {self._dao_user._field_id} = ?"""
        params = (user.username, user.password_hash, user.email, user.id)
        return self._dao_user._execute_with_retry(query, params)

    def delete(self, user_id: int) -> bool:
        return self._dao_user.delete_user(user_id)

    def get_all(self) -> List[User]:
        query = f"""SELECT 
                    {self._dao_user._field_id}, {self._dao_user._field_username}, 
                    {self._dao_user._field_password_hash}, {self._dao_user._field_email}, 
                    {self._dao_user._field_created_at} 
                    FROM {self._dao_user.tablename}"""
        rows = self._dao_user.execute_query(query, fetch_all=True)
        return [self._map_row_to_user(row) for row in rows] if rows else []
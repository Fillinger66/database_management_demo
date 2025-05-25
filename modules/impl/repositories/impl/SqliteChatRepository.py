"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
from typing import List, Optional
import sqlite3 # Just for type hinting

# Import the interface and the DAO
from modules.impl.repositories.IChatRepository import IChatRepository
from modules.impl.dao.SqliteDaoChat import SqliteDaoChat
from modules.impl.models.ChatMessage import ChatMessage # Your domain model

class SqliteChatRepository(IChatRepository):
    """
    Concrete implementation of IChatRepository using DaoChat for SQLite persistence.
    Maps database rows to ChatMessage domain models and vice-versa.
    """
    def __init__(self, dao_chat: SqliteDaoChat):
        if not isinstance(dao_chat, SqliteDaoChat):
            raise TypeError("dao_chat must be an instance of DaoChat")
        self._dao_chat = dao_chat

    def _map_row_to_chat_message(self, row: sqlite3.Row) -> Optional[ChatMessage]:
        """Helper to map a sqlite3.Row object to a ChatMessage domain model."""
        if row:
            return ChatMessage(
                id=row[self._dao_chat._field_id],
                session_id=row[self._dao_chat._field_session_id],
                user_id=row[self._dao_chat._field_user_id],
                role=row[self._dao_chat._field_role],
                text=row[self._dao_chat._field_text]
            )
        return None

    def add(self, message: ChatMessage) -> Optional[int]:
        success = self._dao_chat.insert_chat_history(
             message.user_id,message.session_id, message.role, message.text
        )
        if success:
            last_id_row = self._dao_chat.execute_query("SELECT last_insert_rowid()", fetch_one=True)
            if last_id_row:
                message.id = last_id_row[0]
                return message.id
        return None

    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        query = f"""SELECT 
                    {self._dao_chat._field_id}, {self._dao_chat._field_session_id}, 
                    {self._dao_chat._field_user_id}, {self._dao_chat._field_role},{self._dao_chat._field_text} 
                    FROM {self._dao_chat.tablename} 
                    WHERE {self._dao_chat._field_id} = ?"""
        row = self._dao_chat.execute_query(query, (message_id,), fetch_one=True)
        return self._map_row_to_chat_message(row)

    def get_messages_by_session_id(self,user_id, session_id: str) -> List[ChatMessage]:
        query = f"""SELECT {self._dao_chat._field_id}, {self._dao_chat._field_session_id}, 
                    {self._dao_chat._field_user_id}, {self._dao_chat._field_role},{self._dao_chat._field_text} 
                    FROM {self._dao_chat.tablename} 
                    WHERE {self._dao_chat._field_session_id} = ? AND {self._dao_chat._field_user_id} = ? """
        rows = self._dao_chat.execute_query(query, (user_id,session_id,), fetch_all=True)
        return [self._map_row_to_chat_message(row) for row in rows] if rows else []

    def delete_messages_by_session_id(self, session_id: str) -> bool:
        return self._dao_chat.delete_chat_history_by_session_id(session_id)

    def delete(self, message_id: int) -> bool:
        # Assuming DaoChat has a method to delete by message ID
        # If not, you'd add it to DaoChat first or use a generic delete query via Dao
        query = f"DELETE FROM {self._dao_chat.tablename} WHERE {self._dao_chat._field_id} = ?"
        return self._dao_chat._execute_with_retry(query, (message_id,))
    
    def update(self, message: ChatMessage) -> bool:
        # Assuming DaoChat has a method to delete by message ID
        # If not, you'd add it to DaoChat first or use a generic delete query via Dao
        query = f"""UPDATE {self._dao_chat.tablename} 
                    SET {self._dao_chat._field_role} = ?, 
                        {self._dao_chat._field_text} = ?, 
                        {self._dao_chat._field_session_id} = ? 
                        {self._dao_chat._field_user_id} = ?, 
                    WHERE {self._dao_chat._field_id} = ?"""
        
        params = (message.role, message.text, message.session_id,message.user_id,message.id)
        return self._dao_user._execute_with_retry(query, params)
    
   
    
    def get_all(self) -> List[ChatMessage]:
        """
        Retrieve all chat messages from the repository.
        :return: A list of all ChatMessage domain objects.
        """
        query = f"""SELECT 
                    {self._dao_chat._field_id}, {self._dao_chat._field_session_id},
                    {self._dao_chat._field_user_id}, {self._dao_chat._field_role}, {self._dao_chat._field_text}
                    FROM {self._dao_chat.tablename}"""
        rows = self._dao_chat.execute_query(query, fetch_all=True)
        return [self._map_row_to_chat_message(row) for row in rows] if rows else []
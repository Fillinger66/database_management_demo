"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

# Import your domain model
from modules.impl.models.ChatMessage import ChatMessage
from modules.db.repositories.IRepository import IRepository

class IChatRepository(IRepository[ChatMessage]):
    """
    Abstract Base Class (Interface) for Chat Repositories.
    Defines the contract for interacting with ChatMessage data.
    """

    @abstractmethod
    def get_messages_by_session_id(self,user_id: int, session_id: str) -> List[ChatMessage]:
        """
        Retrieves all chat messages for a given session ID, ordered by timestamp.
            :param session_id: The ID of the chat session.
            :return: A list of ChatMessage domain objects.
        """
        pass

    @abstractmethod
    def delete_messages_by_session_id(self, session_id: str) -> bool:
        """
        Deletes all chat messages associated with a specific session ID.
            :param session_id: The ID of the chat session.
            :return: True if messages were deleted, False otherwise.
        """
        pass

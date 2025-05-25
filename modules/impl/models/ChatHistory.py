"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
from typing import List
from modules.impl.models.ChatMessage import ChatMessage

class ChatHistory:
    """
    Represents a chat history for a user in a specific session.
    This class manages a list of ChatMessage objects, allowing for easy addition and retrieval of messages.
    """
    def __init__(self,user_id:int = None,session_id:str = None, messages: List[ChatMessage] = None):
        self._messages = messages if messages is not None else []
        self.session_id=session_id
        self.user_id=user_id

    def add_message(self, message: ChatMessage):
        self._messages.append(message)
       

    def get_messages(self) -> List[ChatMessage]:
        return list(self._messages) # Return a copy to prevent external modification

    def to_list_of_dicts(self) -> List[dict]:
        """Converts chat history to a list of dictionaries, useful for APIs."""
        return [msg.to_dict() for msg in self._messages]

    def __len__(self):
        return len(self._messages)

    def __str__(self):
        return f"ChatHistory with {len(self._messages)} messages."
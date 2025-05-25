"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
"""
Model: ChatMessage

This file defines the 'ChatMessage' domain model, representing a single message
within the application's chat history. Similar to the 'User' model, this class
is a core business entity, independent of the underlying database technology.

Its purpose is to:
- Provide a rich, type-safe representation of a chat message.
- Encapsulate data and domain-specific behavior related to a chat message
  (e.g., validation rules for its content, roles, or session ID).
- Decouple the application's business logic from the specific
  database schema used to store chat messages.
- Act as a standard data structure for passing chat message data
  between different layers of the application.
"""
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ChatMessage:
    """
    Represents a single chat message in the application's domain.
    """
    id: int = field(default=None)
    session_id: str = field(default=None)
    user_id: int = field(default=None)
    role: str = field(default=None) # 'user', 'model', 'system' etc.
    text: str = field(default=None)

    def __post_init__(self):
        # This method is a dataclass feature that's called after the standard __init__. 
        # It's perfect for initial validation and data conversion (like string-to-datetime from SQLite database) 

        # Add any domain-specific validation or methods here
        if self.session_id is None or not self.session_id.strip():
            raise ValueError("Chat message must have a session ID.")
        if self.user_id is None:
            raise ValueError("Chat message must be associated with a user.")
        if self.role is None or not self.role.strip():
            raise ValueError("Chat message must have a role (e.g., 'user', 'bot').")
        if self.text is None or not self.text.strip():
            raise ValueError("Chat message cannot be empty.")

    def to_dict(self):
        """Converts the ChatMessage object to a dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "role": self.role,
            "text": self.text
        }
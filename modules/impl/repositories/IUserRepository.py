"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
from abc import abstractmethod
from modules.db.repositories.IRepository import IRepository
from typing import List, Optional # For type hinting

# Import your model
from modules.impl.models.User import User

class IUserRepository(IRepository[User]):
    """
    Abstract Base Class (Interface) for User Repositories.
    Defines the contract for interacting with User data.
    The application logic will depend on this interface, not on a specific.
    With the implementation, you will be able to use any database you want 
    (e.g., a SQLite-backed repository).
    """
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieves a user by their username.
            :param username: The username of the user.
            :return: The User domain object if found, otherwise None.
        """
        pass


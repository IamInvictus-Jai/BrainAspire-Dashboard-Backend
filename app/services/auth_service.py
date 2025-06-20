# from fastapi import status, HTTPException
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth_schema import UserInDB, Auth
from app.core.security import Security
from app.exceptions.authExceptions import InvalidCredentials, UserNotFound, AccessDenied
from app.repositories.auth_repository import AuthRepository
# from app.utils.timeFormat import format_ist

class AuthService:
    def __init__(self, security:Security, repo:AuthRepository, collection_name:str = "auth"):
        """
        Initialize the AuthService with security, repository, and collection name.

        Args:
            security (Security): The security service for handling authentication and token operations, injected by dependency injection.
            repo (AuthRepository): The repository used for database operations related to authentication, injected by dependency injection.
            collection_name (str, optional): The name of the MongoDB collection for storing authentication data. Defaults to "auth",  injected by dependency injection.
        """

        self.repo = repo
        self.security = security
        self.collection_name = collection_name
    
    def authenticate(self, user_id:str, password:str):
        """
        Authenticates a user

        Args:
            user_id (str): The id of the user
            password (str): The password of the user

        Returns:
            str: An access token for the user

        Raises:
            UserNotFound: If the user does not exist
            InvalidCredentials: If the password is wrong
        """

        user:Auth = self.repo.get_user_by_id(user_id=user_id, collection_name=self.collection_name)

        if not user:
            raise UserNotFound(f"User {user_id} does not exist")
        
        if not user.is_active:
            raise AccessDenied(f"User {user_id} is no longer active or have been blocked by the admin")

        if not self.security.verify_password(password, user.hashed_pswd):
            raise InvalidCredentials("Wrong password")
        
        # print(f"User {user_id} last logged in at {format_ist(user.last_login)}")
        self.repo.update_user_last_login(user_id=user_id, collection_name=self.collection_name)
        return self.security.create_access_token(user_id=user.userID)
    

from app.db.client import MongoDBClient
from app.schemas.auth_schema import UserInDB, Auth
from datetime import datetime, timezone

# from app.utils.code_profiler import log_timeit

class AuthRepository:
    def __init__(self, db:MongoDBClient):
        self.db = db
    
    # @log_timeit("Find User by ID")
    def get_user_by_id(self, user_id:str, collection_name:str) -> UserInDB | None:
        """
        Get a user by user_id from a given collection_name

        Args:
            user_id (str): User's id
            collection_name (str): Name of the MongoDB collection to query

        Returns:
            UserInDB | None: The user if found, None otherwise
        """
        user = self.db.find_one(collection_name, {"userID": user_id})
        return Auth(**user) if user else None

    # @log_timeit("Update User Last Login")
    def update_user_last_login(self, user_id:str, collection_name:str):
        """
        Update the last_login field of a user in a given collection_name

        Args:
            user_id (str): User's id
            collection_name (str): Name of the MongoDB collection to query
        Returns:
            None
        """
        self.db.update(collection_name, {"userID": user_id}, {"last_login": datetime.now(timezone.utc)})
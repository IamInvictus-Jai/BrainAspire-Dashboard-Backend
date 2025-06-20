from app.db.client import MongoDBClient

class BaseRepository:
    def __init__(self, db: MongoDBClient):
        self.db = db
    
    def connect(self):
        """
        Connect to the MongoDB database

        Raises:
            ConnectionFailure: If the connection fails
        """
        self.db.connect()
    
    def close(self):
        """
        Close the MongoDB connection

        Returns:
            - None
        """
        self.db.close()
    
    def create_indexes(self):
        """
        Create MongoDB indexes on the collection

        Args:
            - collection_name (str): Name of the MongoDB collection to create index on
            - key (str): Name of the field on which to create the index
            - unique (bool): Whether the index should be unique or not

        Returns:
            - None
        """
        self.db.create_index(collection_name="auth", key="userID", unique=True)
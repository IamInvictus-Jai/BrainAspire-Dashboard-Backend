from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi
from app.config.settings import Settings
from logging import Logger
from bson import ObjectId
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_fixed

class MongoDBClient:

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def __init__(self, settings:Settings, logger:Logger):
        try:
            user = settings.mongodb_user
            password = settings.mongodb_password
            cluster = settings.mongodb_cluster
            self.uri = f"mongodb+srv://{user}:{password}@{cluster}.mongodb.net/?retryWrites=true&w=majority"
            self.logger = logger
            
        except Exception as e:
            self.client = None
            self.logger.error(f"Database connection error: {str(e)}")

    def connect(self, database_name:str = "dashboard"):
        try:
            if not self.uri:
                self.logger.error("MongoDB URI is not set")
                return
            client = MongoClient(self.uri, serverSelectionTimeoutMS=5000, server_api=ServerApi('1'))
            self.database = client[database_name]

            client.admin.command('ping')
            self.logger.info("Connected to MongoDB successfully!")

        except ConnectionFailure as e:
            self.logger.error(f"MongoDB connection failed: {str(e)}")
            raise

        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def create_index(self, collection_name, key, unique=False):
        try:
            self.database[collection_name].create_index(key, unique=unique)
            self.logger.info(f"Index created successfully at collection: {collection_name} on key: {key}!")
        except Exception as e:
            self.logger.error(f"Failed to create index: {str(e)}")
            raise

    def verify_connection(self):
        """Verify MongoDB connection is working"""
        if not self.client:
            connection_string = f"mongodb+srv://{self.settings.mongodb_user}:{self.settings.mongodb_password}@{self.settings.mongodb_cluster}"
            self.client = MongoClient(connection_string)
        
        try:
            # The ismaster command is cheap and does not require auth
            self.client.admin.command('ismaster')
            return True
        except ConnectionFailure as e:
            self.logger.error(f"MongoDB connection failed: {str(e)}")
            raise

    def insert(self, collection_name, data) -> Optional[ObjectId]:
        """
        Returns the id of the inserted document
        Returns None if failed
        """
        try:
            result = self.database[collection_name].insert_one(data)
            if result.acknowledged:
                # self.logger.info(f"Document inserted successfully with id: {result.inserted_id}")
                return result.inserted_id  # Returns the ObjectId
            return None
        except Exception as e:
            self.logger.error("Exception while inserting data in database")
            self.logger.error(e)
            return None
    
    def insert_many(self, collection_name, data):
        try:
            result = self.database[collection_name].insert_many(data)
            if result.acknowledged:
                self.logger.info(f"Documents inserted successfully with ids: {result.inserted_ids}")
                return result.inserted_ids  # Returns the ObjectId
            return None
        except Exception as e:
            self.logger.error("Exception while inserting data in database")
            self.logger.error(e)
            return None

    def find(self, collection_name, query):
        return self.database[collection_name].find(query)
    
    def find_one(self, collection_name, query):
        return self.database[collection_name].find_one(query)
    
    def update(self, collection_name, query, data):
        try:
            # Update the document with the new data
            self.database[collection_name].update_one(query, {"$set": data})
            # self.logger.info("Document updated successfully!")
            return True
        except Exception as e:
            self.logger.error("Exception while updating data in MongoDB\nException in utils/dbHandler.py update function")
            self.logger.error(e)
            return False
    
    def delete(self, collection_name: str, query: dict) -> bool:
        try:
            result = self.database[collection_name].delete_one(query)
            if result.deleted_count > 0:
                self.logger.info(f"Document deleted successfully!")
                return True
            return False
        except Exception as e:
            self.logger.error("Exception while deleting data from MongoDB\nException in utils/dbHandler.py delete function")
            self.logger.error(e)
            return False
        
    def close(self):
        self.client.close()


if __name__ == "__main__":
    client = MongoDBClient()
    client.connect()
    client.close()
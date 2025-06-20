from app.db.client import MongoDBClient


class PaymentRepository:
    def __init__(self, db: MongoDBClient):
        self.db = db

    def get_course_fees_config(self, collection_name:str='course-fee-config'):
        return self.db.find_one(collection_name, {})    # return first record
    
    def get_discount_config(self, collection_name:str='discount-config'):
        return self.db.find_one(collection_name, {})    # return first record
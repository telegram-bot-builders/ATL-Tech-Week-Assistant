from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self, database, table):
        self.database = database
        self.table = table
        self.client = self._connect_to_server()
        self.collection = self._connect_to_database()

    def _connect_to_server(self):
        MONGODB_PWD = os.getenv('MONGODB_PWD')
        MONGODB_USER = os.getenv('MONGODB_USER')
        uri = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PWD}@cluster0.jcrcool.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        return MongoClient(uri, server_api=ServerApi('1'))

    def _connect_to_database(self):
        db = self.client[self.database]
        return db[self.table]

    def submit_user(self, user):
        try:
            existing_user = self.collection.find_one({"user_id": user["user_id"]})
            if existing_user is None:
                self.collection.insert_one(user)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error submitting user: {e}")
            return False

    def update_user(self, user):
        try:
            result = self.collection.update_one({"user_id": user["user_id"]}, {"$set": user})
            if result.modified_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

_db = Database("Authenication", "Users")

if __name__ == '__main__':
    pass
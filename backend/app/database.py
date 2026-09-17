import os
from typing import Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

# Load environment variables from .env file
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/smart_task_ai")
DATABASE_NAME = os.getenv("MONGODB_DB_NAME", "smart_task_ai")

_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    """Returns a singleton MongoDB client."""
    global _client
    if _client is None:
        mongo_url = os.getenv("MONGODB_URL", MONGODB_URL).strip()
        if not mongo_url:
            raise RuntimeError("MONGODB_URL environment variable is not configured.")
        _client = MongoClient(mongo_url, serverSelectionTimeoutMS=3000)
    return _client


def get_database() -> Database:
    """Returns the database instance."""
    client = get_mongo_client()
    return client[DATABASE_NAME]


def get_task_collection() -> Collection:
    """Returns the tasks collection."""
    db = get_database()
    return db["tasks"]


def check_db_connection() -> bool:
    """Checks whether the MongoDB instance is reachable."""
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return True
    except Exception:
        return False

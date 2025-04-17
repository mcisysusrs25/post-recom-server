import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import certifi

# Load environment variables
load_dotenv()

# Get MongoDB connection URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")

try:
    print("Connecting to MongoDB...")
    # Create a new client and connect to the server with TLS/SSL configuration
    client = MongoClient(
        MONGO_URI,
        server_api=ServerApi('1'),
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )

    # Test connection
    client.admin.command('ping')
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")

    # Get database
    db = client['postrecds']

    # Get collections
    users_collection = db.users
    posts_collection = db.posts
    interactions_collection = db.interactions
    user_profiles_collection = db.profiles

    # Create indexes
    users_collection.create_index([("email", ASCENDING)], unique=True)
    interactions_collection.create_index(
        [("user", ASCENDING), ("post", ASCENDING), ("interactionType", ASCENDING)],
        unique=True
    )
    user_profiles_collection.create_index([("user", ASCENDING)], unique=True)
    posts_collection.create_index([("user", ASCENDING)])
    posts_collection.create_index([("tags", ASCENDING)])

    print("✅ Database connection established and indexes created.")

except ConnectionFailure as e:
    print(f"❌ MongoDB connection error: {e}")
    # Create empty placeholder collections in case of connection failure
    # This allows the app to start, even if DB operations will fail
    class DummyCollection:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(f"Database connection failed. Operation {name} not executed.")
                return None if 'find' in name else 0
            return method

    class DummyDB:
        def __getattr__(self, name):
            return DummyCollection()

    db = DummyDB()
    users_collection = db.users
    posts_collection = db.posts
    interactions_collection = db.interactions
    user_profiles_collection = db.profiles

    print("⚠️ Using dummy database objects. The application will start but database operations will fail.")

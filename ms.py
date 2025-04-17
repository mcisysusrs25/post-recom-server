from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import certifi

# Replace with your actual URI
MONGO_URI = "mongodb+srv://sundarusa2025:hMgGGCXmr8F9zOBc@postrecds.foeyxiv.mongodb.net/?retryWrites=true&w=majority&appName=postrecds"

try:
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    client.admin.command('ping')  # Test the connection
    print("✅ Connection successful!")
except ConnectionFailure as e:
    print(f"❌ Could not connect to MongoDB: {e}")

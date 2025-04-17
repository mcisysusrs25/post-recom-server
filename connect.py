from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://sundarusa2025:hMgGGCXmr8F9zOBc@postrecds.foeyxiv.mongodb.net/?retryWrites=true&w=majority&appName=postrecds"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # Test database access
    db = client['postrecds']
    collection_names = db.list_collection_names()
    print(f"Collections in database: {collection_names}")
    
except Exception as e:
    print(f"Connection error: {e}")
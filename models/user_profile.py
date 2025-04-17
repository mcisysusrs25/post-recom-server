from pymongo import ASCENDING
from bson import ObjectId
from datetime import datetime
from mongo_helper import user_profiles_collection

# Define schema structure (for documentation purposes)
USER_PROFILE_SCHEMA = {
    "user": {
        "type": ObjectId,
        "ref": "User",
        "required": True,
        "unique": True  # This ensures one profile per user
    },
    "name": {
        "type": str,
        "required": True
    },
    "age": {
        "type": int,
        "min": 13,
        "max": 120
    },
    "feedPreferences": {
        "type": list,
        "default": []
    },
    "skills": {
        "type": list,
        "default": []
    },
    "occupation": {
        "type": str
    },
    "createdAt": {
        "type": datetime
    },
    "updatedAt": {
        "type": datetime
    }
}

# Create index on user field for faster lookups and to enforce uniqueness
user_profiles_collection.create_index([("user", ASCENDING)], unique=True)
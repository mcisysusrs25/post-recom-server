from pymongo import ASCENDING
from bson import ObjectId
from datetime import datetime
from mongo_helper import posts_collection

# Define schema structure (for documentation purposes)
POST_SCHEMA = {
    "user": {
        "type": ObjectId,
        "ref": "User",
        "required": True
    },
    "title": {
        "type": str,
        "required": True
    },
    "description": {
        "type": str,
        "required": True
    },
    "tags": {
        "type": list,
        "default": []
    },
    "likes": {
        "type": int,
        "default": 0
    },
    "views": {
        "type": int,
        "default": 0
    },
    "viewedBy": {
        "type": list,
        "default": []
    },
    "createdAt": {
        "type": datetime
    },
    "updatedAt": {
        "type": datetime
    }
}

# Create indexes for faster queries
posts_collection.create_index([("user", ASCENDING)])
posts_collection.create_index([("tags", ASCENDING)])
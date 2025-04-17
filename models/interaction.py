from pymongo import ASCENDING
from bson import ObjectId
from datetime import datetime
from mongo_helper import interactions_collection

# Define schema structure (for documentation purposes)
INTERACTION_SCHEMA = {
    "user": {
        "type": ObjectId,
        "ref": "User",
        "required": True
    },
    "post": {
        "type": ObjectId,
        "ref": "Post",
        "required": True
    },
    "interactionType": {
        "type": str,
        "enum": ["like", "view"],
        "required": True
    },
    "createdAt": {
        "type": datetime
    },
    "updatedAt": {
        "type": datetime
    }
}

# Create compound index for user-post pairs to prevent duplicates
interactions_collection.create_index(
    [("user", ASCENDING), ("post", ASCENDING), ("interactionType", ASCENDING)],
    unique=True
)
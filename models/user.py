from datetime import datetime
from mongo_helper import users_collection

# Define schema structure (for documentation purposes)
USER_SCHEMA = {
    "email": {
        "type": str,
        "required": True,
        "unique": True
    },
    "password": {
        "type": str,
        "required": True
    },
    "createdAt": {
        "type": datetime
    },
    "updatedAt": {
        "type": datetime
    }
}

# Create email index for uniqueness
users_collection.create_index("email", unique=True)
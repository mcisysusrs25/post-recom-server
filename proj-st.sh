#!/bin/bash

# Create Flask project structure mirroring the Node.js structure
echo "Creating Flask project structure..."

# Create main directories
mkdir -p controllers middleware models routes

# Create route files
touch routes/auth_routes.py
touch routes/post_routes.py
touch routes/profile_routes.py

# Create controller files
touch controllers/auth_controller.py
touch controllers/post_controller.py
touch controllers/profile_controller.py

# Create middleware files
touch middleware/auth.py

# Create model files
touch models/interaction.py
touch models/post.py
touch models/user.py
touch models/user_profile.py

# Create main app file
touch app.py

# Create environment and requirements files
touch .env
touch requirements.txt

echo "Project structure created successfully!"
echo "Install required packages with: pip install flask flask-cors python-dotenv pymongo flask-pymongo pyjwt bcrypt"
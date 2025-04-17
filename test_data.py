"""
Test data generator for post recommendation system.
This script creates test users, profiles, posts, and interactions
directly in MongoDB without going through the API.
"""

import random
import string
from datetime import datetime, timedelta
from bson import ObjectId
import bcrypt

# Import MongoDB collections
from mongo_helper import users_collection, posts_collection, interactions_collection, user_profiles_collection

# Sample data for test generation
SKILLS = [
    "Python", "JavaScript", "React", "Node.js", "MongoDB", "Flask", "Django",
    "Machine Learning", "Data Science", "DevOps", "AWS", "Docker", "UI/UX"
]

FEED_PREFERENCES = [
    "technology", "web development", "data science", "artificial intelligence",
    "cloud computing", "mobile development", "design", "career advice",
    "programming", "databases", "security", "tutorials", "startups"
]

POST_TAGS = [
    "python", "javascript", "react", "nodejs", "mongodb", "flask", "django",
    "machine-learning", "data-science", "devops", "aws", "docker", "ui-ux",
    "technology", "web-development", "artificial-intelligence", "cloud-computing", 
    "mobile-development", "design", "career-advice", "programming", "databases", 
    "security", "tutorials", "startups"
]

POST_TITLES = [
    "Getting Started with ReactJS",
    "Python Best Practices for Beginners",
    "MongoDB Schema Design Patterns",
    "Machine Learning Fundamentals",
    "Career Transition to Tech",
    "AWS Deployment Guide",
    "Building RESTful APIs with Flask",
    "Modern JavaScript Features",
    "Data Science Project Workflow",
    "Docker for Development Environments",
    "Node.js Performance Optimization",
    "Frontend Design Principles",
    "Database Security Basics",
    "DevOps Automation Techniques",
    "Mobile App Development with React Native"
]

OCCUPATIONS = [
    "Software Engineer", "Data Scientist", "Web Developer", "UX Designer",
    "Product Manager", "DevOps Engineer", "Student", "Teacher"
]

def generate_random_string(length=10):
    """Generate a random string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_random_date(start_date, end_date):
    """Get a random date between start_date and end_date"""
    time_delta = end_date - start_date
    days_delta = time_delta.total_seconds() / (24 * 3600)
    random_days = random.randint(0, int(days_delta))
    return start_date + timedelta(days=random_days)

def create_test_users(count=10):
    """Create test users"""
    users = []
    
    for i in range(count):
        email = f"testuser{i}@example.com"
        
        # Skip if user already exists
        if users_collection.find_one({"email": email}):
            print(f"User {email} already exists, skipping...")
            continue
        
        # Hash password
        password = "password123"
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        now = datetime.now()
        
        user = {
            "email": email,
            "password": hashed_password,
            "createdAt": now,
            "updatedAt": now
        }
        
        result = users_collection.insert_one(user)
        user_id = result.inserted_id
        user["_id"] = user_id
        users.append(user)
        
        print(f"Created user: {email} with ID: {user_id}")
        
    return users

def create_user_profiles(users):
    """Create user profiles for test users"""
    profiles = []
    
    for user in users:
        # Skip if profile already exists
        if user_profiles_collection.find_one({"user": user["_id"]}):
            print(f"Profile for user {user['email']} already exists, skipping...")
            continue
        
        # Generate random profile data
        name = f"Test User {user['email'].split('@')[0]}"
        num_skills = random.randint(2, 5)
        num_preferences = random.randint(2, 5)
        
        now = datetime.now()
        
        profile = {
            "user": user["_id"],
            "name": name,
            "age": random.randint(18, 50),
            "feedPreferences": random.sample(FEED_PREFERENCES, num_preferences),
            "skills": random.sample(SKILLS, num_skills),
            "occupation": random.choice(OCCUPATIONS),
            "createdAt": now,
            "updatedAt": now
        }
        
        result = user_profiles_collection.insert_one(profile)
        profile["_id"] = result.inserted_id
        profiles.append(profile)
        
        print(f"Created profile for user: {user['email']}")
        
    return profiles

def create_test_posts(users, count_per_user=5):
    """Create test posts for users"""
    posts = []
    
    # Date range for posts (past 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for user in users:
        for i in range(count_per_user):
            # Generate random post data
            title = f"{random.choice(POST_TITLES)} #{i+1}"
            description = (
                f"This is a test post about {random.choice(POST_TAGS)}. "
                f"It demonstrates the functionality of the recommendation system. "
                f"Created by {user['email']}."
            )
            
            # Select 2-5 random tags
            num_tags = random.randint(2, 5)
            tags = random.sample(POST_TAGS, num_tags)
            
            # Random creation date
            created_at = get_random_date(start_date, end_date)
            
            post = {
                "user": user["_id"],
                "title": title,
                "description": description,
                "tags": tags,
                "likes": 0,
                "views": 0,
                "viewedBy": [],
                "createdAt": created_at,
                "updatedAt": created_at
            }
            
            result = posts_collection.insert_one(post)
            post["_id"] = result.inserted_id
            posts.append(post)
            
            print(f"Created post: '{title}' with tags {tags}")
            
    return posts

def create_test_interactions(users, posts):
    """Create test interactions (likes and views)"""
    interactions = []
    
    for user in users:
        # Get posts by other users
        other_posts = [post for post in posts if post["user"] != user["_id"]]
        
        if not other_posts:
            continue
            
        # Randomly select posts to view (30-50% of other posts)
        view_count = max(1, int(len(other_posts) * random.uniform(0.3, 0.5)))
        posts_to_view = random.sample(other_posts, min(view_count, len(other_posts)))
        
        # Randomly select posts to like (40-70% of viewed posts)
        like_count = max(1, int(len(posts_to_view) * random.uniform(0.4, 0.7)))
        posts_to_like = random.sample(posts_to_view, min(like_count, len(posts_to_view)))
        
        now = datetime.now()
        
        # Create view interactions
        for post in posts_to_view:
            # Skip if interaction already exists
            existing = interactions_collection.find_one({
                "user": user["_id"],
                "post": post["_id"],
                "interactionType": "view"
            })
            
            if existing:
                print(f"View interaction already exists for user {user['email']} and post {post['title']}")
                continue
                
            interaction = {
                "user": user["_id"],
                "post": post["_id"],
                "interactionType": "view",
                "createdAt": now - timedelta(minutes=random.randint(1, 1000)),
                "updatedAt": now
            }
            
            try:
                result = interactions_collection.insert_one(interaction)
                
                # Update post view count
                posts_collection.update_one(
                    {"_id": post["_id"]},
                    {
                        "$inc": {"views": 1},
                        "$addToSet": {"viewedBy": user["_id"]}
                    }
                )
                
                print(f"Created view interaction: {user['email']} viewed '{post['title']}'")
                
            except Exception as e:
                print(f"Error creating view interaction: {e}")
                
        # Create like interactions
        for post in posts_to_like:
            # Skip if interaction already exists
            existing = interactions_collection.find_one({
                "user": user["_id"],
                "post": post["_id"],
                "interactionType": "like"
            })
            
            if existing:
                print(f"Like interaction already exists for user {user['email']} and post {post['title']}")
                continue
                
            interaction = {
                "user": user["_id"],
                "post": post["_id"],
                "interactionType": "like",
                "createdAt": now - timedelta(minutes=random.randint(1, 1000)),
                "updatedAt": now
            }
            
            try:
                result = interactions_collection.insert_one(interaction)
                
                # Update post like count
                posts_collection.update_one(
                    {"_id": post["_id"]},
                    {"$inc": {"likes": 1}}
                )
                
                print(f"Created like interaction: {user['email']} liked '{post['title']}'")
                
            except Exception as e:
                print(f"Error creating like interaction: {e}")

def create_specialized_test_cases():
    """Create specialized test cases to verify recommendation behavior"""
    
    # Get existing users
    all_users = list(users_collection.find())
    
    if len(all_users) < 3:
        print("Not enough users for specialized test cases")
        return
    
    # Create user groups with strong preferences
    # This will help us test if recommendations work as expected
    
    # User 1: Python & Data Science expert
    user1 = all_users[0]
    user_profiles_collection.update_one(
        {"user": user1["_id"]},
        {"$set": {
            "skills": ["Python", "Data Science", "Machine Learning", "Flask"],
            "feedPreferences": ["data science", "artificial intelligence", "tutorials"],
            "occupation": "Data Scientist"
        }}
    )
    print(f"Updated {user1['email']} to be a Python & Data Science expert")
    
    # Create Python & Data Science posts
    for i in range(3):
        title = f"Advanced Python for Data Science #{i+1}"
        description = "This post covers advanced techniques for data analysis using Python libraries."
        tags = ["python", "data-science", "machine-learning", "tutorials"]
        
        post = {
            "user": user1["_id"],
            "title": title,
            "description": description,
            "tags": tags,
            "likes": 0,
            "views": 0,
            "viewedBy": [],
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        posts_collection.insert_one(post)
        print(f"Created specialized post: '{title}'")
    
    # User 2: Web Development expert
    user2 = all_users[1]
    user_profiles_collection.update_one(
        {"user": user2["_id"]},
        {"$set": {
            "skills": ["JavaScript", "React", "Node.js", "UI/UX"],
            "feedPreferences": ["web development", "design", "programming"],
            "occupation": "Web Developer"
        }}
    )
    print(f"Updated {user2['email']} to be a Web Development expert")
    
    # Create Web Development posts
    for i in range(3):
        title = f"Modern Web Development Techniques #{i+1}"
        description = "This post explores the latest approaches to building responsive web applications."
        tags = ["javascript", "react", "nodejs", "web-development"]
        
        post = {
            "user": user2["_id"],
            "title": title,
            "description": description,
            "tags": tags,
            "likes": 0,
            "views": 0,
            "viewedBy": [],
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        posts_collection.insert_one(post)
        print(f"Created specialized post: '{title}'")
    
    # User 3: DevOps & Cloud expert
    user3 = all_users[2]
    user_profiles_collection.update_one(
        {"user": user3["_id"]},
        {"$set": {
            "skills": ["DevOps", "AWS", "Docker", "MongoDB"],
            "feedPreferences": ["cloud computing", "databases", "security"],
            "occupation": "DevOps Engineer"
        }}
    )
    print(f"Updated {user3['email']} to be a DevOps & Cloud expert")
    
    # Create DevOps & Cloud posts
    for i in range(3):
        title = f"Cloud Infrastructure Best Practices #{i+1}"
        description = "This post discusses optimal approaches to cloud architecture and deployment."
        tags = ["devops", "aws", "docker", "cloud-computing"]
        
        post = {
            "user": user3["_id"],
            "title": title,
            "description": description,
            "tags": tags,
            "likes": 0,
            "views": 0,
            "viewedBy": [],
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        posts_collection.insert_one(post)
        print(f"Created specialized post: '{title}'")
    
    # Create interactions between these specialized users and posts
    # This helps test the recommendation system's ability to match preferences
    
    # User 1 (Python expert) likes web dev posts
    web_posts = list(posts_collection.find({"tags": "web-development"}))
    for post in web_posts[:2]:  # Like first 2 web dev posts
        try:
            interactions_collection.insert_one({
                "user": user1["_id"],
                "post": post["_id"],
                "interactionType": "like",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            })
            
            # Update post like count
            posts_collection.update_one(
                {"_id": post["_id"]},
                {"$inc": {"likes": 1}}
            )
            
            print(f"Created specialized interaction: {user1['email']} liked '{post['title']}'")
        except Exception as e:
            print(f"Error creating specialized interaction: {e}")
    
    # User 2 (Web dev) likes DevOps posts
    devops_posts = list(posts_collection.find({"tags": "devops"}))
    for post in devops_posts[:2]:  # Like first 2 devops posts
        try:
            interactions_collection.insert_one({
                "user": user2["_id"],
                "post": post["_id"],
                "interactionType": "like",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            })
            
            # Update post like count
            posts_collection.update_one(
                {"_id": post["_id"]},
                {"$inc": {"likes": 1}}
            )
            
            print(f"Created specialized interaction: {user2['email']} liked '{post['title']}'")
        except Exception as e:
            print(f"Error creating specialized interaction: {e}")
    
    # User 3 (DevOps) likes Python posts
    python_posts = list(posts_collection.find({"tags": "python"}))
    for post in python_posts[:2]:  # Like first 2 python posts
        try:
            interactions_collection.insert_one({
                "user": user3["_id"],
                "post": post["_id"],
                "interactionType": "like",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            })
            
            # Update post like count
            posts_collection.update_one(
                {"_id": post["_id"]},
                {"$inc": {"likes": 1}}
            )
            
            print(f"Created specialized interaction: {user3['email']} liked '{post['title']}'")
        except Exception as e:
            print(f"Error creating specialized interaction: {e}")

def test_recommendation_system():
    """Test the recommendation system with a specific user"""
    from post_recommendation_system import get_recommended_posts
    
    # Get a test user
    user = users_collection.find_one()
    if not user:
        print("No users found for testing")
        return
    
    user_id = user["_id"]
    print(f"\nTesting recommendations for user: {user['email']}")
    print("User profile details:")
    
    profile = user_profiles_collection.find_one({"user": user_id})
    if profile:
        print(f"- Skills: {profile.get('skills', [])}")
        print(f"- Feed Preferences: {profile.get('feedPreferences', [])}")
        print(f"- Occupation: {profile.get('occupation', '')}")
    
    # Get user interactions
    likes = list(interactions_collection.find({"user": user_id, "interactionType": "like"}))
    views = list(interactions_collection.find({"user": user_id, "interactionType": "view"}))
    print(f"- Liked posts: {len(likes)}")
    print(f"- Viewed posts: {len(views)}")
    
    # Get recommendations
    recommended_post_ids = get_recommended_posts(user_id, limit=5)
    print(f"\nRecommended posts: {len(recommended_post_ids)}")
    
    # Get full post details
    for i, post_id in enumerate(recommended_post_ids):
        post = posts_collection.find_one({"_id": ObjectId(post_id)})
        if post:
            print(f"{i+1}. '{post['title']}' with tags: {post['tags']}")

def main():
    """Main function to generate test data"""
    try:
        print("Starting test data generation...")
        
        # Step 1: Create users
        print("\n=== Creating Test Users ===")
        users = create_test_users(10)
        
        # Step 2: Create user profiles
        print("\n=== Creating User Profiles ===")
        profiles = create_user_profiles(users)
        
        # Step 3: Create posts
        print("\n=== Creating Test Posts ===")
        posts = create_test_posts(users, 5)
        
        # Step 4: Create interactions
        print("\n=== Creating Test Interactions ===")
        create_test_interactions(users, posts)
        
        # Step 5: Create specialized test cases
        print("\n=== Creating Specialized Test Cases ===")
        create_specialized_test_cases()
        
        # Step 6: Test recommendation system
        print("\n=== Testing Recommendation System ===")
        test_recommendation_system()
        
        print("\nTest data generation complete!")
        
    except Exception as e:
        print(f"Error generating test data: {e}")

if __name__ == "__main__":
    main()
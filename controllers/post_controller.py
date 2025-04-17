from flask import jsonify
from bson import ObjectId
from mongo_helper import posts_collection, interactions_collection, users_collection
from post_recommendation_system import get_recommended_posts

def create_post(data, current_user):
    """Create a new post"""
    try:
        title = data.get('title')
        description = data.get('description')
        tags = data.get('tags', [])
        user_id = current_user['id']
        
        # Validation
        if not title or not description:
            return jsonify({"message": "Title and description are required"}), 400
        
        # Create new post
        new_post = {
            "user": ObjectId(user_id),
            "title": title,
            "description": description,
            "tags": tags or [],
            "likes": 0,
            "views": 0,
            "viewedBy": []
        }
        
        result = posts_collection.insert_one(new_post)
        
        # Get created post
        post = posts_collection.find_one({"_id": result.inserted_id})
        post['_id'] = str(post['_id'])
        post['user'] = str(post['user'])
        
        return jsonify(post), 201
        
    except Exception as error:
        print(f'Create post error: {error}')
        return jsonify({"message": "Server error"}), 500


def serialize_document(doc):
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, datetime):
                doc[key] = value.isoformat()
            elif isinstance(value, dict):
                doc[key] = serialize_document(value)
            elif isinstance(value, list):
                doc[key] = [serialize_document(item) if isinstance(item, dict) else str(item) if isinstance(item, ObjectId) else item for item in value]
    return doc


def get_all_posts(current_user):
    try:
        # 1. Get recommended post IDs for the current user
        from post_recommendation_system import get_recommended_posts
        recommended_post_ids = get_recommended_posts(current_user['id'], limit=10)
        
        # 2. Only get the recommended posts instead of all posts
        post_id_objects = [ObjectId(pid) for pid in recommended_post_ids]
        recommended_posts = []
        
        if post_id_objects:
            # Only fetch the recommended posts from the database
            recommended_posts = list(posts_collection.find({"_id": {"$in": post_id_objects}}))
            
            # Process these posts
            for post in recommended_posts:
                post['_id'] = str(post['_id'])
                post['user'] = str(post['user'])
                
                # Add position in recommendations as score (higher is better)
                post_id_str = str(post['_id'])
                position = recommended_post_ids.index(post_id_str)
                post['recommendation_score'] = len(recommended_post_ids) - position
                post['is_recommended'] = True
                
                # Convert viewedBy ObjectIds to strings
                if 'viewedBy' in post and post['viewedBy']:
                    post['viewedBy'] = [str(uid) for uid in post['viewedBy']]
        
        # 3. Sort by recommendation score
        recommended_posts.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return jsonify(recommended_posts)
    except Exception as error:
        print(f'Get posts error: {error}')
        return jsonify({"message": "Server error"}), 500

# def get_all_posts(current_user):
#     try:
#         # 1. Get recommended post IDs for the current user
#         from post_recommendation_system import get_recommended_posts
#         recommended_post_ids = get_recommended_posts(current_user['id'], limit=10)
        
#         # 2. Get all posts sorted by creation date
#         posts = list(posts_collection.find().sort("createdAt", -1))
        
#         # 3. Process posts (converting ObjectId and marking recommendations)
#         for post in posts:
#             post['_id'] = str(post['_id'])
#             post['user'] = str(post['user'])
            
#             # Check if post is in recommended list and assign a score
#             if post['_id'] in recommended_post_ids:
#                 # The position in the recommended list determines the score
#                 # Earlier items in the list have higher scores
#                 score = len(recommended_post_ids) - recommended_post_ids.index(post['_id'])
#                 post['recommendation_score'] = score
#                 post['is_recommended'] = True
#             else:
#                 post['recommendation_score'] = 0
#                 post['is_recommended'] = False
            
#             # Convert viewedBy ObjectIds to strings
#             if 'viewedBy' in post and post['viewedBy']:
#                 post['viewedBy'] = [str(uid) for uid in post['viewedBy']]
        
#         # 4. Sort posts by recommendation score
#         posts.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
#         return jsonify(posts)
#     except Exception as error:
#         print(f'Get posts error: {error}')
#         return jsonify({"message": "Server error"}), 500


# def get_all_posts(current_user):
#     try:
#         # 1. Get recommended post IDs for the current user
#         recommended_ids = get_recommended_posts(current_user['id'], limit=10)
        
#         # 2. Get all posts sorted by creation date (your original code)
#         posts = list(posts_collection.find().sort("createdAt", -1))
        
#         # 3. Process posts (converting ObjectId and marking recommendations)
#         for post in posts:
#             post['_id'] = str(post['_id'])
#             post['user'] = str(post['user'])
            
#             # Mark if post is recommended by the KNN algorithm
#             post['is_recommended'] = post['_id'] in recommended_ids
            
#             # Convert viewedBy ObjectIds to strings as in your original code
#             if 'viewedBy' in post and post['viewedBy']:
#                 post['viewedBy'] = [str(uid) for uid in post['viewedBy']]
        
#         posts.sort(key=lambda x: x['is_recommended'], reverse=True)
        
#         return jsonify(posts)
#     except Exception as error:
#         print(f'Get posts error: {error}')
#         return jsonify({"message": "Server error"}), 500
        

def get_posts_by_tag(tag, current_user):
    """Get posts by tag"""
    try:
        posts = list(posts_collection.find({"tags": tag}).sort("createdAt", -1))
        
        # Populate user data
        for post in posts:
            post['_id'] = str(post['_id'])
            user_id = post['user']
            user = users_collection.find_one({"_id": user_id}, {"email": 1})
            post['user'] = {"_id": str(user_id), "email": user['email']}
        
        return jsonify(posts)
        
    except Exception as error:
        print(f'Get posts by tag error: {error}')
        return jsonify({"message": "Server error"}), 500

# def get_post_by_id(post_id, current_user):
#     """Get post by ID"""
#     try:
#         # Validate post ID
#         try:
#             post_object_id = ObjectId(post_id)
#         except:
#             return jsonify({"message": "Invalid post ID"}), 400
        
#         post = posts_collection.find_one({"_id": post_object_id})
        
#         if not post:
#             return jsonify({"message": "Post not found"}), 404
        
#         # Populate user data
#         user_id = post['user']
#         user = users_collection.find_one({"_id": user_id}, {"email": 1})
        
#         post['_id'] = str(post['_id'])
#         post['user'] = {"_id": str(user_id), "email": user['email']}
        
#         return jsonify(post)
        
#     except Exception as error:
#         print(f'Get post error: {error}')
#         return jsonify({"message": "Server error"}), 500



def get_post_by_id(post_id, current_user):
    """Get post by ID"""
    try:
        # Validate post ID
        try:
            post_object_id = ObjectId(post_id)
        except:
            return jsonify({"message": "Invalid post ID"}), 400
        
        post = posts_collection.find_one({"_id": post_object_id})
        
        if not post:
            return jsonify({"message": "Post not found"}), 404
        
        # Populate user data
        user_id = post['user']
        user = users_collection.find_one({"_id": user_id}, {"email": 1})
        
        # Convert ObjectId to string
        post['_id'] = str(post['_id'])
        post['user'] = {"_id": str(user_id), "email": user['email']}
        
        # Handle nested ObjectId values if any
        if 'viewedBy' in post and post['viewedBy']:
            post['viewedBy'] = [str(uid) for uid in post['viewedBy']]
        
        return jsonify(post)
        
    except Exception as error:
        print(f'Get post error: {error}')
        return jsonify({"message": "Server error"}), 500



def get_user_posts(current_user):
    """Get posts by current user"""
    try:
        user_id = current_user['id']
        posts = list(posts_collection.find({"user": ObjectId(user_id)}).sort("createdAt", -1))
        
        # Convert ObjectIds to strings
        for post in posts:
            post['_id'] = str(post['_id'])
            post['user'] = str(post['user'])
        
        return jsonify(posts)
        
    except Exception as error:
        print(f'Get user posts error: {error}')
        return jsonify({"message": "Server error"}), 500

def update_post(post_id, data, current_user):
    """Update a post"""
    try:
        title = data.get('title')
        description = data.get('description')
        tags = data.get('tags')
        user_id = current_user['id']
        
        # Validate post ID
        try:
            post_object_id = ObjectId(post_id)
        except:
            return jsonify({"message": "Invalid post ID"}), 400
        
        # Find post
        post = posts_collection.find_one({"_id": post_object_id})
        
        # Check if post exists
        if not post:
            return jsonify({"message": "Post not found"}), 404
        
        # Check post ownership
        if str(post['user']) != user_id:
            return jsonify({"message": "Not authorized to update this post"}), 401
        
        # Update fields
        update_data = {}
        if title:
            update_data['title'] = title
        if description:
            update_data['description'] = description
        if tags:
            update_data['tags'] = tags
        
        # Save changes
        posts_collection.update_one(
            {"_id": post_object_id},
            {"$set": update_data}
        )
        
        # Get updated post
        updated_post = posts_collection.find_one({"_id": post_object_id})
        updated_post['_id'] = str(updated_post['_id'])
        updated_post['user'] = str(updated_post['user'])
        
        return jsonify(updated_post)
        
    except Exception as error:
        print(f'Update post error: {error}')
        return jsonify({"message": "Server error"}), 500

def delete_post(post_id, current_user):
    """Delete a post"""
    try:
        user_id = current_user['id']
        
        # Validate post ID
        try:
            post_object_id = ObjectId(post_id)
        except:
            return jsonify({"message": "Invalid post ID"}), 400
        
        # Find post
        post = posts_collection.find_one({"_id": post_object_id})
        
        # Check if post exists
        if not post:
            return jsonify({"message": "Post not found"}), 404
        
        # Check post ownership
        if str(post['user']) != user_id:
            return jsonify({"message": "Not authorized to delete this post"}), 401
        
        # Delete post
        posts_collection.delete_one({"_id": post_object_id})
        
        # Delete all interactions for this post
        interactions_collection.delete_many({"post": post_object_id})
        
        return jsonify({"message": "Post deleted successfully"})
        
    except Exception as error:
        print(f'Delete post error: {error}')
        return jsonify({"message": "Server error"}), 500

def like_post(post_id, current_user):
    """Like a post"""
    try:
        user_id = current_user['id']
        
        # Validate post ID
        try:
            post_object_id = ObjectId(post_id)
        except:
            return jsonify({"message": "Invalid post ID"}), 400
        
        # Find post
        post = posts_collection.find_one({"_id": post_object_id})
        
        # Check if post exists
        if not post:
            return jsonify({"message": "Post not found"}), 404
        
        # Check if already liked
        existing_like = interactions_collection.find_one({
            "user": ObjectId(user_id),
            "post": post_object_id,
            "interactionType": "like"
        })
        
        if existing_like:
            return jsonify({"message": "Post already liked"}), 400
        
        # Create interaction record
        new_interaction = {
            "user": ObjectId(user_id),
            "post": post_object_id,
            "interactionType": "like"
        }
        
        interactions_collection.insert_one(new_interaction)
        
        # Update like count
        posts_collection.update_one(
            {"_id": post_object_id},
            {"$inc": {"likes": 1}}
        )
        
        # Get updated likes count
        updated_post = posts_collection.find_one({"_id": post_object_id})
        
        return jsonify({"likes": updated_post.get("likes", 0)})
        
    except Exception as error:
        print(f'Like post error: {error}')
        return jsonify({"message": "Server error"}), 500

def unlike_post(post_id, current_user):
    """Unlike a post"""
    try:
        user_id = current_user['id']
        
        # Validate post ID
        try:
            post_object_id = ObjectId(post_id)
        except:
            return jsonify({"message": "Invalid post ID"}), 400
        
        # Find post
        post = posts_collection.find_one({"_id": post_object_id})
        
        # Check if post exists
        if not post:
            return jsonify({"message": "Post not found"}), 404
        
        # Check if liked
        existing_like = interactions_collection.find_one({
            "user": ObjectId(user_id),
            "post": post_object_id,
            "interactionType": "like"
        })
        
        if not existing_like:
            return jsonify({"message": "Post not liked yet"}), 400
        
        # Remove interaction record
        interactions_collection.delete_one({
            "user": ObjectId(user_id),
            "post": post_object_id,
            "interactionType": "like"
        })
        
        # Update like count (ensure it doesn't go below 0)
        current_likes = post.get("likes", 0)
        new_likes = max(0, current_likes - 1)
        
        posts_collection.update_one(
            {"_id": post_object_id},
            {"$set": {"likes": new_likes}}
        )
        
        return jsonify({"likes": new_likes})
        
    except Exception as error:
        print(f'Unlike post error: {error}')
        return jsonify({"message": "Server error"}), 500

def view_post(post_id, current_user):
    """View a post"""
    try:
        user_id = current_user['id']
        
        # Validate post ID
        try:
            post_object_id = ObjectId(post_id)
        except:
            return jsonify({"message": "Invalid post ID"}), 400
        
        # Find post
        post = posts_collection.find_one({"_id": post_object_id})
        
        # Check if post exists
        if not post:
            return jsonify({"message": "Post not found"}), 404
        
        # Check if already viewed
        viewed_by = post.get("viewedBy", [])
        already_viewed = False
        
        for viewer_id in viewed_by:
            if str(viewer_id) == user_id:
                already_viewed = True
                break
        
        if not already_viewed:
            # Create interaction record
            new_interaction = {
                "user": ObjectId(user_id),
                "post": post_object_id,
                "interactionType": "view"
            }
            
            interactions_collection.insert_one(new_interaction)
            
            # Update view count and viewedBy array
            posts_collection.update_one(
                {"_id": post_object_id},
                {
                    "$inc": {"views": 1},
                    "$push": {"viewedBy": ObjectId(user_id)}
                }
            )
        
        # Get full post data
        updated_post = posts_collection.find_one({"_id": post_object_id})
        user_obj = users_collection.find_one({"_id": updated_post["user"]}, {"email": 1})
        
        # Format response
        updated_post["_id"] = str(updated_post["_id"])
        updated_post["user"] = {"_id": str(updated_post["user"]), "email": user_obj["email"]}
        
        # Convert viewedBy array of ObjectIds to strings
        if "viewedBy" in updated_post:
            updated_post["viewedBy"] = [str(viewer_id) for viewer_id in updated_post["viewedBy"]]
        
        return jsonify(updated_post)
        
    except Exception as error:
        print(f'View post error: {error}')
        return jsonify({"message": "Server error"}), 500
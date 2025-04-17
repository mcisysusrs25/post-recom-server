"""
KNN-based post recommendation system that balances user skills and preferences
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
from bson import ObjectId
import re

# Import MongoDB collections
from mongo_helper import posts_collection, interactions_collection, user_profiles_collection

def normalize_tag(tag):
    """Normalize a tag by removing special characters and converting to lowercase"""
    if not tag:
        return ""
    # Replace special characters with spaces and convert to lowercase
    normalized = re.sub(r'[_\-/\s+]', '', tag.lower())
    return normalized

def get_recommended_posts(user_id, limit=10):
    """
    Generate balanced post recommendations based on user skills and preferences
    
    Args:
        user_id: User ID to generate recommendations for (string or ObjectId)
        limit: Number of posts to recommend
        
    Returns:
        List of recommended post IDs as strings
    """
    user_id_obj = ObjectId(user_id) if isinstance(user_id, str) else user_id
    
    # 1. Get user profile and interactions
    user_profile = user_profiles_collection.find_one({"user": user_id_obj})
    user_interactions = list(interactions_collection.find({"user": user_id_obj}))
    
    # If no user profile, return empty list
    if not user_profile:
        return []
    
    # 2. Extract user skills and preferences
    skills = [normalize_tag(skill) for skill in user_profile.get('skills', [])]
    preferences = [normalize_tag(pref) for pref in user_profile.get('feedPreferences', [])]
    
    # 3. Get posts the user has already viewed
    viewed_post_ids = {i['post'] for i in user_interactions if i['interactionType'] == 'view'}
    
    # 4. Get all posts except user's own posts and those already viewed
    candidate_posts = list(posts_collection.find({
        "user": {"$ne": user_id_obj},
        "_id": {"$nin": list(viewed_post_ids)}
    }))
    
    # If no candidate posts, return empty list
    if not candidate_posts:
        return []
    
    # 5. Calculate direct tag matches for each post
    post_scores = []
    for post in candidate_posts:
        post_id = post['_id']
        post_tags = [normalize_tag(tag) for tag in post.get('tags', [])]
        
        # Count matches with skills and preferences
        skill_matches = sum(1 for skill in skills if any(skill in tag or tag in skill for tag in post_tags))
        pref_matches = sum(1 for pref in preferences if any(pref in tag or tag in pref for tag in post_tags))
        
        # Calculate a direct matching score (higher is better)
        direct_score = (skill_matches * 5) + (pref_matches * 5)
        
        # Also check for interaction history (likes)
        interaction_score = 0
        for interaction in user_interactions:
            if interaction['post'] == post_id and interaction['interactionType'] == 'like':
                # Get tags from this liked post to compare with current post
                liked_post = posts_collection.find_one({"_id": interaction['post']})
                if liked_post:
                    liked_tags = [normalize_tag(tag) for tag in liked_post.get('tags', [])]
                    # Count matching tags between liked post and current post
                    tag_matches = sum(1 for tag in post_tags if tag in liked_tags)
                    interaction_score += tag_matches * 3
        
        # Combine scores
        total_score = direct_score + interaction_score
        
        post_scores.append({
            'id': post_id,
            'score': total_score,
            'skill_matches': skill_matches,
            'pref_matches': pref_matches,
            'tags': post.get('tags', []),
            'title': post.get('title', '')
        })
    
    # 6. Sort posts by score (highest first)
    post_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # 7. Ensure we have a balanced mix of recommendations
    final_recommendations = []
    skill_related = []
    pref_related = []
    
    # Separate posts into skill-related and preference-related
    for post in post_scores:
        if post['skill_matches'] > 0:
            skill_related.append(post)
        if post['pref_matches'] > 0:
            pref_related.append(post)
    
    # If user has both skills and preferences, ensure both are represented
    if skills and preferences and skill_related and pref_related:
        # Fill half with skill-related, half with preference-related
        skill_count = min(limit // 2, len(skill_related))
        pref_count = min(limit - skill_count, len(pref_related))
        
        # Add skill-related posts
        for i in range(skill_count):
            if skill_related[i]['id'] not in [p['id'] for p in final_recommendations]:
                final_recommendations.append(skill_related[i])
        
        # Add preference-related posts
        for i in range(pref_count):
            if pref_related[i]['id'] not in [p['id'] for p in final_recommendations]:
                final_recommendations.append(pref_related[i])
    
    # If we still need more recommendations, add from the remaining top-scored posts
    remaining_count = limit - len(final_recommendations)
    if remaining_count > 0:
        for post in post_scores:
            if post['id'] not in [p['id'] for p in final_recommendations]:
                final_recommendations.append(post)
                remaining_count -= 1
                if remaining_count == 0:
                    break
    
    # 8. Sort final recommendations by score again
    final_recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    # 9. Extract post IDs for return
    recommended_post_ids = [str(post['id']) for post in final_recommendations[:limit]]
    
    # Print debug info
    print(f"\nUser skills: {user_profile.get('skills', [])}")
    print(f"User preferences: {user_profile.get('feedPreferences', [])}")
    print("\nRecommended posts:")
    for post in final_recommendations[:limit]:
        print(f"- '{post['title']}' (Tags: {post['tags']}, Score: {post['score']})")
        print(f"  Skill matches: {post['skill_matches']}, Preference matches: {post['pref_matches']}")
    
    return recommended_post_ids
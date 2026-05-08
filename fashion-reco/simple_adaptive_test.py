#!/usr/bin/env python3
"""
🧪 SIMPLE ADAPTIVE TEST: Check if scores change after feedback
Run this AFTER starting the server with: python adaptive_api.py
"""

import requests

BASE_URL = "http://localhost:8004"
USER_ID = "test_user_simple"

def simple_test():
    """Simple test to check if adaptive algorithm works."""
    
    print("🧪 TESTING ADAPTIVE ALGORITHM")
    print("=" * 40)
    
    request_data = {
        "user_id": USER_ID,
        "quiz_features": {
            "size": "M",
            "preferred_categories": ["shoes"],
            "preferred_colors": ["white"],
            "max_price": 100,
            "preferred_brands": ["nike"],
            "preferred_styles": ["casual"]
        },
        "adaptation_strength": 0.5,
        "k": 5
    }
    
    # Step 1: Get initial recommendations
    print("\n1️⃣ INITIAL RECOMMENDATIONS:")
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json=request_data)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return
    
    initial_recs = response.json()
    print("Before feedback:")
    for i, item in enumerate(initial_recs[:3], 1):
        print(f"   {i}. {item['title']} (ID: {item['id']}) - Score: {item.get('score', 0):.4f}")
    
    # Step 2: Give feedback
    print("\n2️⃣ GIVING FEEDBACK:")
    
    # Like Nike shoes
    feedback_response = requests.post(f"{BASE_URL}/feedback", json={
        "user_id": USER_ID,
        "item_id": "item_003",  # Nike shoes
        "feedback": "like"
    })
    print(f"👍 Liked Nike shoes: {feedback_response.status_code}")
    
    # Dislike hoodie
    feedback_response = requests.post(f"{BASE_URL}/feedback", json={
        "user_id": USER_ID,
        "item_id": "item_004",  # Hoodie
        "feedback": "dislike"
    })
    print(f"👎 Disliked hoodie: {feedback_response.status_code}")
    
    # Step 3: Get adapted recommendations
    print("\n3️⃣ ADAPTED RECOMMENDATIONS:")
    request_data["adaptation_strength"] = 0.8  # Higher adaptation
    
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json=request_data)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return
    
    adapted_recs = response.json()
    print("After feedback:")
    
    # Compare scores
    for i, item in enumerate(adapted_recs[:3], 1):
        item_id = item['id']
        new_score = item.get('score', 0)
        
        # Find old score
        old_score = 0
        for old_item in initial_recs:
            if old_item['id'] == item_id:
                old_score = old_item.get('score', 0)
                break
        
        change = new_score - old_score
        change_icon = "🟢" if change > 0.01 else "🔴" if change < -0.01 else "🟡"
        
        print(f"   {i}. {item['title']} (ID: {item_id})")
        print(f"      Before: {old_score:.4f}")
        print(f"      After:  {new_score:.4f}")
        print(f"      Change: {change:+.4f} {change_icon}")
        
        if item.get('user_feedback'):
            feedback_info = item['user_feedback']
            emoji = "👍" if feedback_info['feedback'] == 'like' else "👎"
            print(f"      Feedback: {emoji} {feedback_info['feedback']}")
    
    # Check user stats
    print("\n4️⃣ USER STATS:")
    stats_response = requests.get(f"{BASE_URL}/users/{USER_ID}/stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"👍 Likes: {stats.get('likes', 0)}")
        print(f"👎 Dislikes: {stats.get('dislikes', 0)}")
        print(f"🧠 Preference strength: {stats.get('preference_strength', 0):.3f}")
    
    print("\n🏁 Test complete!")
    print("💡 If scores changed, the adaptive algorithm is working!")

if __name__ == "__main__":
    try:
        simple_test()
    except requests.exceptions.ConnectionError:
        print("❌ Server not running!")
        print("💡 Start server with: python adaptive_api.py")
    except Exception as e:
        print(f"❌ Error: {e}")
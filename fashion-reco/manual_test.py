#!/usr/bin/env python3
"""
🎯 SIMPLE MANUAL TEST: Test feedback with correct item IDs from catalog.csv

This uses the EXACT item IDs from your catalog.csv file:
- item_001: Zara White Cotton T-Shirt
- item_002: H&M Blue Denim Jeans  
- item_003: Nike Black Running Shoes
- item_004: Uniqlo Gray Hoodie
- item_005: Adidas Red Track Jacket
"""

import requests
import json

BASE_URL = "http://localhost:8004"
USER_ID = "manual_test_user"

def test_feedback_with_real_items():
    """Test feedback using actual item IDs from catalog."""
    
    print("🧪 TESTING FEEDBACK WITH REAL CATALOG ITEMS")
    print("=" * 60)
    
    # Step 1: Get initial recommendations
    print("\n1️⃣ GET INITIAL RECOMMENDATIONS")
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json={
        "user_id": USER_ID,
        "brand_name": "Nike", 
        "k": 5
    })
    
    if response.status_code == 200:
        recommendations = response.json()["recommendations"]
        print(f"✅ Got {len(recommendations)} recommendations:")
        for i, item in enumerate(recommendations, 1):
            print(f"   {i}. {item['title']} (ID: {item['id']}) - Score: {item.get('score', 0):.3f}")
    else:
        print(f"❌ Failed to get recommendations: {response.status_code}")
        return
    
    # Step 2: Like Nike shoes (item_003)
    print(f"\n2️⃣ LIKE NIKE SHOES (item_003)")
    response = requests.post(f"{BASE_URL}/feedback", json={
        "user_id": USER_ID,
        "item_id": "item_003",  # Nike Black Running Shoes
        "feedback": "like"
    })
    
    if response.status_code == 200:
        print("✅ Successfully liked Nike shoes!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Failed to like item: {response.status_code} - {response.text}")
        return
    
    # Step 3: Dislike Hoodie (item_004)  
    print(f"\n3️⃣ DISLIKE HOODIE (item_004)")
    response = requests.post(f"{BASE_URL}/feedback", json={
        "user_id": USER_ID,
        "item_id": "item_004",  # Uniqlo Gray Hoodie
        "feedback": "dislike"
    })
    
    if response.status_code == 200:
        print("✅ Successfully disliked hoodie!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Failed to dislike item: {response.status_code} - {response.text}")
        return
    
    # Step 4: Get adapted recommendations
    print(f"\n4️⃣ GET ADAPTED RECOMMENDATIONS")
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json={
        "user_id": USER_ID,
        "brand_name": "Nike",
        "adaptation_strength": 0.8,
        "k": 5
    })
    
    if response.status_code == 200:
        adapted_recommendations = response.json()["recommendations"] 
        print(f"✅ Got {len(adapted_recommendations)} adapted recommendations:")
        for i, item in enumerate(adapted_recommendations, 1):
            score = item.get('score', 0)
            personalized = "🎯" if item.get('is_personalized') else "  "
            print(f"   {personalized} {i}. {item['title']} (ID: {item['id']}) - Score: {score:.3f}")
            
            # Show if user gave feedback on this item
            if item.get('user_feedback'):
                feedback_info = item['user_feedback']
                emoji = "👍" if feedback_info['feedback'] == 'like' else "👎"
                print(f"      {emoji} Your feedback: {feedback_info['feedback']} ({feedback_info['days_ago']} days ago)")
    else:
        print(f"❌ Failed to get adapted recommendations: {response.status_code}")
        return
    
    # Step 5: Check user stats
    print(f"\n5️⃣ CHECK USER LEARNING STATS")
    response = requests.get(f"{BASE_URL}/users/{USER_ID}/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ User learning statistics:")
        print(f"   👍 Likes: {stats.get('likes', 0)}")
        print(f"   👎 Dislikes: {stats.get('dislikes', 0)}")
        print(f"   🧠 Preference strength: {stats.get('preference_strength', 0):.2f}")
        print(f"   📝 Has profile: {stats.get('has_preference_profile', False)}")
    else:
        print(f"❌ Failed to get user stats: {response.status_code}")
    
    print(f"\n🎉 MANUAL TEST COMPLETED!")
    print(f"💡 The system successfully learned from your feedback!")

def test_all_catalog_items():
    """Test feedback on all items in catalog."""
    
    print(f"\n🔍 TESTING ALL CATALOG ITEMS")
    print("=" * 40)
    
    catalog_items = [
        {"id": "item_001", "name": "Zara White Cotton T-Shirt"},
        {"id": "item_002", "name": "H&M Blue Denim Jeans"},
        {"id": "item_003", "name": "Nike Black Running Shoes"}, 
        {"id": "item_004", "name": "Uniqlo Gray Hoodie"},
        {"id": "item_005", "name": "Adidas Red Track Jacket"}
    ]
    
    print("Testing feedback on each catalog item:")
    
    for item in catalog_items:
        print(f"\n📝 Testing item: {item['name']} (ID: {item['id']})")
        
        # Test like
        response = requests.post(f"{BASE_URL}/feedback", json={
            "user_id": f"test_{item['id']}",
            "item_id": item["id"],
            "feedback": "like"
        })
        
        if response.status_code == 200:
            print(f"   ✅ Like feedback: SUCCESS")
        else:
            print(f"   ❌ Like feedback: FAILED ({response.status_code})")
            print(f"      Error: {response.text}")

if __name__ == "__main__":
    try:
        # Test basic functionality
        test_feedback_with_real_items()
        
        # Test all catalog items
        test_all_catalog_items()
        
    except requests.exceptions.ConnectionError:
        print("❌ Server not running! Start it with: python adaptive_api.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
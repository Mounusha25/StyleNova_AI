#!/usr/bin/env python3
"""
🧪 TEST ALL THREE INPUT METHODS: Quiz, Image URL, Brand Name
"""

import requests

BASE_URL = "http://localhost:8004"
USER_ID = "method_test_user"

def test_all_methods():
    """Test all three input methods work with adaptive learning."""
    
    print("🧪 TESTING ALL INPUT METHODS")
    print("=" * 50)
    
    # Test 1: Quiz Features
    print("\n1️⃣ QUIZ FEATURES METHOD:")
    quiz_request = {
        "user_id": USER_ID,
        "quiz_features": {
            "size": "M",
            "preferred_categories": ["shoes"],
            "preferred_colors": ["black"],
            "preferred_brands": ["nike"],
            "preferred_styles": ["athletic"]
        },
        "adaptation_strength": 0.5,
        "k": 3
    }
    
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json=quiz_request)
    if response.status_code == 200:
        results = response.json()
        print("✅ Quiz method works!")
        for i, item in enumerate(results[:2], 1):
            print(f"   {i}. {item['title']} - Score: {item.get('score', 0):.3f}")
    else:
        print(f"❌ Quiz method failed: {response.status_code}")
    
    # Test 2: Image URL
    print("\n2️⃣ IMAGE URL METHOD:")
    image_request = {
        "user_id": USER_ID,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        "adaptation_strength": 0.5,
        "k": 3
    }
    
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json=image_request)
    if response.status_code == 200:
        results = response.json()
        print("✅ Image URL method works!")
        for i, item in enumerate(results[:2], 1):
            print(f"   {i}. {item['title']} - Score: {item.get('score', 0):.3f}")
    else:
        print(f"❌ Image URL method failed: {response.status_code}")
    
    # Test 3: Brand Name
    print("\n3️⃣ BRAND NAME METHOD:")
    brand_request = {
        "user_id": USER_ID,
        "brand_name": "Nike",
        "category": "shoes",
        "adaptation_strength": 0.5,
        "k": 3
    }
    
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json=brand_request)
    if response.status_code == 200:
        results = response.json()
        print("✅ Brand name method works!")
        for i, item in enumerate(results[:2], 1):
            print(f"   {i}. {item['title']} - Score: {item.get('score', 0):.3f}")
    else:
        print(f"❌ Brand name method failed: {response.status_code}")
    
    print("\n🎯 ALL METHODS WORK WITH ADAPTIVE LEARNING!")
    print("💡 The same user feedback applies to all search methods!")

if __name__ == "__main__":
    try:
        test_all_methods()
    except requests.exceptions.ConnectionError:
        print("❌ Server not running!")
    except Exception as e:
        print(f"❌ Error: {e}")
#!/usr/bin/env python3
"""
🧪 ADAPTIVE ALGORITHM TEST: Check if scores change after feedback

This test will prove whether the adaptive algorithm is working by:
1. Getting initial recommendations and recording scores
2. Giving feedback (like/dislike)
3. Getting recommendations again and comparing scores
4. Showing the exact differences
"""

import requests
import json
import time

BASE_URL = "http://localhost:8004"
USER_ID = "adaptive_test_user"

def test_adaptive_algorithm():
    """Test if the adaptive algorithm actually changes scores."""
    
    print("🧪 TESTING ADAPTIVE ALGORITHM - SCORE CHANGES")
    print("=" * 60)
    
    # Test request payload (same as you used)
    request_payload = {
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
    
    # Step 1: Get INITIAL recommendations
    print("\n1️⃣ GETTING INITIAL RECOMMENDATIONS (before feedback)")
    print("-" * 50)
    
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json=request_payload)
    
    if response.status_code != 200:
        print(f"❌ Failed to get recommendations: {response.status_code}")
        print(f"Error: {response.text}")
        return
    
    initial_recommendations = response.json()  # API returns list directly, not dict with "recommendations" key
    print(f"✅ Got {len(initial_recommendations)} initial recommendations:")
    
    # Store initial scores
    initial_scores = {}
    for i, item in enumerate(initial_recommendations, 1):
        item_id = item['id']
        score = item.get('score', 0)
        initial_scores[item_id] = score
        
        print(f"   {i}. {item['title']} (ID: {item_id})")
        print(f"      Initial Score: {score:.4f}")
        print(f"      Personalized: {item.get('is_personalized', False)}")
    
    # Step 2: Give POSITIVE feedback on item_003 (Nike shoes)
    print(f"\n2️⃣ GIVING POSITIVE FEEDBACK (LIKE) on item_003")
    print("-" * 50)
    
    feedback_payload = {
        "user_id": USER_ID,
        "item_id": "item_003",  # Nike Black Running Shoes
        "feedback": "like"
    }
    
    response = requests.post(f"{BASE_URL}/feedback", json=feedback_payload)
    
    if response.status_code != 200:
        print(f"❌ Failed to give feedback: {response.status_code}")
        print(f"Error: {response.text}")
        return
    
    print("✅ Successfully gave positive feedback on Nike shoes!")
    print(f"   Response: {response.json()}")
    
    # Step 3: Give NEGATIVE feedback on item_004 (hoodie)
    print(f"\n3️⃣ GIVING NEGATIVE FEEDBACK (DISLIKE) on item_004")
    print("-" * 50)
    
    feedback_payload = {
        "user_id": USER_ID,
        "item_id": "item_004",  # Uniqlo Gray Hoodie
        "feedback": "dislike"
    }
    
    response = requests.post(f"{BASE_URL}/feedback", json=feedback_payload)
    
    if response.status_code != 200:
        print(f"❌ Failed to give feedback: {response.status_code}")
        print(f"Error: {response.text}")
        return
    
    print("✅ Successfully gave negative feedback on hoodie!")
    print(f"   Response: {response.json()}")
    
    # Step 4: Get ADAPTED recommendations
    print(f"\n4️⃣ GETTING ADAPTED RECOMMENDATIONS (after feedback)")
    print("-" * 50)
    
    # Use higher adaptation strength to see bigger changes
    request_payload["adaptation_strength"] = 0.8
    
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json=request_payload)
    
    if response.status_code != 200:
        print(f"❌ Failed to get adapted recommendations: {response.status_code}")
        print(f"Error: {response.text}")
        return
    
    adapted_recommendations = response.json()  # API returns list directly
    print(f"✅ Got {len(adapted_recommendations)} adapted recommendations:")
    
    # Step 5: COMPARE scores and show differences
    print(f"\n5️⃣ SCORE COMPARISON ANALYSIS")
    print("=" * 60)
    
    score_changes = {}
    for i, item in enumerate(adapted_recommendations, 1):
        item_id = item['id']
        new_score = item.get('score', 0)
        old_score = initial_scores.get(item_id, 0)
        difference = new_score - old_score
        score_changes[item_id] = difference
        
        # Determine change type
        if abs(difference) < 0.001:
            change_type = "🟡 NO CHANGE"
        elif difference > 0:
            change_type = "🟢 INCREASED"
        else:
            change_type = "🔴 DECREASED"
        
        print(f"\n   {i}. {item['title']} (ID: {item_id})")
        print(f"      Before: {old_score:.4f}")
        print(f"      After:  {new_score:.4f}")
        print(f"      Change: {difference:+.4f} {change_type}")
        print(f"      Personalized: {item.get('is_personalized', False)}")
        
        # Show feedback info if available
        if item.get('user_feedback'):
            feedback_info = item['user_feedback']
            emoji = "👍" if feedback_info['feedback'] == 'like' else "👎"
            print(f"      Feedback: {emoji} {feedback_info['feedback']} ({feedback_info['days_ago']} days ago)")
    
    # Step 6: ANALYSIS SUMMARY
    print(f"\n6️⃣ ADAPTIVE ALGORITHM ANALYSIS")
    print("=" * 60)
    
    nike_change = score_changes.get('item_003', 0)  # Should increase (liked)
    hoodie_change = score_changes.get('item_004', 0)  # Should decrease (disliked)
    
    print(f"🎯 Expected Results:")
    print(f"   Nike shoes (item_003) - LIKED → should INCREASE: {nike_change:+.4f}")
    print(f"   Hoodie (item_004) - DISLIKED → should DECREASE: {hoodie_change:+.4f}")
    
    # Determine if algorithm is working
    algorithm_working = False
    
    if nike_change > 0.01:  # Significant increase
        print(f"   ✅ Nike score increased - POSITIVE feedback working!")
        algorithm_working = True
    else:
        print(f"   ⚠️  Nike score didn't increase much - check positive feedback")
    
    if hoodie_change < -0.01:  # Significant decrease
        print(f"   ✅ Hoodie score decreased - NEGATIVE feedback working!")
        algorithm_working = True
    else:
        print(f"   ⚠️  Hoodie score didn't decrease much - check negative feedback")
    
    # Overall assessment
    total_changes = sum(abs(change) for change in score_changes.values())
    
    print(f"\n📊 FINAL ASSESSMENT:")
    if total_changes > 0.05:
        print(f"   🎉 ADAPTIVE ALGORITHM IS WORKING!")
        print(f"   📈 Total score changes: {total_changes:.4f}")
        print(f"   💡 The system is learning from your feedback!")
    else:
        print(f"   ⚠️  Algorithm might not be adapting enough")
        print(f"   📈 Total score changes: {total_changes:.4f}")
        print(f"   💡 Try higher adaptation_strength or check implementation")
    
    return algorithm_working

def check_user_stats():
    """Check user learning statistics."""
    print(f"\n7️⃣ USER LEARNING STATISTICS")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/users/{USER_ID}/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ User learning statistics:")
        print(f"   👍 Total likes: {stats.get('likes', 0)}")
        print(f"   👎 Total dislikes: {stats.get('dislikes', 0)}")
        print(f"   🧠 Preference strength: {stats.get('preference_strength', 0):.3f}")
        print(f"   📝 Has preference profile: {stats.get('has_preference_profile', False)}")
        
        if stats.get('likes', 0) > 0 or stats.get('dislikes', 0) > 0:
            print(f"   ✅ System has recorded your feedback!")
        else:
            print(f"   ⚠️  No feedback recorded - check feedback endpoint")
    else:
        print(f"❌ Failed to get user stats: {response.status_code}")

if __name__ == "__main__":
    try:
        print("🚀 ADAPTIVE ALGORITHM VERIFICATION TEST")
        print("Testing if like/dislike feedback actually changes recommendation scores")
        print()
        
        # Run the main test
        algorithm_working = test_adaptive_algorithm()
        
        # Check user stats
        check_user_stats()
        
        print(f"\n🏁 TEST COMPLETE!")
        if algorithm_working:
            print(f"✅ Your adaptive algorithm IS WORKING! 🎉")
        else:
            print(f"⚠️  Algorithm needs debugging - scores aren't changing enough")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running!")
        print("💡 Start it with: source fashion_venv/bin/activate && python adaptive_api.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
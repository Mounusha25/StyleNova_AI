#!/usr/bin/env python3
"""
🔬 ADAPTIVE ALGORITHM VERIFICATION TEST

This test specifically checks if the algorithm is truly adaptive by:
1. Getting baseline scores
2. Adding feedback 
3. Checking if scores actually change
4. Showing the mathematical difference
"""

import requests
import json
import time

BASE_URL = "http://localhost:8004"

def test_adaptive_algorithm():
    """Test if the adaptive algorithm actually changes scores."""
    
    print("🔬 TESTING IF ALGORITHM IS TRULY ADAPTIVE")
    print("=" * 60)
    
    # Use consistent user ID
    user_id = "adaptive_test_user"
    
    # Step 1: Get baseline recommendations (before any feedback)
    print("1️⃣ GETTING BASELINE RECOMMENDATIONS (Before Feedback)")
    print("-" * 50)
    
    baseline_request = {
        "user_id": user_id,
        "brand_name": "Nike",
        "adaptation_strength": 0.8,  # High adaptation to see clear changes
        "k": 5
    }
    
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json=baseline_request)
    
    if response.status_code != 200:
        print(f"❌ Failed to get baseline: {response.status_code}")
        print(f"Error: {response.text}")
        return False
    
    baseline_results = response.json()["recommendations"]
    print(f"✅ Got {len(baseline_results)} baseline recommendations:")
    
    baseline_scores = {}
    for i, item in enumerate(baseline_results, 1):
        item_id = item['id']
        score = item.get('score', 0)
        baseline_scores[item_id] = score
        print(f"   {i}. {item['title']} (ID: {item_id})")
        print(f"      Baseline Score: {score:.4f}")
    
    # Step 2: Give positive feedback on Nike item
    print(f"\n2️⃣ GIVING POSITIVE FEEDBACK")
    print("-" * 30)
    
    # Find a Nike item to like
    nike_item_id = "item_003"  # Nike Black Running Shoes from catalog
    print(f"👍 Liking Nike item: {nike_item_id}")
    
    feedback_response = requests.post(f"{BASE_URL}/feedback", json={
        "user_id": user_id,
        "item_id": nike_item_id,
        "feedback": "like"
    })
    
    if feedback_response.status_code != 200:
        print(f"❌ Failed to give feedback: {feedback_response.status_code}")
        print(f"Error: {feedback_response.text}")
        return False
    
    print("✅ Positive feedback recorded!")
    
    # Step 3: Give negative feedback on non-Nike item
    print(f"\n3️⃣ GIVING NEGATIVE FEEDBACK")
    print("-" * 30)
    
    non_nike_item_id = "item_004"  # Uniqlo Gray Hoodie
    print(f"👎 Disliking non-athletic item: {non_nike_item_id}")
    
    feedback_response = requests.post(f"{BASE_URL}/feedback", json={
        "user_id": user_id,
        "item_id": non_nike_item_id,
        "feedback": "dislike"
    })
    
    if feedback_response.status_code != 200:
        print(f"❌ Failed to give negative feedback: {feedback_response.status_code}")
        return False
    
    print("✅ Negative feedback recorded!")
    
    # Small delay to ensure feedback is processed
    time.sleep(1)
    
    # Step 4: Get adapted recommendations (after feedback)
    print(f"\n4️⃣ GETTING ADAPTED RECOMMENDATIONS (After Feedback)")
    print("-" * 50)
    
    # Use EXACT same request as baseline
    response = requests.post(f"{BASE_URL}/recommend/adaptive", json=baseline_request)
    
    if response.status_code != 200:
        print(f"❌ Failed to get adapted recommendations: {response.status_code}")
        return False
    
    adapted_results = response.json()["recommendations"]
    print(f"✅ Got {len(adapted_results)} adapted recommendations:")
    
    adapted_scores = {}
    for i, item in enumerate(adapted_results, 1):
        item_id = item['id']
        score = item.get('score', 0)
        adapted_scores[item_id] = score
        is_personalized = item.get('is_personalized', False)
        personalized_tag = " 🎯" if is_personalized else ""
        
        print(f"   {i}. {item['title']} (ID: {item_id}){personalized_tag}")
        print(f"      Adapted Score: {score:.4f}")
        
        # Show user feedback if available
        if item.get('user_feedback'):
            feedback_info = item['user_feedback']
            emoji = "👍" if feedback_info['feedback'] == 'like' else "👎"
            print(f"      {emoji} Your feedback: {feedback_info['feedback']}")
    
    # Step 5: Compare scores and show differences
    print(f"\n5️⃣ SCORE COMPARISON & ADAPTATION ANALYSIS")
    print("-" * 50)
    
    has_changes = False
    significant_changes = 0
    
    print("Item-by-item comparison:")
    for item_id in baseline_scores:
        if item_id in adapted_scores:
            baseline_score = baseline_scores[item_id]
            adapted_score = adapted_scores[item_id]
            difference = adapted_score - baseline_score
            
            # Get item name from results
            item_name = next((item['title'] for item in baseline_results if item['id'] == item_id), item_id)
            
            print(f"\n📊 {item_name} (ID: {item_id})")
            print(f"   Before: {baseline_score:.4f}")
            print(f"   After:  {adapted_score:.4f}")
            print(f"   Change: {difference:+.4f}", end="")
            
            if abs(difference) > 0.001:  # Significant change threshold
                has_changes = True
                significant_changes += 1
                if difference > 0:
                    print(" ⬆️ INCREASED (Positive adaptation)")
                else:
                    print(" ⬇️ DECREASED (Negative adaptation)")
            else:
                print(" ➡️ No significant change")
    
    # Step 6: Final verdict
    print(f"\n6️⃣ ADAPTATION VERDICT")
    print("-" * 25)
    
    if has_changes:
        print(f"✅ ALGORITHM IS ADAPTIVE!")
        print(f"   📈 {significant_changes} items showed significant score changes")
        print(f"   🧠 The system learned from your feedback")
        print(f"   🎯 Recommendations are being personalized")
        
        if nike_item_id in adapted_scores and nike_item_id in baseline_scores:
            nike_change = adapted_scores[nike_item_id] - baseline_scores[nike_item_id]
            if nike_change > 0:
                print(f"   👍 Nike item score INCREASED by {nike_change:+.4f} (as expected from like)")
            else:
                print(f"   ⚠️  Nike item score changed by {nike_change:+.4f} (unexpected)")
                
        return True
    else:
        print(f"❌ ALGORITHM APPEARS NOT ADAPTIVE")
        print(f"   📉 No significant score changes detected")
        print(f"   🤔 Possible issues:")
        print(f"      - Adaptation strength too low")
        print(f"      - Feedback not being processed")
        print(f"      - User profile not being used")
        print(f"      - Same user_id not being used consistently")
        return False

def test_user_profile_creation():
    """Test if user profile is being created and used."""
    
    print(f"\n🧠 TESTING USER PROFILE CREATION")
    print("-" * 40)
    
    user_id = "adaptive_test_user"
    
    # Check user stats
    response = requests.get(f"{BASE_URL}/users/{user_id}/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ User profile exists:")
        print(f"   👍 Likes: {stats.get('likes', 0)}")
        print(f"   👎 Dislikes: {stats.get('dislikes', 0)}")
        print(f"   🧠 Preference strength: {stats.get('preference_strength', 0):.3f}")
        print(f"   📝 Has profile: {stats.get('has_preference_profile', False)}")
        
        if stats.get('likes', 0) > 0 or stats.get('dislikes', 0) > 0:
            print("✅ User has feedback history - adaptation should work!")
            return True
        else:
            print("⚠️  User has no feedback history - give some feedback first")
            return False
    else:
        print(f"❌ Could not get user stats: {response.status_code}")
        return False

if __name__ == "__main__":
    try:
        print("🧪 COMPREHENSIVE ADAPTIVE ALGORITHM TEST")
        print("=" * 80)
        
        # Test if algorithm is adaptive
        is_adaptive = test_adaptive_algorithm()
        
        # Test user profile
        has_profile = test_user_profile_creation()
        
        print(f"\n🏆 FINAL RESULTS")
        print("=" * 30)
        print(f"Algorithm Adaptive: {'✅ YES' if is_adaptive else '❌ NO'}")
        print(f"User Profile Active: {'✅ YES' if has_profile else '❌ NO'}")
        
        if is_adaptive and has_profile:
            print(f"\n🎉 YOUR ADAPTIVE SYSTEM IS WORKING PERFECTLY!")
            print(f"💡 The algorithm learns from feedback and adapts recommendations!")
        else:
            print(f"\n⚠️  ISSUES DETECTED - CHECK THE DETAILS ABOVE")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running! Start with: python adaptive_api.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
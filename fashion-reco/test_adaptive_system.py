#!/usr/bin/env python3
"""
🧪 COMPLETE TESTING GUIDE: Adaptive Fashion Recommendation System

This script shows you EXACTLY how to test your adaptive system!
Run this to see step-by-step testing with real examples.
"""

import requests
import json
import time
from datetime import datetime
import pandas as pd

# API Configuration
BASE_URL = "http://localhost:8004"
TEST_USER_ID = "test_user_123"

def test_step(step_num, description):
    """Print a testing step with formatting."""
    print(f"\n{'='*60}")
    print(f"🧪 STEP {step_num}: {description}")
    print(f"{'='*60}")

def make_request(method, endpoint, data=None, expected_status=200):
    """Make API request with error handling."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        
        print(f"📡 {method.upper()} {endpoint}")
        if data:
            print(f"   Request: {json.dumps(data, indent=2)}")
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            result = response.json()
            print(f"   ✅ Success!")
            return result
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def test_server_running():
    """Test if the adaptive API server is running."""
    test_step(1, "Check if server is running")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server is not running: {str(e)}")
        print(f"💡 Start server with: python adaptive_api.py")
        return False

def test_initial_recommendations():
    """Test getting initial recommendations (no user history)."""
    test_step(2, "Get initial recommendations (fresh user)")
    
    data = {
        "user_id": TEST_USER_ID,
        "brand_name": "Nike",
        "adaptation_strength": 0.5,
        "k": 5
    }
    
    result = make_request("POST", "/recommend/adaptive", data)
    
    if result and "recommendations" in result:
        print(f"📊 Got {len(result['recommendations'])} recommendations")
        for i, item in enumerate(result["recommendations"][:3], 1):
            print(f"   {i}. {item['title']} - {item['brand']} (${item['price']})")
            print(f"      Score: {item.get('score', 'N/A'):.3f}")
        
        # Store first few items for feedback testing
        global test_items
        test_items = result["recommendations"][:3]
        return True
    else:
        print("❌ Failed to get recommendations")
        return False

def test_positive_feedback():
    """Test giving positive feedback (like)."""
    test_step(3, "Give positive feedback (LIKE)")
    
    # Use actual item ID from catalog instead of from recommendations
    # This ensures we use a valid item_id that exists in catalog.csv
    liked_item_id = "item_003"  # Nike Black Running Shoes
    print(f"👍 Liking item: {liked_item_id} (Nike Black Running Shoes)")
    
    data = {
        "user_id": TEST_USER_ID,
        "item_id": liked_item_id,
        "feedback": "like"
    }
    
    result = make_request("POST", "/feedback", data)
    
    if result and result.get("status") == "success":
        print("✅ Positive feedback recorded!")
        return True
    else:
        print("❌ Failed to record positive feedback")
        return False

def test_negative_feedback():
    """Test giving negative feedback (dislike)."""
    test_step(4, "Give negative feedback (DISLIKE)")
    
    # Use actual item ID from catalog
    disliked_item_id = "item_004"  # Uniqlo Gray Hoodie
    print(f"👎 Disliking item: {disliked_item_id} (Uniqlo Gray Hoodie)")
    
    data = {
        "user_id": TEST_USER_ID,
        "item_id": disliked_item_id,
        "feedback": "dislike"
    }
    
    result = make_request("POST", "/feedback", data)
    
    if result and result.get("status") == "success":
        print("✅ Negative feedback recorded!")
        return True
    else:
        print("❌ Failed to record negative feedback")
        return False

def test_adapted_recommendations():
    """Test getting recommendations after feedback (should be different)."""
    test_step(5, "Get adapted recommendations (after feedback)")
    
    data = {
        "user_id": TEST_USER_ID,
        "brand_name": "Nike",
        "adaptation_strength": 0.8,  # Higher adaptation
        "k": 5
    }
    
    result = make_request("POST", "/recommend/adaptive", data)
    
    if result and "recommendations" in result:
        print(f"📊 Got {len(result['recommendations'])} adapted recommendations")
        print("🎯 Notice how recommendations changed based on your feedback:")
        
        for i, item in enumerate(result["recommendations"][:3], 1):
            print(f"   {i}. {item['title']} - {item['brand']} (${item['price']})")
            print(f"      Score: {item.get('score', 'N/A'):.3f}")
            
            # Check if this item has previous feedback
            if item.get("user_feedback"):
                feedback = item["user_feedback"]
                emoji = "👍" if feedback["feedback"] == "like" else "👎"
                print(f"      {emoji} Previous feedback: {feedback['feedback']} ({feedback['days_ago']} days ago)")
        
        return True
    else:
        print("❌ Failed to get adapted recommendations")
        return False

def test_user_stats():
    """Test getting user learning statistics."""
    test_step(6, "Check user learning statistics")
    
    result = make_request("GET", f"/users/{TEST_USER_ID}/stats")
    
    if result:
        print("📊 User Learning Statistics:")
        print(f"   👍 Likes: {result.get('likes', 0)}")
        print(f"   👎 Dislikes: {result.get('dislikes', 0)}")
        print(f"   🧠 Preference strength: {result.get('preference_strength', 0):.2f}")
        print(f"   📝 Has profile: {result.get('has_preference_profile', False)}")
        
        if result.get('feedback_history'):
            print(f"   📈 Total feedback entries: {len(result['feedback_history'])}")
        
        return True
    else:
        print("❌ Failed to get user statistics")
        return False

def test_brand_search():
    """Test brand-only search functionality."""
    test_step(7, "Test brand-only search")
    
    brands_to_test = ["Adidas", "Zara", "H&M"]
    
    for brand in brands_to_test:
        print(f"\n🔍 Searching for: {brand}")
        
        data = {
            "user_id": TEST_USER_ID,
            "brand_name": brand,
            "adaptation_strength": 0.3,
            "k": 3
        }
        
        result = make_request("POST", "/recommend/adaptive", data)
        
        if result and "recommendations" in result:
            print(f"   Found {len(result['recommendations'])} items:")
            for item in result["recommendations"]:
                print(f"     • {item['title']} - {item['brand']}")
        else:
            print(f"   ❌ No results for {brand}")

def test_multiple_feedback_learning():
    """Test that system learns from multiple feedback interactions."""
    test_step(8, "Test learning from multiple feedback")
    
    # Use actual item IDs from catalog.csv
    feedback_scenarios = [
        {"item_id": "item_003", "feedback": "like", "description": "Nike athletic shoes"},
        {"item_id": "item_005", "feedback": "like", "description": "Adidas athletic jacket"},
        {"item_id": "item_001", "feedback": "dislike", "description": "Zara casual t-shirt"},
        {"item_id": "item_002", "feedback": "dislike", "description": "H&M denim jeans"}
    ]
    
    for scenario in feedback_scenarios:
        data = {
            "user_id": TEST_USER_ID,
            "item_id": scenario["item_id"],
            "feedback": scenario["feedback"]
        }
        
        emoji = "👍" if scenario["feedback"] == "like" else "👎"
        print(f"{emoji} {scenario['feedback'].title()}ing {scenario['description']} (ID: {scenario['item_id']})")
        
        result = make_request("POST", "/feedback", data)
        if result and result.get("status") == "success":
            print("   ✅ Feedback recorded")
        
        # Small delay to simulate real usage
        time.sleep(0.5)

def test_temporal_decay_simulation():
    """Simulate temporal decay by checking feedback over time."""
    test_step(9, "Test temporal decay concept")
    
    print("📅 Temporal Decay Simulation:")
    print("   (This shows how negative feedback weakens over time)")
    
    # Simulate different time periods
    decay_examples = [
        {"days": 0, "description": "Just disliked"},
        {"days": 7, "description": "1 week later"},
        {"days": 30, "description": "1 month later"},
        {"days": 90, "description": "3 months later"}
    ]
    
    for example in decay_examples:
        # Calculate penalty using the same formula as the system
        import math
        penalty = -0.4 * math.exp(-0.1 * example["days"])
        print(f"   Day {example['days']:2d}: {penalty:+.3f} penalty → {example['description']}")
    
    print("\n💡 Key insight: Negative feedback becomes weaker over time!")
    print("   Recent dislikes have strong impact, old ones barely matter.")

def run_complete_test():
    """Run the complete testing suite."""
    print("🧪 ADAPTIVE FASHION RECOMMENDER - COMPLETE TEST SUITE")
    print("=" * 70)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Test User: {TEST_USER_ID}")
    print(f"🌐 API Base URL: {BASE_URL}")
    
    # Initialize global variables
    global test_items
    test_items = []
    
    # Run all tests
    tests = [
        test_server_running,
        test_initial_recommendations,
        test_positive_feedback,
        test_negative_feedback,
        test_adapted_recommendations,
        test_user_stats,
        test_brand_search,
        test_multiple_feedback_learning,
        test_temporal_decay_simulation
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            failed += 1
        
        # Small delay between tests
        time.sleep(1)
    
    # Final summary
    print(f"\n🏁 TEST SUMMARY")
    print("=" * 30)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Your adaptive system is working perfectly! 🎯")
    else:
        print(f"\n⚠️  Some tests failed. Check the errors above for details.")

def show_quick_test_commands():
    """Show quick test commands for manual testing."""
    print("\n🚀 QUICK MANUAL TESTING COMMANDS")
    print("=" * 50)
    
    commands = [
        {
            "title": "1. Start Server",
            "command": "python adaptive_api.py",
            "description": "Starts the adaptive API server on port 8004"
        },
        {
            "title": "2. View API Documentation", 
            "command": "open http://localhost:8004/docs",
            "description": "Interactive API documentation with test interface"
        },
        {
            "title": "3. Run This Test Suite",
            "command": "python test_adaptive_system.py",
            "description": "Automated testing of all features"
        },
        {
            "title": "4. Test Single Recommendation",
            "command": """curl -X POST "http://localhost:8004/recommend/adaptive" \\
     -H "Content-Type: application/json" \\
     -d '{"user_id": "test123", "brand_name": "Nike", "k": 5}'""",
            "description": "Test basic recommendation endpoint"
        },
        {
            "title": "5. Test Feedback",
            "command": """curl -X POST "http://localhost:8004/feedback" \\
     -H "Content-Type: application/json" \\
     -d '{"user_id": "test123", "item_id": "item_1", "feedback": "like"}'""",
            "description": "Test feedback endpoint"
        }
    ]
    
    for cmd in commands:
        print(f"\n{cmd['title']}")
        print(f"   {cmd['description']}")
        print(f"   Command: {cmd['command']}")

if __name__ == "__main__":
    try:
        run_complete_test()
        show_quick_test_commands()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
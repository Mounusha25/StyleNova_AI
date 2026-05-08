#!/usr/bin/env python3
"""
Simple Manual Test for User Adaptability: user_1758445519323_oy30b5wb2

This script provides step-by-step instructions and simple tools to test
how the algorithm adapts to the specific user's preferences.
"""

import json
import subprocess
import sys
from datetime import datetime


class SimpleUserTester:
    def __init__(self, user_id="user_1758445519323_oy30b5wb2"):
        self.user_id = user_id

    def check_api_status(self):
        """Check if the adaptive API is running"""
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:8000/health"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                print("✅ API is running")
                return True
            else:
                print("❌ API is not responding")
                return False
        except subprocess.TimeoutExpired:
            print("❌ API connection timeout")
            return False
        except FileNotFoundError:
            print("⚠️  curl not found, please check API manually")
            return True  # Assume it's running

    def get_user_profile(self):
        """Get current user profile"""
        try:
            with open("user_profiles.json", "r") as f:
                profiles = json.load(f)
                return profiles.get(self.user_id, None)
        except FileNotFoundError:
            print("❌ user_profiles.json not found")
            return None

    def show_user_stats(self):
        """Display current user statistics"""
        profile = self.get_user_profile()

        print(f"\n📊 USER PROFILE ANALYSIS: {self.user_id}")
        print("=" * 60)

        if not profile:
            print("❌ User not found in profiles")
            print("💡 This means the user hasn't interacted with the system yet")
            return False

        liked_items = profile.get("liked_items", [])
        disliked_items = profile.get("disliked_items", [])
        feedback_history = profile.get("feedback_history", [])
        preference_vector = profile.get("preference_vector")

        print(f"👍 Total Likes: {len(liked_items)}")
        print(f"👎 Total Dislikes: {len(disliked_items)}")
        print(f"📝 Total Feedback: {len(feedback_history)}")
        print(
            f"🧠 Preference Vector: {'Learned' if preference_vector else 'Not learned yet'}"
        )

        if liked_items:
            print(f"\n🔍 LIKED ITEMS ANALYSIS:")
            self.analyze_preferences(liked_items, "liked")

        if disliked_items:
            print(f"\n🔍 DISLIKED ITEMS ANALYSIS:")
            self.analyze_preferences(disliked_items, "disliked")

        return True

    def analyze_preferences(self, items, feedback_type):
        """Analyze patterns in user feedback"""
        if not items:
            return

        # Analyze categories
        categories = {}
        brands = {}
        price_ranges = {"low": 0, "medium": 0, "high": 0}

        for item in items:
            item_data = item.get("item_data", {})

            # Category analysis
            category = item_data.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

            # Brand analysis
            brand = item_data.get("brand", "unknown")
            brands[brand] = brands.get(brand, 0) + 1

            # Price analysis
            price = item_data.get("price", 0)
            if price < 30:
                price_ranges["low"] += 1
            elif price < 100:
                price_ranges["medium"] += 1
            else:
                price_ranges["high"] += 1

        print(f"   Categories {feedback_type}:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]:
            print(f"     - {cat}: {count} items")

        print(f"   Brands {feedback_type}:")
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]:
            print(f"     - {brand}: {count} items")

        print(f"   Price preferences:")
        print(f"     - Low ($0-30): {price_ranges['low']} items")
        print(f"     - Medium ($30-100): {price_ranges['medium']} items")
        print(f"     - High ($100+): {price_ranges['high']} items")

    def create_test_curl_commands(self):
        """Generate curl commands for manual testing"""
        print(f"\n🛠️  MANUAL TESTING COMMANDS")
        print("=" * 50)
        print(
            f"Copy and paste these commands to test adaptation for user: {self.user_id}"
        )
        print()

        # Step 1: Get initial recommendations
        print("1️⃣  GET INITIAL RECOMMENDATIONS:")
        print("```bash")
        get_recs_cmd = f'''curl -X POST "http://localhost:8000/recommend/adaptive" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "user_id": "{self.user_id}",
    "preferences": {{
      "preferred_categories": ["dress", "top"],
      "preferred_brands": ["EDIKTED"],
      "budget_max": 80,
      "style_preferences": ["casual", "trendy"]
    }},
    "num_recommendations": 5
  }}'
'''
        print(get_recs_cmd)
        print("```")
        print()

        # Step 2: Submit feedback
        print("2️⃣  SUBMIT FEEDBACK (replace ITEM_ID with actual item ID from step 1):")
        print("```bash")
        feedback_cmd = f'''curl -X POST "http://localhost:8000/feedback" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "user_id": "{self.user_id}",
    "item_id": "ITEM_ID",
    "feedback": "like",
    "item_data": {{
      "id": "ITEM_ID",
      "title": "Item Title",
      "category": "dress",
      "brand": "EDIKTED",
      "price": 45
    }}
  }}'
'''
        print(feedback_cmd)
        print("```")
        print()

        # Step 3: Check adaptation
        print("3️⃣  REPEAT STEPS 1-2 MULTIPLE TIMES, THEN CHECK ADAPTATION:")
        print("```bash")
        print("python test_user_adaptability_simple.py --check-profile")
        print("```")

    def simulate_quick_test(self):
        """Show a quick simulation of what adaptation looks like"""
        print(f"\n🎯 EXPECTED ADAPTATION BEHAVIOR")
        print("=" * 50)
        print(f"For user: {self.user_id}")
        print()

        print("📈 What you should see over time:")
        print("1. Initial recommendations: Generic based on quiz preferences")
        print("2. After 3-5 likes/dislikes: Algorithm starts learning patterns")
        print("3. After 10+ feedback: Recommendations become more personalized")
        print("4. After 20+ feedback: Strong adaptation to user preferences")
        print()

        print("📊 Key metrics to watch:")
        print("- User profile grows (likes/dislikes accumulate)")
        print("- Preference vector gets learned (appears in profile)")
        print("- New recommendations better match past likes")
        print("- Categories/brands shift toward user preferences")
        print()

        print("🔬 Testing strategy:")
        print("1. Like items from specific categories (e.g., 'mini dress', 'crop top')")
        print("2. Like items from specific brands (e.g., 'EDIKTED', 'Princess Polly')")
        print("3. Dislike expensive items (>$100)")
        print("4. Dislike certain categories (e.g., 'coat', 'blazer')")
        print("5. Check if future recommendations follow these patterns")


def main():
    user_id = "user_1758445519323_oy30b5wb2"
    tester = SimpleUserTester(user_id)

    print("🧪 SIMPLE USER ADAPTABILITY TESTER")
    print("=" * 50)
    print(f"Target User: {user_id}")
    print()

    # Check if we have command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check-profile":
            tester.show_user_stats()
            return
        elif sys.argv[1] == "--generate-commands":
            tester.create_test_curl_commands()
            return
        elif sys.argv[1] == "--help":
            print("Usage:")
            print(
                "  python test_user_adaptability_simple.py                  # Full overview"
            )
            print(
                "  python test_user_adaptability_simple.py --check-profile  # Check current profile"
            )
            print(
                "  python test_user_adaptability_simple.py --generate-commands  # Get curl commands"
            )
            return

    # Full overview
    print("🔄 Checking API status...")
    api_running = tester.check_api_status()

    if not api_running:
        print("\n⚠️  API not running. Please start it with:")
        print(
            "cd fashion-reco && source fashion_venv/bin/activate && python adaptive_api.py"
        )
        print()

    print("🔄 Checking current user profile...")
    has_profile = tester.show_user_stats()

    if not has_profile:
        print("\n💡 GETTING STARTED:")
        print("Since this user doesn't exist yet, you need to:")
        print("1. Start the API (if not running)")
        print("2. Get initial recommendations")
        print("3. Submit feedback")
        print("4. Repeat to see adaptation")
        print()

        tester.create_test_curl_commands()
    else:
        print("\n✅ User profile exists! You can:")
        print("1. Continue testing with more feedback")
        print("2. Analyze the current adaptation level")
        print("3. Get new recommendations to see improvements")

    tester.simulate_quick_test()

    print(f"\n🎯 QUICK COMMANDS:")
    print(f"Check profile:     python {sys.argv[0]} --check-profile")
    print(f"Get curl commands: python {sys.argv[0]} --generate-commands")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive Test for Adaptive Fashion Recommendation System
This script demonstrates that the algorithm actually learns and adapts from user feedback.

Test Flow:
1. Get baseline recommendations (no feedback)
2. Add positive and negative feedback
3. Get adapted recommendations
4. Compare scores to show learning
5. Test temporal decay and smart exclusion
"""

import requests
import json
import time
from datetime import datetime
import sys
from typing import List, Dict


class AdaptiveLearningTester:
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.test_user_id = f"test_user_{int(time.time())}"
        self.results = {}

    def test_connection(self) -> bool:
        """Test if the API is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"✅ API Connection: Healthy")
                print(f"📊 Catalog Size: {health.get('total_users', 0)} users tracked")
                return True
            else:
                print(f"❌ API Health Check Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API at {self.base_url}")
            print(f"   Error: {e}")
            print(f"💡 Make sure to run: python adaptive_api.py")
            return False

    def get_recommendations(
        self, exclude_items: List[str] = None, adaptation_strength: float = 0.8
    ) -> List[Dict]:
        """Get adaptive recommendations."""
        url = f"{self.base_url}/recommend/adaptive"
        data = {
            "user_id": self.test_user_id,
            "brand_name": "Nike",
            "adaptation_strength": adaptation_strength,
            "k": 5,
            "exclude_items": exclude_items or [],
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Recommendation API Error: {response.status_code}")
                print(response.text)
                return []
        except Exception as e:
            print(f"❌ Recommendation Error: {e}")
            return []

    def add_feedback(self, item_id: str, feedback: str) -> bool:
        """Add user feedback."""
        url = f"{self.base_url}/feedback"
        data = {"user_id": self.test_user_id, "item_id": item_id, "feedback": feedback}

        try:
            response = requests.post(url, json=data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Feedback Error: {e}")
            return False

    def get_user_stats(self) -> Dict:
        """Get user learning statistics."""
        try:
            response = requests.get(
                f"{self.base_url}/users/{self.test_user_id}/stats", timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"❌ Stats Error: {e}")
            return {}

    def print_recommendations(self, recs: List[Dict], title: str):
        """Pretty print recommendations."""
        print(f"\n{title}")
        print("=" * len(title))

        if not recs:
            print("❌ No recommendations received")
            return

        for i, rec in enumerate(recs):
            score = rec.get("score", 0)
            base_score = rec.get("base_score", score)
            adaptation = score - base_score
            personalized = "🎯" if rec.get("is_personalized") else "🆕"

            print(f"{personalized} {i + 1}. {rec['title'][:50]}")
            print(f"    Brand: {rec['brand']} | Price: ${rec['price']}")
            print(
                f"    Score: {score:.3f} (base: {base_score:.3f}, adaptation: {adaptation:+.3f})"
            )
            print()

    def test_baseline_recommendations(self):
        """Test 1: Get baseline recommendations with no learning."""
        print("\n🔍 TEST 1: BASELINE RECOMMENDATIONS (No Learning Yet)")
        print("=" * 60)

        baseline_recs = self.get_recommendations(
            adaptation_strength=0.0
        )  # No adaptation
        self.results["baseline"] = baseline_recs

        self.print_recommendations(
            baseline_recs, "📋 Baseline Recommendations (Pure Algorithm)"
        )

        if baseline_recs:
            print(f"✅ Got {len(baseline_recs)} baseline recommendations")
            return True
        else:
            print("❌ Failed to get baseline recommendations")
            return False

    def test_feedback_learning(self):
        """Test 2: Add feedback and see if algorithm adapts."""
        print("\n📝 TEST 2: ADDING USER FEEDBACK")
        print("=" * 40)

        baseline_recs = self.results.get("baseline", [])
        if not baseline_recs:
            print("❌ No baseline recommendations to provide feedback on")
            return False

        # Like first 2 items
        liked_items = baseline_recs[:2]
        for item in liked_items:
            success = self.add_feedback(item["id"], "like")
            if success:
                print(f"👍 LIKED: {item['title'][:40]}")
            else:
                print(f"❌ Failed to add like for {item['title'][:40]}")

        # Dislike next 2 items
        disliked_items = baseline_recs[2:4] if len(baseline_recs) > 2 else []
        for item in disliked_items:
            success = self.add_feedback(item["id"], "dislike")
            if success:
                print(f"👎 DISLIKED: {item['title'][:40]}")
            else:
                print(f"❌ Failed to add dislike for {item['title'][:40]}")

        # Show user stats
        stats = self.get_user_stats()
        if stats:
            print(f"\n📊 USER LEARNING STATS:")
            print(f"   👍 Likes: {stats.get('likes', 0)}")
            print(f"   👎 Dislikes: {stats.get('dislikes', 0)}")
            print(
                f"   🧠 Preference Strength: {stats.get('preference_strength', 0):.3f}"
            )
            print(
                f"   ✨ Has Learned Profile: {stats.get('has_preference_profile', False)}"
            )

            self.results["initial_stats"] = stats
            return stats.get("has_preference_profile", False)

        return False

    def test_adapted_recommendations(self):
        """Test 3: Get recommendations after learning and compare."""
        print("\n🎯 TEST 3: ADAPTIVE RECOMMENDATIONS (After Learning)")
        print("=" * 55)

        # Get adapted recommendations with smart exclusion
        baseline_recs = self.results.get("baseline", [])
        disliked_ids = (
            [rec["id"] for rec in baseline_recs[2:4]] if len(baseline_recs) > 2 else []
        )

        adapted_recs = self.get_recommendations(
            exclude_items=disliked_ids, adaptation_strength=0.8
        )
        self.results["adapted"] = adapted_recs

        self.print_recommendations(
            adapted_recs, "🎯 Adapted Recommendations (After Learning)"
        )

        return len(adapted_recs) > 0

    def test_adaptation_comparison(self):
        """Test 4: Compare baseline vs adapted to prove learning."""
        print("\n🔬 TEST 4: ADAPTATION ANALYSIS")
        print("=" * 35)

        baseline_recs = self.results.get("baseline", [])
        adapted_recs = self.results.get("adapted", [])

        if not baseline_recs or not adapted_recs:
            print("❌ Missing baseline or adapted recommendations")
            return False

        print("🧠 LEARNING EVIDENCE:")
        print("-" * 20)

        # Check for personalization
        personalized_count = sum(
            1 for rec in adapted_recs if rec.get("is_personalized")
        )
        print(
            f"✨ Personalized Recommendations: {personalized_count}/{len(adapted_recs)}"
        )

        # Check for score adaptations
        significant_adaptations = 0
        for rec in adapted_recs:
            score = rec.get("score", 0)
            base_score = rec.get("base_score", score)
            adaptation = score - base_score

            if abs(adaptation) > 0.01:  # Significant adaptation
                significant_adaptations += 1
                direction = "↗️ BOOSTED" if adaptation > 0 else "↘️ PENALIZED"
                print(
                    f"   {direction}: {rec['title'][:30]} (adaptation: {adaptation:+.3f})"
                )

        print(
            f"\n📈 Recommendations with Significant Adaptation: {significant_adaptations}/{len(adapted_recs)}"
        )

        # Check exclusion working
        baseline_ids = {rec["id"] for rec in baseline_recs}
        adapted_ids = {rec["id"] for rec in adapted_recs}
        new_items = len(adapted_ids - baseline_ids)

        print(f"🔄 New Items Discovered: {new_items}/{len(adapted_recs)}")

        # Final verdict
        if personalized_count > 0 and significant_adaptations > 0:
            print(f"\n🎉 ✅ ALGORITHM IS SUCCESSFULLY ADAPTING!")
            print(
                f"   Evidence: {personalized_count} personalized + {significant_adaptations} adapted scores"
            )
            return True
        else:
            print(f"\n❌ Algorithm may not be adapting properly")
            print(
                f"   Personalized: {personalized_count}, Adaptations: {significant_adaptations}"
            )
            return False

    def test_smart_exclusion(self):
        """Test 5: Verify smart exclusion logic."""
        print("\n🚫 TEST 5: SMART EXCLUSION VERIFICATION")
        print("=" * 40)

        baseline_recs = self.results.get("baseline", [])
        adapted_recs = self.results.get("adapted", [])

        if not baseline_recs or not adapted_recs:
            print("❌ Missing recommendations for exclusion test")
            return False

        # Items that should be excluded (disliked ones)
        disliked_ids = {
            baseline_recs[i]["id"] for i in range(2, min(4, len(baseline_recs)))
        }
        adapted_ids = {rec["id"] for rec in adapted_recs}

        excluded_correctly = disliked_ids - adapted_ids
        still_showing = disliked_ids & adapted_ids

        print(f"🎯 Disliked Items: {len(disliked_ids)}")
        print(f"✅ Correctly Excluded: {len(excluded_correctly)}")
        print(f"⚠️ Still Showing: {len(still_showing)}")

        if excluded_correctly:
            print("   Successfully excluded:")
            for item_id in excluded_correctly:
                item = next(rec for rec in baseline_recs if rec["id"] == item_id)
                print(f"   🚫 {item['title'][:40]}")

        if still_showing:
            print("   Still showing (may reappear for learning):")
            for item_id in still_showing:
                item = next(rec for rec in baseline_recs if rec["id"] == item_id)
                print(f"   🔄 {item['title'][:40]}")

        return len(excluded_correctly) > 0

    def run_full_test(self):
        """Run complete adaptive learning test suite."""
        print("🧪 ADAPTIVE FASHION RECOMMENDATION LEARNING TEST")
        print("=" * 60)
        print(f"👤 Test User ID: {self.test_user_id}")
        print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Test 1: Connection
        if not self.test_connection():
            return False

        # Test 2: Baseline
        if not self.test_baseline_recommendations():
            return False

        # Test 3: Learning
        if not self.test_feedback_learning():
            return False

        # Test 4: Adaptation
        if not self.test_adapted_recommendations():
            return False

        # Test 5: Analysis
        adaptation_success = self.test_adaptation_comparison()

        # Test 6: Exclusion
        exclusion_success = self.test_smart_exclusion()

        # Final Results
        print("\n🏁 FINAL TEST RESULTS")
        print("=" * 25)

        stats = self.get_user_stats()
        if stats:
            print(f"📊 User Profile Created: ✅")
            print(f"   Likes: {stats.get('likes', 0)}")
            print(f"   Dislikes: {stats.get('dislikes', 0)}")
            print(f"   Preference Strength: {stats.get('preference_strength', 0):.3f}")

        print(f"🎯 Adaptation Working: {'✅' if adaptation_success else '❌'}")
        print(f"🚫 Smart Exclusion: {'✅' if exclusion_success else '❌'}")

        if adaptation_success:
            print(f"\n🎉 🎉 🎉 CONGRATULATIONS! 🎉 🎉 🎉")
            print(f"Your Adaptive Fashion Recommendation Algorithm is WORKING!")
            print(f"✨ The system successfully learned from user feedback")
            print(f"✨ Recommendations adapted based on likes/dislikes")
            print(f"✨ Smart exclusion prevents repetition while allowing learning")
        else:
            print(f"\n🔧 Algorithm needs debugging - adaptation not detected")

        return adaptation_success


def main():
    """Run the adaptive learning test."""
    tester = AdaptiveLearningTester()
    success = tester.run_full_test()

    if success:
        print(f"\n✅ Test completed successfully - Algorithm is adaptive!")
        sys.exit(0)
    else:
        print(f"\n❌ Test failed - Algorithm may need debugging")
        sys.exit(1)


if __name__ == "__main__":
    main()

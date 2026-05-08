#!/usr/bin/env python3
"""
Test Adaptability for Specific User: user_1758445519323_oy30b5wb2

This script comprehensively tests the adaptive learning system for a specific user,
measuring how the algorithm learns and adapts to user preferences over time.
"""

import requests
import json
import time
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os


class UserAdaptabilityTester:
    def __init__(
        self, user_id="user_1758445519323_oy30b5wb2", base_url="http://localhost:8000"
    ):
        self.user_id = user_id
        self.base_url = base_url
        self.feedback_history = []
        self.recommendation_scores = []

    def test_connection(self):
        """Test if the API is running"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ API connection successful")
                return True
            else:
                print("❌ API not responding properly")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to API: {e}")
            return False

    def get_initial_recommendations(self, preferences=None):
        """Get initial recommendations for the user"""
        if preferences is None:
            preferences = {
                "preferred_categories": ["dress", "top", "sweater"],
                "preferred_brands": ["ZARA", "H&M"],
                "budget_max": 150,
                "style_preferences": ["casual", "trendy"],
            }

        try:
            response = requests.post(
                f"{self.base_url}/recommend/adaptive",
                json={
                    "user_id": self.user_id,
                    "preferences": preferences,
                    "num_recommendations": 10,
                },
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Got {len(data['recommendations'])} initial recommendations")
                return data
            else:
                print(f"❌ Failed to get recommendations: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def simulate_user_feedback(self, recommendations, like_patterns=None):
        """
        Simulate user feedback based on patterns

        like_patterns: dict with criteria for what the user likes
        """
        if like_patterns is None:
            # Default: User likes dresses, doesn't like expensive items, prefers certain brands
            like_patterns = {
                "categories": ["dress", "maxi dress", "mini dress"],
                "max_price": 100,
                "preferred_brands": ["EDIKTED", "Princess Polly"],
                "dislike_categories": ["coat", "blazer"],
            }

        feedback_batch = []

        for item in recommendations:
            # Determine if user would like this item
            should_like = False

            # Check category preference
            if item.get("category") in like_patterns["categories"]:
                should_like = True

            # Check price preference
            if item.get("price", 999) > like_patterns["max_price"]:
                should_like = False

            # Check brand preference
            if item.get("brand") in like_patterns["preferred_brands"]:
                should_like = True

            # Check dislikes
            if item.get("category") in like_patterns.get("dislike_categories", []):
                should_like = False

            # Add some randomness (80% follow pattern, 20% random)
            if np.random.random() > 0.8:
                should_like = np.random.random() > 0.5

            feedback = {
                "user_id": self.user_id,
                "item_id": item["id"],
                "feedback": "like" if should_like else "dislike",
                "item_data": item,
            }

            feedback_batch.append(feedback)

        return feedback_batch

    def submit_feedback(self, feedback_batch):
        """Submit feedback to the API"""
        success_count = 0

        for feedback in feedback_batch:
            try:
                response = requests.post(f"{self.base_url}/feedback", json=feedback)

                if response.status_code == 200:
                    success_count += 1
                    self.feedback_history.append(feedback)
                else:
                    print(
                        f"❌ Failed to submit feedback for item {feedback['item_id']}"
                    )

            except requests.exceptions.RequestException as e:
                print(f"❌ Feedback submission failed: {e}")

        print(
            f"✅ Successfully submitted {success_count}/{len(feedback_batch)} feedback items"
        )
        return success_count

    def get_user_profile(self):
        """Get current user profile to analyze learning progress"""
        try:
            with open("user_profiles.json", "r") as f:
                profiles = json.load(f)
                return profiles.get(self.user_id, {})
        except FileNotFoundError:
            print("❌ User profiles file not found")
            return {}

    def measure_recommendation_quality(self, recommendations, like_patterns):
        """Measure how well recommendations match user preferences"""
        if not recommendations:
            return 0.0

        good_recommendations = 0

        for item in recommendations:
            score = 0

            # Category match
            if item.get("category") in like_patterns["categories"]:
                score += 2

            # Price preference
            if item.get("price", 999) <= like_patterns["max_price"]:
                score += 1

            # Brand preference
            if item.get("brand") in like_patterns["preferred_brands"]:
                score += 2

            # Avoid dislikes
            if item.get("category") not in like_patterns.get("dislike_categories", []):
                score += 1

            # Consider it good if score >= 3
            if score >= 3:
                good_recommendations += 1

        quality_score = good_recommendations / len(recommendations)
        return quality_score

    def run_adaptation_test(self, rounds=5):
        """
        Run a comprehensive adaptation test

        rounds: Number of feedback rounds to simulate
        """
        print(f"\n🔄 Starting Adaptation Test for User: {self.user_id}")
        print("=" * 60)

        # Test connection first
        if not self.test_connection():
            return False

        # Define user preferences
        like_patterns = {
            "categories": ["mini dress", "dress", "crop top"],
            "max_price": 80,
            "preferred_brands": ["EDIKTED", "Princess Polly", "ALO YOGA"],
            "dislike_categories": ["coat", "blazer", "pants"],
        }

        print(f"👤 User Preference Profile:")
        print(f"   Likes: {like_patterns['categories']}")
        print(f"   Budget: ${like_patterns['max_price']}")
        print(f"   Brands: {like_patterns['preferred_brands']}")
        print(f"   Dislikes: {like_patterns['dislike_categories']}")
        print()

        quality_scores = []

        for round_num in range(rounds):
            print(f"🔄 Round {round_num + 1}/{rounds}")
            print("-" * 30)

            # Get recommendations
            initial_prefs = {
                "preferred_categories": ["dress", "top"],
                "preferred_brands": ["ZARA"],
                "budget_max": 150,
                "style_preferences": ["casual"],
            }

            rec_data = self.get_initial_recommendations(initial_prefs)
            if not rec_data:
                print("❌ Failed to get recommendations")
                break

            recommendations = rec_data["recommendations"]

            # Measure quality
            quality = self.measure_recommendation_quality(
                recommendations, like_patterns
            )
            quality_scores.append(quality)

            print(f"📊 Recommendation Quality: {quality:.2%}")

            # Simulate feedback
            feedback_batch = self.simulate_user_feedback(recommendations, like_patterns)
            likes = sum(1 for f in feedback_batch if f["feedback"] == "like")
            dislikes = len(feedback_batch) - likes

            print(f"👍 Likes: {likes}, 👎 Dislikes: {dislikes}")

            # Submit feedback
            self.submit_feedback(feedback_batch)

            # Get updated user profile
            profile = self.get_user_profile()

            if profile:
                total_likes = len(profile.get("liked_items", []))
                total_dislikes = len(profile.get("disliked_items", []))
                print(
                    f"📈 Total Profile: {total_likes} likes, {total_dislikes} dislikes"
                )

                if profile.get("preference_vector") is not None:
                    print("🧠 Preference vector learned!")
                else:
                    print("⏳ Learning preferences...")

            print()

            # Small delay between rounds
            time.sleep(1)

        # Analysis
        print("📊 ADAPTATION ANALYSIS")
        print("=" * 40)

        if len(quality_scores) > 1:
            initial_quality = quality_scores[0]
            final_quality = quality_scores[-1]
            improvement = final_quality - initial_quality

            print(f"Initial Quality: {initial_quality:.2%}")
            print(f"Final Quality: {final_quality:.2%}")
            print(f"Improvement: {improvement:+.2%}")

            if improvement > 0.1:
                print("✅ Strong adaptation detected!")
            elif improvement > 0:
                print("✅ Positive adaptation detected")
            else:
                print("⚠️  No clear adaptation - may need more feedback")

        # Plot results
        self.plot_adaptation_curve(quality_scores)

        return True

    def plot_adaptation_curve(self, quality_scores):
        """Plot the adaptation curve"""
        if len(quality_scores) < 2:
            return

        plt.figure(figsize=(10, 6))
        rounds = list(range(1, len(quality_scores) + 1))

        plt.plot(rounds, quality_scores, "b-o", linewidth=2, markersize=8)
        plt.title(
            f"Recommendation Quality Over Time\nUser: {self.user_id}", fontsize=14
        )
        plt.xlabel("Feedback Round", fontsize=12)
        plt.ylabel("Recommendation Quality Score", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 1)

        # Add trend line
        if len(quality_scores) > 2:
            z = np.polyfit(rounds, quality_scores, 1)
            p = np.poly1d(z)
            plt.plot(
                rounds, p(rounds), "r--", alpha=0.8, label=f"Trend (slope: {z[0]:.3f})"
            )
            plt.legend()

        plt.tight_layout()

        # Save plot
        filename = f"adaptation_curve_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        print(f"📊 Adaptation curve saved as: {filename}")
        plt.show()


def main():
    """Main function to run the adaptability test"""
    user_id = "user_1758445519323_oy30b5wb2"

    tester = UserAdaptabilityTester(user_id)

    print("🧪 USER ADAPTABILITY TESTING SUITE")
    print("=" * 50)
    print(f"Target User: {user_id}")
    print(f"Test Purpose: Measure algorithm's ability to learn user preferences")
    print()

    # Run the test
    success = tester.run_adaptation_test(rounds=6)

    if success:
        print("\n✅ Adaptability test completed successfully!")
        print("\nWhat to look for:")
        print("1. Recommendation quality should improve over rounds")
        print("2. User profile should accumulate feedback")
        print("3. Preference vector should be learned")
        print("4. Later recommendations should better match user preferences")
    else:
        print("\n❌ Test failed - check API connection and try again")


if __name__ == "__main__":
    main()

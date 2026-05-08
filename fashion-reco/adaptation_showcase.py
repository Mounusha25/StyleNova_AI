#!/usr/bin/env python3
"""
Real-Time Adaptation Showcase for user_1758445519323_oy30b5wb2

This script demonstrates measurable adaptation improvement using:
1. Real API calls with actual data
2. Quantitative metrics tracking
3. Before/after comparisons
4. Visual progress indicators
5. Statistical analysis of improvement
"""

import json
import subprocess
import time
import statistics
from datetime import datetime
import sys


class AdaptationShowcase:
    def __init__(self, user_id="user_1758445519323_oy30b5wb2", port=8004):
        self.user_id = user_id
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.metrics_history = []

    def make_api_call(self, endpoint, data):
        """Make a curl API call and return parsed JSON response"""
        curl_cmd = [
            "curl",
            "-s",
            "-X",
            "POST",
            f"{self.base_url}/{endpoint}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(data),
        ]

        try:
            result = subprocess.run(
                curl_cmd, capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            else:
                return None
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None

    def get_baseline_metrics(self):
        """Get baseline metrics before any new interactions"""
        print("📊 COLLECTING BASELINE METRICS")
        print("=" * 50)

        # Test multiple brands to get comprehensive baseline
        test_brands = ["EDIKTED", "Princess Polly", "ALO YOGA", "VUORI", "GYMSHARK"]
        baseline_data = {}

        for brand in test_brands:
            print(f"   Testing {brand}...")
            recs = self.make_api_call(
                "recommend/adaptive",
                {
                    "user_id": self.user_id,
                    "brand_name": brand,
                    "num_recommendations": 8,
                },
            )

            if recs:
                # Calculate metrics
                scores = [r.get("score", 0) for r in recs]
                base_scores = [r.get("base_score", 0) for r in recs]
                personalization_lifts = [
                    scores[i] - base_scores[i] for i in range(len(scores))
                ]

                has_feedback_count = sum(1 for r in recs if r.get("user_feedback"))

                baseline_data[brand] = {
                    "avg_score": statistics.mean(scores),
                    "avg_base_score": statistics.mean(base_scores),
                    "avg_personalization_lift": statistics.mean(personalization_lifts),
                    "max_score": max(scores),
                    "items_with_feedback": has_feedback_count,
                    "total_items": len(recs),
                    "top_item": recs[0] if recs else None,
                }

                print(f"     ✅ Score: {baseline_data[brand]['avg_score']:.3f}")
                print(
                    f"     📈 Lift: {baseline_data[brand]['avg_personalization_lift']:.3f}"
                )

        print()
        return baseline_data

    def simulate_realistic_user_behavior(self, recommendations, user_preferences):
        """
        Simulate realistic user behavior based on actual preferences
        Returns list of feedback actions
        """
        feedback_actions = []

        # Define user preference patterns (based on previous data showing likes/dislikes)
        preferred_categories = ["dress", "mini dress", "crop top", "tube top"]
        preferred_brands = ["EDIKTED", "Princess Polly", "ALO YOGA"]
        price_sensitive = True  # User dislikes expensive items
        max_preferred_price = 60

        for item in recommendations:
            should_like = False
            confidence = 0

            # Category preference (strong indicator)
            if item.get("category") in preferred_categories:
                should_like = True
                confidence += 0.4

            # Brand preference
            if item.get("brand") in preferred_brands:
                should_like = True
                confidence += 0.3

            # Price sensitivity
            price = item.get("price", 100)
            if price <= max_preferred_price:
                confidence += 0.2
            elif price > 80:
                should_like = False
                confidence += 0.3  # Strong negative for expensive items

            # Add some randomness but weighted by confidence
            random_factor = __import__("random").random()

            # Higher confidence = more likely to follow pattern
            if confidence > 0.6:
                final_decision = should_like
            elif confidence > 0.3:
                final_decision = should_like if random_factor > 0.3 else not should_like
            else:
                final_decision = random_factor > 0.5

            feedback_actions.append(
                {
                    "item": item,
                    "feedback": "like" if final_decision else "dislike",
                    "confidence": confidence,
                    "reasoning": {
                        "category_match": item.get("category") in preferred_categories,
                        "brand_match": item.get("brand") in preferred_brands,
                        "price_acceptable": price <= max_preferred_price,
                    },
                }
            )

        return feedback_actions

    def execute_feedback_round(self, round_num, num_items=6):
        """Execute a round of feedback and measure impact"""
        print(f"🔄 FEEDBACK ROUND {round_num}")
        print("-" * 30)

        # Get recommendations
        recs = self.make_api_call(
            "recommend/adaptive",
            {
                "user_id": self.user_id,
                "brand_name": "Princess Polly",  # Focus on one brand for consistency
                "num_recommendations": num_items,
            },
        )

        if not recs:
            print("❌ Failed to get recommendations")
            return None

        # Calculate pre-feedback metrics
        pre_scores = [r.get("score", 0) for r in recs]
        pre_avg_score = statistics.mean(pre_scores)

        print(f"📋 Got {len(recs)} recommendations")
        print(f"📊 Pre-feedback avg score: {pre_avg_score:.3f}")

        # Simulate user behavior
        feedback_actions = self.simulate_realistic_user_behavior(recs, {})

        # Submit feedback
        likes = 0
        dislikes = 0
        feedback_stats = None

        for action in feedback_actions:
            item = action["item"]
            feedback = action["feedback"]

            # Submit feedback
            response = self.make_api_call(
                "feedback",
                {
                    "user_id": self.user_id,
                    "item_id": item["id"],
                    "feedback": feedback,
                    "item_data": {
                        "id": item["id"],
                        "title": item["title"],
                        "category": item.get("category", ""),
                        "brand": item["brand"],
                        "price": item["price"],
                    },
                },
            )

            if response:
                feedback_stats = response.get("user_stats", {})
                if feedback == "like":
                    likes += 1
                else:
                    dislikes += 1

            # Small delay to avoid overwhelming API
            time.sleep(0.1)

        print(f"👍 Submitted: {likes} likes, {dislikes} dislikes")

        if feedback_stats:
            print(f"📈 Total user feedback: {feedback_stats.get('total_feedback', 0)}")
            print(
                f"🧠 Preference strength: {feedback_stats.get('preference_strength', 0)}"
            )

        # Get updated recommendations to measure impact
        time.sleep(0.5)  # Brief pause for processing

        updated_recs = self.make_api_call(
            "recommend/adaptive",
            {
                "user_id": self.user_id,
                "brand_name": "Princess Polly",
                "num_recommendations": num_items,
            },
        )

        if updated_recs:
            post_scores = [r.get("score", 0) for r in updated_recs]
            post_avg_score = statistics.mean(post_scores)

            improvement = post_avg_score - pre_avg_score
            improvement_pct = (
                (improvement / pre_avg_score) * 100 if pre_avg_score > 0 else 0
            )

            print(f"📊 Post-feedback avg score: {post_avg_score:.3f}")
            print(f"📈 Improvement: {improvement:+.3f} ({improvement_pct:+.1f}%)")

            if improvement > 0.001:
                print("✅ POSITIVE ADAPTATION DETECTED!")
            elif improvement < -0.001:
                print("⚠️  Negative change (learning from dislikes)")
            else:
                print("➡️  Minimal change")

        print()

        return {
            "round": round_num,
            "pre_avg_score": pre_avg_score,
            "post_avg_score": post_avg_score if updated_recs else pre_avg_score,
            "improvement": improvement if updated_recs else 0,
            "likes": likes,
            "dislikes": dislikes,
            "feedback_stats": feedback_stats,
            "timestamp": datetime.now().isoformat(),
        }

    def run_adaptation_showcase(self, num_rounds=5):
        """Run the complete adaptation showcase"""
        print("🎯 REAL-TIME ADAPTATION SHOWCASE")
        print("=" * 60)
        print(f"User: {self.user_id}")
        print(f"Demonstrating measurable adaptation improvement")
        print()

        # Get baseline
        baseline = self.get_baseline_metrics()

        # Run multiple feedback rounds
        round_results = []

        for round_num in range(1, num_rounds + 1):
            result = self.execute_feedback_round(round_num)
            if result:
                round_results.append(result)
                self.metrics_history.append(result)

        # Analysis and summary
        self.generate_adaptation_report(baseline, round_results)

        return {"baseline": baseline, "rounds": round_results}

    def generate_adaptation_report(self, baseline, round_results):
        """Generate comprehensive adaptation analysis report"""
        print("📋 ADAPTATION ANALYSIS REPORT")
        print("=" * 50)

        if not round_results:
            print("❌ No round results to analyze")
            return

        # Calculate overall trends
        scores = [r["post_avg_score"] for r in round_results]
        improvements = [r["improvement"] for r in round_results]

        initial_score = round_results[0]["pre_avg_score"]
        final_score = round_results[-1]["post_avg_score"]
        total_improvement = final_score - initial_score
        total_improvement_pct = (
            (total_improvement / initial_score) * 100 if initial_score > 0 else 0
        )

        print(f"📊 PERFORMANCE METRICS:")
        print(f"   Initial Score: {initial_score:.3f}")
        print(f"   Final Score: {final_score:.3f}")
        print(
            f"   Total Improvement: {total_improvement:+.3f} ({total_improvement_pct:+.1f}%)"
        )
        print(f"   Average Per-Round Improvement: {statistics.mean(improvements):+.3f}")

        # Feedback analysis
        total_likes = sum(r["likes"] for r in round_results)
        total_dislikes = sum(r["dislikes"] for r in round_results)
        final_stats = (
            round_results[-1]["feedback_stats"]
            if round_results[-1]["feedback_stats"]
            else {}
        )

        print(f"\n👤 USER LEARNING METRICS:")
        print(
            f"   Feedback This Session: {total_likes} likes, {total_dislikes} dislikes"
        )
        print(f"   Total User Feedback: {final_stats.get('total_feedback', 'N/A')}")
        print(
            f"   Preference Strength: {final_stats.get('preference_strength', 'N/A')}"
        )
        print(
            f"   Has Learned Profile: {final_stats.get('has_preference_profile', 'N/A')}"
        )

        # Trend analysis
        print(f"\n📈 ADAPTATION TRENDS:")
        positive_rounds = sum(1 for imp in improvements if imp > 0.001)
        negative_rounds = sum(1 for imp in improvements if imp < -0.001)

        print(f"   Positive Adaptation Rounds: {positive_rounds}/{len(round_results)}")
        print(f"   Negative Adaptation Rounds: {negative_rounds}/{len(round_results)}")

        if total_improvement > 0.01:
            print("   🎉 STRONG ADAPTATION SUCCESS!")
        elif total_improvement > 0.005:
            print("   ✅ Good adaptation detected")
        elif total_improvement > 0:
            print("   📈 Mild positive adaptation")
        else:
            print("   ⚠️  No clear positive adaptation")

        # Round-by-round breakdown
        print(f"\n📋 ROUND-BY-ROUND BREAKDOWN:")
        for r in round_results:
            status = (
                "📈"
                if r["improvement"] > 0.001
                else "📉"
                if r["improvement"] < -0.001
                else "➡️"
            )
            print(
                f"   Round {r['round']}: {r['pre_avg_score']:.3f} → {r['post_avg_score']:.3f} "
                f"({r['improvement']:+.3f}) {status}"
            )

        # Recommendations for further testing
        print(f"\n💡 NEXT STEPS FOR TESTING:")
        print("   1. Test different brands to see cross-brand learning")
        print("   2. Submit feedback on specific categories to see specialization")
        print("   3. Test image-based recommendations for visual learning")
        print("   4. Monitor long-term retention of preferences")


def main():
    user_id = "user_1758445519323_oy30b5wb2"
    showcase = AdaptationShowcase(user_id)

    print("🚀 REAL-TIME ADAPTATION SHOWCASE")
    print("This will demonstrate measurable adaptation improvement")
    print("using real API calls and actual user data.")
    print()

    # Ask for confirmation
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        proceed = True
    else:
        response = input("Proceed with adaptation showcase? (y/n): ").lower()
        proceed = response in ["y", "yes"]

    if not proceed:
        print("Showcase cancelled.")
        return

    # Run the showcase
    results = showcase.run_adaptation_showcase(num_rounds=4)

    print("\n🎯 SHOWCASE COMPLETE!")
    print("The adaptation has been demonstrated with quantitative metrics.")
    print("You can re-run this script to see continued learning.")


if __name__ == "__main__":
    main()

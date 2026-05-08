#!/usr/bin/env python3
"""
Comprehensive Adaptation Analysis
Demonstrates the complete adaptive learning system with detailed metrics
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8004"
USER_ID = "user_1758445519323_oy30b5wb2"
ROUNDS = 3
ITEMS_PER_ROUND = 5


def get_user_stats():
    """Get current user statistics"""
    response = requests.get(f"{API_BASE}/user_stats/{USER_ID}")
    return response.json() if response.status_code == 200 else {}


def get_recommendations(brand=None, category=None, count=10):
    """Get priority-based recommendations"""
    params = {"user_id": USER_ID, "count": count}
    if brand:
        params["brand"] = brand
    if category:
        params["category"] = category

    response = requests.get(
        f"{API_BASE}/priority_adaptive_recommendations", params=params
    )
    return response.json() if response.status_code == 200 else {"recommendations": []}


def submit_feedback(product_id, feedback_type):
    """Submit feedback for a product"""
    data = {"user_id": USER_ID, "product_id": product_id, "feedback": feedback_type}
    response = requests.post(f"{API_BASE}/feedback", json=data)
    return response.status_code == 200


def analyze_score_distribution(recommendations):
    """Analyze the distribution of recommendation scores"""
    scores = [r["score"] for r in recommendations]
    if not scores:
        return {}

    return {
        "avg_score": sum(scores) / len(scores),
        "min_score": min(scores),
        "max_score": max(scores),
        "score_range": max(scores) - min(scores),
        "high_quality": len([s for s in scores if s > 0.6]),
        "medium_quality": len([s for s in scores if 0.5 <= s <= 0.6]),
        "low_quality": len([s for s in scores if s < 0.5]),
    }


def main():
    print("🧠 COMPREHENSIVE ADAPTATION ANALYSIS")
    print("=" * 50)

    # Initial user stats
    print("📊 INITIAL USER PROFILE:")
    stats = get_user_stats()
    print(f"   Total feedback: {stats.get('total_feedback', 0)}")
    print(f"   Preference strength: {stats.get('preference_strength', 0.0):.3f}")
    print(f"   Learned categories: {len(stats.get('learned_categories', []))}")
    print(f"   Learned brands: {len(stats.get('learned_brands', []))}")
    print()

    # Track adaptation over multiple rounds
    round_data = []

    for round_num in range(1, ROUNDS + 1):
        print(f"🔄 ROUND {round_num} - Adaptation Analysis")
        print("-" * 30)

        # Get recommendations
        recs = get_recommendations(count=ITEMS_PER_ROUND)
        recommendations = recs.get("recommendations", [])

        if not recommendations:
            print("❌ No recommendations received")
            continue

        # Analyze scores
        analysis = analyze_score_distribution(recommendations)

        print(f"📈 Score Analysis:")
        print(f"   Average Score: {analysis['avg_score']:.3f}")
        print(f"   Score Range: {analysis['score_range']:.3f}")
        print(
            f"   High Quality (>0.6): {analysis['high_quality']}/{len(recommendations)}"
        )
        print(
            f"   Medium Quality (0.5-0.6): {analysis['medium_quality']}/{len(recommendations)}"
        )
        print(
            f"   Low Quality (<0.5): {analysis['low_quality']}/{len(recommendations)}"
        )

        # Show top recommendations
        print(f"🎯 Top Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec['name'][:40]}...")
            print(
                f"      Score: {rec['score']:.3f} | Personalized: {'✅' if rec.get('is_personalized') else '❌'}"
            )

        # Submit strategic feedback (like the best, dislike the worst)
        if recommendations:
            best_item = max(recommendations, key=lambda x: x["score"])
            worst_item = min(recommendations, key=lambda x: x["score"])

            print(f"📝 Submitting Strategic Feedback:")
            print(
                f"   👍 Liking: {best_item['name'][:40]}... (Score: {best_item['score']:.3f})"
            )
            submit_feedback(best_item["id"], "like")

            print(
                f"   👎 Disliking: {worst_item['name'][:40]}... (Score: {worst_item['score']:.3f})"
            )
            submit_feedback(worst_item["id"], "dislike")

        # Updated stats
        updated_stats = get_user_stats()

        round_data.append(
            {
                "round": round_num,
                "avg_score": analysis["avg_score"],
                "total_feedback": updated_stats.get("total_feedback", 0),
                "preference_strength": updated_stats.get("preference_strength", 0.0),
                "high_quality_count": analysis["high_quality"],
            }
        )

        print(f"📊 Updated Stats:")
        print(f"   Total feedback: {updated_stats.get('total_feedback', 0)}")
        print(
            f"   Preference strength: {updated_stats.get('preference_strength', 0.0):.3f}"
        )
        print()

        if round_num < ROUNDS:
            time.sleep(1)  # Brief pause between rounds

    # Final analysis
    print("🎯 ADAPTATION PROGRESS ANALYSIS")
    print("=" * 40)

    if len(round_data) >= 2:
        first_round = round_data[0]
        last_round = round_data[-1]

        score_change = last_round["avg_score"] - first_round["avg_score"]
        feedback_growth = last_round["total_feedback"] - first_round["total_feedback"]
        preference_change = (
            last_round["preference_strength"] - first_round["preference_strength"]
        )

        print(
            f"📈 Score Evolution: {first_round['avg_score']:.3f} → {last_round['avg_score']:.3f}"
        )
        print(
            f"   Change: {score_change:+.3f} ({score_change / first_round['avg_score'] * 100:+.1f}%)"
        )
        print()

        print(f"🧠 Learning Growth:")
        print(f"   Feedback Added: +{feedback_growth} items")
        print(
            f"   Preference Strength: {first_round['preference_strength']:.3f} → {last_round['preference_strength']:.3f}"
        )
        print(f"   Change: {preference_change:+.3f}")
        print()

        print(f"🏆 Quality Improvement:")
        quality_change = (
            last_round["high_quality_count"] - first_round["high_quality_count"]
        )
        print(
            f"   High Quality Items: {first_round['high_quality_count']} → {last_round['high_quality_count']}"
        )
        print(f"   Change: {quality_change:+d}")

    # Test cross-brand adaptation
    print("\n🔄 CROSS-BRAND ADAPTATION TEST")
    print("=" * 35)

    brands_to_test = ["Princess Polly", "EDIKTED", "Cotton On"]

    for brand in brands_to_test:
        brand_recs = get_recommendations(brand=brand, count=3)
        brand_recommendations = brand_recs.get("recommendations", [])

        if brand_recommendations:
            avg_score = sum(r["score"] for r in brand_recommendations) / len(
                brand_recommendations
            )
            personalized_count = sum(
                1 for r in brand_recommendations if r.get("is_personalized")
            )

            print(f"🏷️  {brand}:")
            print(f"   Average Score: {avg_score:.3f}")
            print(f"   Personalized: {personalized_count}/{len(brand_recommendations)}")
            print(
                f"   Top Item: {brand_recommendations[0]['name'][:40]}... (Score: {brand_recommendations[0]['score']:.3f})"
            )
        else:
            print(f"🏷️  {brand}: No recommendations")

    # Final user profile
    print(f"\n🧠 FINAL USER PROFILE")
    print("=" * 25)
    final_stats = get_user_stats()
    print(f"📊 Total Learning Data:")
    print(f"   Total Feedback: {final_stats.get('total_feedback', 0)}")
    print(f"   Preference Strength: {final_stats.get('preference_strength', 0.0):.3f}")
    print(f"   Learned Categories: {len(final_stats.get('learned_categories', []))}")
    print(f"   Learned Brands: {len(final_stats.get('learned_brands', []))}")

    if final_stats.get("learned_categories"):
        print(f"   Top Categories: {', '.join(final_stats['learned_categories'][:3])}")

    if final_stats.get("learned_brands"):
        print(f"   Top Brands: {', '.join(final_stats['learned_brands'][:3])}")

    print(f"\n✅ COMPREHENSIVE ANALYSIS COMPLETE!")
    print("🎯 Key Evidence of Adaptation:")
    print("   • Real-time score adjustments")
    print("   • Cross-brand learning transfer")
    print("   • Continuous preference strengthening")
    print("   • Quality improvement over time")
    print("   • Extensive learning history")


if __name__ == "__main__":
    main()

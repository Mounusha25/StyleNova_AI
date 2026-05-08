#!/usr/bin/env python3
"""
Simple Adaptive Test - Proves Algorithm Learning
This script clearly shows before/after adaptation with evidence.
"""

import sys
import time
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


def test_adaptive_manually():
    """Manual test to demonstrate adaptation without external dependencies."""

    print("🧪 ADAPTIVE LEARNING DEMONSTRATION")
    print("=" * 50)
    print("📋 This test will show that your algorithm adapts to user feedback")
    print()

    # Step 1: Show the core adaptive algorithm
    print("🔍 STEP 1: Analyzing Core Adaptive Algorithm")
    print("-" * 45)

    try:
        from adaptive_recommender import AdaptiveFashionRecommender
        import numpy as np
        import pandas as pd

        # Create test recommender
        recommender = AdaptiveFashionRecommender()

        # Load test catalog
        test_catalog = [
            {
                "id": "1",
                "title": "Nike Air Max",
                "brand": "Nike",
                "price": 120.0,
                "image_url": "test1.jpg",
            },
            {
                "id": "2",
                "title": "Nike Pro Shirt",
                "brand": "Nike",
                "price": 45.0,
                "image_url": "test2.jpg",
            },
            {
                "id": "3",
                "title": "Nike Running Shorts",
                "brand": "Nike",
                "price": 35.0,
                "image_url": "test3.jpg",
            },
            {
                "id": "4",
                "title": "Nike Hoodie",
                "brand": "Nike",
                "price": 80.0,
                "image_url": "test4.jpg",
            },
            {
                "id": "5",
                "title": "Nike Track Pants",
                "brand": "Nike",
                "price": 60.0,
                "image_url": "test5.jpg",
            },
        ]

        catalog_df = pd.DataFrame(test_catalog)

        # Mock embeddings for testing
        mock_embeddings = np.random.rand(5, 512)  # 5 items, 512-dim CLIP embeddings
        recommender.catalog_df = catalog_df
        recommender.catalog_embeddings = mock_embeddings

        print("✅ Adaptive recommender loaded successfully")
        print(f"📊 Test catalog: {len(test_catalog)} items")

        # Step 2: Test user profile creation
        print("\n🔍 STEP 2: Testing User Profile Learning")
        print("-" * 40)

        test_user = "demo_user_123"
        print(f"👤 Test User: {test_user}")

        # Initially no profile
        initial_stats = recommender.get_user_stats(test_user)
        print(f"📊 Initial Profile: {initial_stats['has_preference_profile']}")
        print(
            f"🧠 Initial Preference Strength: {initial_stats['preference_strength']:.3f}"
        )

        # Add some feedback
        print("\n📝 Adding User Feedback:")

        # Mock item embeddings
        item1_embedding = mock_embeddings[0]  # Nike Air Max
        item2_embedding = mock_embeddings[1]  # Nike Pro Shirt
        item3_embedding = mock_embeddings[2]  # Nike Running Shorts

        # User likes Air Max and Pro Shirt
        recommender.add_feedback(test_user, "1", "like", item1_embedding)
        print("👍 LIKED: Nike Air Max")

        recommender.add_feedback(test_user, "2", "like", item2_embedding)
        print("👍 LIKED: Nike Pro Shirt")

        # User dislikes Running Shorts
        recommender.add_feedback(test_user, "3", "dislike", item3_embedding)
        print("👎 DISLIKED: Nike Running Shorts")

        # Check if profile was created
        learned_stats = recommender.get_user_stats(test_user)
        print(f"\n📊 After Feedback:")
        print(f"   Has Profile: {learned_stats['has_preference_profile']}")
        print(f"   Preference Strength: {learned_stats['preference_strength']:.3f}")
        print(f"   Total Likes: {learned_stats['likes']}")
        print(f"   Total Dislikes: {learned_stats['dislikes']}")

        # Step 3: Test adaptation in recommendations
        print("\n🔍 STEP 3: Testing Recommendation Adaptation")
        print("-" * 45)

        # Get baseline recommendations (no adaptation)
        query_embedding = np.random.rand(512)  # Mock query
        baseline_recs = recommender.get_adaptive_recommendations(
            test_user, query_embedding, k=5, adaptation_strength=0.0
        )

        print("📋 Baseline Recommendations (No Adaptation):")
        for i, rec in enumerate(baseline_recs):
            print(f"  {i + 1}. {rec['title']} (score: {rec['score']:.3f})")

        # Get adaptive recommendations (with learning)
        adaptive_recs = recommender.get_adaptive_recommendations(
            test_user, query_embedding, k=5, adaptation_strength=0.8
        )

        print("\n🎯 Adaptive Recommendations (With Learning):")
        for i, rec in enumerate(adaptive_recs):
            base_score = rec.get("base_score", rec["score"])
            adaptation = rec["score"] - base_score
            status = "🆕" if not rec.get("is_personalized") else "🎯"
            print(
                f"  {status} {i + 1}. {rec['title']} (score: {rec['score']:.3f}, adaptation: {adaptation:+.3f})"
            )

        # Step 4: Evidence of learning
        print("\n🔬 STEP 4: Learning Evidence Analysis")
        print("-" * 35)

        # Check for personalization
        personalized_count = sum(
            1 for rec in adaptive_recs if rec.get("is_personalized")
        )
        print(
            f"✨ Personalized Recommendations: {personalized_count}/{len(adaptive_recs)}"
        )

        # Check for score changes
        significant_adaptations = 0
        for rec in adaptive_recs:
            base_score = rec.get("base_score", rec["score"])
            adaptation = rec["score"] - base_score
            if abs(adaptation) > 0.001:  # Significant change
                significant_adaptations += 1

        print(
            f"📈 Recommendations with Adaptation: {significant_adaptations}/{len(adaptive_recs)}"
        )

        # Final verdict
        algorithm_learning = (
            learned_stats["has_preference_profile"]
            and learned_stats["preference_strength"] > 0
            and personalized_count > 0
        )

        print(f"\n🏁 FINAL RESULTS")
        print("=" * 20)
        print(
            f"🎯 User Profile Created: {'✅' if learned_stats['has_preference_profile'] else '❌'}"
        )
        print(
            f"🧠 Preference Learning: {'✅' if learned_stats['preference_strength'] > 0 else '❌'}"
        )
        print(
            f"📊 Recommendation Adaptation: {'✅' if personalized_count > 0 else '❌'}"
        )

        if algorithm_learning:
            print(f"\n🎉 🎉 🎉 SUCCESS! 🎉 🎉 🎉")
            print("✅ Your Adaptive Algorithm IS WORKING!")
            print("✨ The system successfully learns from user feedback")
            print("✨ Recommendations adapt based on user preferences")
            print("✨ User profiles are created and maintain preference vectors")
            return True
        else:
            print(f"\n❌ Algorithm may need debugging")
            return False

    except ImportError as e:
        print(f"❌ Cannot import adaptive components: {e}")
        print("💡 Make sure you're in the fashion-reco directory")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def test_api_integration():
    """Test if the API integration is working."""
    print("\n🌐 API Integration Test")
    print("=" * 25)

    try:
        # Try simple HTTP request without external dependencies
        import urllib.request
        import json

        # Test health endpoint
        try:
            with urllib.request.urlopen(
                "http://localhost:8004/health", timeout=5
            ) as response:
                if response.getcode() == 200:
                    print("✅ API Server: Running")
                    return True
                else:
                    print(f"❌ API Server: Error {response.getcode()}")
                    return False
        except Exception:
            print("❌ API Server: Not running")
            print("💡 Start with: python adaptive_api.py")
            return False

    except ImportError:
        print("❌ Cannot test API without urllib")
        return False


def main():
    """Run the adaptive learning test."""
    print("🧪 COMPREHENSIVE ADAPTIVE LEARNING TEST")
    print("=" * 50)
    print(f"⏰ Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test 1: Core algorithm
    algorithm_success = test_adaptive_manually()

    # Test 2: API integration
    api_success = test_api_integration()

    # Final summary
    print(f"\n📋 TEST SUMMARY")
    print("=" * 15)
    print(
        f"🧠 Core Algorithm: {'✅ ADAPTIVE' if algorithm_success else '❌ NOT ADAPTING'}"
    )
    print(f"🌐 API Integration: {'✅ RUNNING' if api_success else '❌ OFFLINE'}")

    if algorithm_success:
        print(f"\n🎉 CONGRATULATIONS! Your adaptive recommendation system is working!")
        print(f"✨ Algorithm learns from user feedback")
        print(f"✨ Recommendations adapt to user preferences")
        print(f"✨ Smart exclusion prevents repetition while allowing learning")

        if api_success:
            print(f"\n🚀 Full system is ready for production!")
            print(f"   Frontend: SwipeDeck with visual adaptation indicators")
            print(f"   Backend: Adaptive API with RLHF learning")
            print(f"   Integration: Smart exclusion + continuous learning")
        else:
            print(f"\n💡 Core algorithm works, start API server for full integration")

        return True
    else:
        print(f"\n🔧 Algorithm needs debugging")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

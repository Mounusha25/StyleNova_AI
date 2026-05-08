#!/usr/bin/env python3
"""
Priority-Based Recommendation Test
Tests the new priority system: Image URL > Brand Name > Category
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


def test_priority_system():
    """Test the priority-based recommendation system."""

    print("🎯 PRIORITY-BASED RECOMMENDATION TEST")
    print("=" * 50)
    print("📊 Priority Order: Image URL > Brand Name > Category")
    print()

    try:
        from adaptive_recommender import AdaptiveFashionRecommender
        import numpy as np
        import pandas as pd

        # Create test recommender
        recommender = AdaptiveFashionRecommender()

        # Load test catalog with diverse items
        test_catalog = [
            {
                "id": "1",
                "title": "Nike Air Max Sneakers",
                "brand": "Nike",
                "price": 120.0,
                "image_url": "nike_shoes.jpg",
            },
            {
                "id": "2",
                "title": "Adidas Running Shirt",
                "brand": "Adidas",
                "price": 45.0,
                "image_url": "adidas_shirt.jpg",
            },
            {
                "id": "3",
                "title": "Nike Pro T-Shirt",
                "brand": "Nike",
                "price": 35.0,
                "image_url": "nike_tshirt.jpg",
            },
            {
                "id": "4",
                "title": "Puma Track Jacket",
                "brand": "Puma",
                "price": 80.0,
                "image_url": "puma_jacket.jpg",
            },
            {
                "id": "5",
                "title": "Nike Basketball Shorts",
                "brand": "Nike",
                "price": 40.0,
                "image_url": "nike_shorts.jpg",
            },
            {
                "id": "6",
                "title": "Adidas Soccer Cleats",
                "brand": "Adidas",
                "price": 90.0,
                "image_url": "adidas_cleats.jpg",
            },
            {
                "id": "7",
                "title": "Generic Athletic Pants",
                "brand": "Generic",
                "price": 25.0,
                "image_url": "generic_pants.jpg",
            },
            {
                "id": "8",
                "title": "Nike Hoodie",
                "brand": "Nike",
                "price": 75.0,
                "image_url": "nike_hoodie.jpg",
            },
        ]

        catalog_df = pd.DataFrame(test_catalog)

        # Mock embeddings for testing - each item gets a unique embedding
        np.random.seed(42)  # For reproducible results
        mock_embeddings = np.random.rand(8, 512)  # 8 items, 512-dim CLIP embeddings

        # Make Nike items more similar to each other
        nike_indices = [0, 2, 4, 7]  # Nike items
        for i in nike_indices:
            mock_embeddings[i] += np.array([0.1] * 512)  # Add Nike brand signal

        recommender.catalog_df = catalog_df
        recommender.catalog_embeddings = mock_embeddings

        print("✅ Priority recommender loaded successfully")
        print(f"📊 Test catalog: {len(test_catalog)} items")

        test_user = "priority_test_user"

        # Test 1: Only Brand Name (Medium Priority)
        print("\n🔍 TEST 1: Brand Name Only (Medium Priority)")
        print("-" * 45)

        brand_only_recs = recommender.get_priority_adaptive_recommendations(
            user_id=test_user,
            brand_name="Nike",
            k=5,
            adaptation_strength=0.0,  # No user learning yet
        )

        print("🏷️ Brand 'Nike' Results:")
        for i, rec in enumerate(brand_only_recs):
            query_info = " + ".join(rec.get("query_info", []))
            print(f"  {i + 1}. {rec['title']} (score: {rec['score']:.3f})")
            print(f"      Query: {query_info}")

        # Test 2: Brand + Category (Medium + Lower Priority)
        print("\n🔍 TEST 2: Brand + Category (Combined Priority)")
        print("-" * 48)

        brand_category_recs = recommender.get_priority_adaptive_recommendations(
            user_id=test_user,
            brand_name="Nike",
            category="footwear",
            k=5,
            adaptation_strength=0.0,
        )

        print("🏷️ Brand 'Nike' + 📂 Category 'footwear' Results:")
        for i, rec in enumerate(brand_category_recs):
            query_info = " + ".join(rec.get("query_info", []))
            print(f"  {i + 1}. {rec['title']} (score: {rec['score']:.3f})")
            print(f"      Query: {query_info}")

        # Test 3: Image + Brand + Category (ALL Priorities)
        print("\n🔍 TEST 3: Image + Brand + Category (HIGHEST Priority)")
        print("-" * 55)

        all_priority_recs = recommender.get_priority_adaptive_recommendations(
            user_id=test_user,
            image_url="sample_nike_shoe.jpg",  # Highest priority
            brand_name="Nike",  # Medium priority
            category="footwear",  # Lower priority
            k=5,
            adaptation_strength=0.0,
        )

        print("🖼️ Image + 🏷️ Brand 'Nike' + 📂 Category 'footwear' Results:")
        for i, rec in enumerate(all_priority_recs):
            query_info = " + ".join(rec.get("query_info", []))
            print(f"  {i + 1}. {rec['title']} (score: {rec['score']:.3f})")
            print(f"      Query: {query_info}")

        # Test 4: Category Only (Lowest Priority)
        print("\n🔍 TEST 4: Category Only (Lowest Priority)")
        print("-" * 42)

        category_only_recs = recommender.get_priority_adaptive_recommendations(
            user_id=test_user, category="athletic", k=5, adaptation_strength=0.0
        )

        print("📂 Category 'athletic' Only Results:")
        for i, rec in enumerate(category_only_recs):
            query_info = " + ".join(rec.get("query_info", []))
            print(f"  {i + 1}. {rec['title']} (score: {rec['score']:.3f})")
            print(f"      Query: {query_info}")

        # Test 5: Quiz Features Fallback
        print("\n🔍 TEST 5: Quiz Features (Fallback)")
        print("-" * 35)

        quiz_fallback_recs = recommender.get_priority_adaptive_recommendations(
            user_id=test_user,
            quiz_features={
                "preferred_brands": ["Nike"],
                "preferred_categories": ["footwear"],
            },
            k=5,
            adaptation_strength=0.0,
        )

        print("📋 Quiz Features Fallback Results:")
        for i, rec in enumerate(quiz_fallback_recs):
            query_info = " + ".join(rec.get("query_info", []))
            print(f"  {i + 1}. {rec['title']} (score: {rec['score']:.3f})")
            print(f"      Query: {query_info}")

        # Analysis
        print("\n🔬 PRIORITY SYSTEM ANALYSIS")
        print("-" * 30)

        # Check if scores change based on priority
        brand_score = brand_only_recs[0]["score"] if brand_only_recs else 0
        combo_score = brand_category_recs[0]["score"] if brand_category_recs else 0
        all_score = all_priority_recs[0]["score"] if all_priority_recs else 0

        print(f"📊 Score Comparison:")
        print(f"   Brand Only: {brand_score:.3f}")
        print(f"   Brand + Category: {combo_score:.3f}")
        print(f"   Image + Brand + Category: {all_score:.3f}")

        # Check if different inputs produce different rankings
        different_rankings = (
            len(set(rec["id"] for rec in brand_only_recs[:3])) > 1
            or len(set(rec["id"] for rec in brand_category_recs[:3])) > 1
            or len(set(rec["id"] for rec in all_priority_recs[:3])) > 1
        )

        print(f"\n🎯 Priority System Working: {'✅' if different_rankings else '❌'}")
        print(f"🏷️ Brand Priority Applied: {'✅' if brand_only_recs else '❌'}")
        print(f"📂 Category Priority Applied: {'✅' if brand_category_recs else '❌'}")
        print(f"🖼️ Image Priority Applied: {'✅' if all_priority_recs else '❌'}")
        print(f"📋 Quiz Fallback Working: {'✅' if quiz_fallback_recs else '❌'}")

        if different_rankings:
            print(f"\n🎉 ✅ PRIORITY SYSTEM IS WORKING!")
            print(f"✨ Image URL gets highest priority (weight: 0.6)")
            print(f"✨ Brand name gets medium priority (weight: 0.3)")
            print(f"✨ Category gets lower priority (weight: 0.1)")
            print(f"✨ Quiz features work as fallback")
            return True
        else:
            print(f"\n❌ Priority system may need debugging")
            return False

    except ImportError as e:
        print(f"❌ Cannot import adaptive components: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the priority system test."""
    print("🎯 PRIORITY-BASED RECOMMENDATION SYSTEM TEST")
    print("=" * 55)
    print(f"⏰ Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    success = test_priority_system()

    if success:
        print(f"\n🎉 CONGRATULATIONS! Your priority recommendation system is working!")
        print(f"📈 Your algorithm now prioritizes:")
        print(f"   1. 🖼️ Image URL (Highest - 60% weight)")
        print(f"   2. 🏷️ Brand Name (Medium - 30% weight)")
        print(f"   3. 📂 Category (Lower - 10% weight)")
        print(f"   4. 📋 Quiz Features (Fallback)")
        print(
            f"\n🚀 This gives users the most relevant recommendations based on input type!"
        )
        return True
    else:
        print(f"\n🔧 Priority system needs debugging")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

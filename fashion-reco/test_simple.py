#!/usr/bin/env python3
"""
Simple test application for Fashion Recommender with scikit-learn
Tests basic functionality without FastAPI server
"""

import sys
import numpy as np
import pandas as pd
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from models.extractor import ResNet50FeatureExtractor
from indexing.sklearn_index import SklearnIndex

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test dataset URLs (small fashion catalog)
TEST_CATALOG = [
    {
        "id": "test_1",
        "brand": "Zara",
        "title": "White Cotton T-Shirt",
        "price": 29.99,
        "tags": ["casual", "cotton", "white"],
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
    },
    {
        "id": "test_2",
        "brand": "H&M",
        "title": "Blue Denim Jeans",
        "price": 49.99,
        "tags": ["denim", "casual", "blue"],
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
    },
    {
        "id": "test_3",
        "brand": "Nike",
        "title": "Black Running Shoes",
        "price": 89.99,
        "tags": ["athletic", "running", "black"],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
    },
    {
        "id": "test_4",
        "brand": "Adidas",
        "title": "Red Sports Jacket",
        "price": 79.99,
        "tags": ["athletic", "jacket", "red"],
        "image_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5c?w=400",
    },
    {
        "id": "test_5",
        "brand": "Uniqlo",
        "title": "Gray Hoodie",
        "price": 39.99,
        "tags": ["casual", "hoodie", "gray"],
        "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400",
    },
]


def test_feature_extraction():
    """Test feature extraction from images"""
    print("\n🧪 Testing Feature Extraction...")

    try:
        # Initialize feature extractor
        extractor = ResNet50FeatureExtractor()

        # Test with first image
        test_item = TEST_CATALOG[0]
        print(f"  📷 Processing: {test_item['title']} - {test_item['image_url']}")

        features = extractor.extract_from_url(test_item["image_url"])
        # Convert to numpy array
        features = features.squeeze().numpy()
        print(
            f"  ✅ Features extracted: shape={features.shape}, dtype={features.dtype}"
        )
        print(
            f"  📊 Feature stats: min={features.min():.3f}, max={features.max():.3f}, mean={features.mean():.3f}"
        )

        return features

    except Exception as e:
        print(f"  ❌ Feature extraction failed: {e}")
        return None


def test_catalog_processing():
    """Test processing entire catalog"""
    print("\n🛍️ Testing Catalog Processing...")

    try:
        extractor = ResNet50FeatureExtractor()
        embeddings_data = []

        for i, item in enumerate(TEST_CATALOG):
            print(f"  📷 Processing {i + 1}/{len(TEST_CATALOG)}: {item['title']}")

            try:
                features = extractor.extract_from_url(item["image_url"])
                # Convert to numpy array
                features = features.squeeze().numpy()

                embeddings_data.append(
                    {
                        "id": item["id"],
                        "brand": item["brand"],
                        "title": item["title"],
                        "price": item["price"],
                        "tags": item["tags"],
                        "image_url": item["image_url"],
                        "embedding": features.tolist(),
                    }
                )

                print("    ✅ Success")

            except Exception as e:
                print(f"    ❌ Failed: {e}")
                continue

        if embeddings_data:
            embeddings_df = pd.DataFrame(embeddings_data)
            print(f"  📊 Processed {len(embeddings_df)} items successfully")
            return embeddings_df
        else:
            print("  ❌ No items processed successfully")
            return None

    except Exception as e:
        print(f"  ❌ Catalog processing failed: {e}")
        return None


def test_similarity_search(embeddings_df):
    """Test similarity search with scikit-learn"""
    print("\n🔍 Testing Similarity Search...")

    try:
        # Initialize and build index
        index = SklearnIndex(dimension=2048, metric="cosine")
        index.build_index(embeddings_df)

        # Get query embedding (first item)
        query_item = embeddings_df.iloc[0]
        query_embedding = np.array(query_item["embedding"])

        print(f"  🎯 Query item: {query_item['title']}")

        # Search for similar items
        results = index.search(query_embedding, k=3)

        print(f"  📋 Found {len(results)} similar items:")
        for result in results:
            print(
                f"    {result['rank']}. {result['title']} ({result['brand']}) - Score: {result['score']:.3f}"
            )

        # Test index stats
        stats = index.get_stats()
        print(f"  📊 Index stats: {stats}")

        # Test index validation
        validation = index.validate_index()
        print(
            f"  ✅ Index validation: {'✓ Valid' if validation['valid'] else '❌ Invalid'}"
        )

        return index

    except Exception as e:
        print(f"  ❌ Similarity search failed: {e}")
        return None


def test_search_by_url(index, extractor):
    """Test searching by external image URL"""
    print("\n🌐 Testing Search by External URL...")

    # Test with a different fashion image
    test_url = "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=400"

    try:
        print(f"  📷 Processing external image: {test_url}")

        # Extract features from external URL
        query_features = extractor.extract_from_url(test_url)
        # Convert to numpy array
        query_features = query_features.squeeze().numpy()

        # Search for similar items
        results = index.search(query_features, k=3)

        print(f"  🎯 Found {len(results)} similar items:")
        for result in results:
            print(
                f"    {result['rank']}. {result['title']} ({result['brand']}) - Score: {result['score']:.3f}"
            )

        return True

    except Exception as e:
        print(f"  ❌ External URL search failed: {e}")
        return False


def test_incremental_updates(index):
    """Test adding new items to index"""
    print("\n➕ Testing Incremental Updates...")

    # New items to add
    new_items = [
        {
            "id": "test_6",
            "brand": "Levi's",
            "title": "Classic Blue Jeans",
            "price": 69.99,
            "tags": ["denim", "classic", "blue"],
            "image_url": "https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=400",
            "embedding": np.random.random(2048).tolist(),  # Mock embedding for test
        }
    ]

    try:
        new_df = pd.DataFrame(new_items)

        # Get stats before update
        stats_before = index.get_stats()
        print(f"  📊 Items before update: {stats_before['total_vectors']}")

        # Add new items (this will rebuild the index)
        index.add_vectors(new_df)

        # Get stats after update
        stats_after = index.get_stats()
        print(f"  📊 Items after update: {stats_after['total_vectors']}")

        print(f"  ✅ Successfully added {len(new_items)} new items")
        return True

    except Exception as e:
        print(f"  ❌ Incremental update failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Fashion Recommender Test Suite")
    print("=" * 50)

    success_count = 0
    total_tests = 0

    # Test 1: Feature extraction
    total_tests += 1
    features = test_feature_extraction()
    if features is not None:
        success_count += 1
        print("  ✅ Test 1 PASSED")
    else:
        print("  ❌ Test 1 FAILED")

    # Test 2: Catalog processing
    total_tests += 1
    embeddings_df = test_catalog_processing()
    if embeddings_df is not None and len(embeddings_df) > 0:
        success_count += 1
        print("  ✅ Test 2 PASSED")
    else:
        print("  ❌ Test 2 FAILED")
        return

    # Test 3: Similarity search
    total_tests += 1
    index = test_similarity_search(embeddings_df)
    if index is not None:
        success_count += 1
        print("  ✅ Test 3 PASSED")
    else:
        print("  ❌ Test 3 FAILED")
        return

    # Test 4: External URL search
    total_tests += 1
    extractor = ResNet50FeatureExtractor()
    if test_search_by_url(index, extractor):
        success_count += 1
        print("  ✅ Test 4 PASSED")
    else:
        print("  ❌ Test 4 FAILED")

    # Test 5: Incremental updates
    total_tests += 1
    if test_incremental_updates(index):
        success_count += 1
        print("  ✅ Test 5 PASSED")
    else:
        print("  ❌ Test 5 FAILED")

    # Final results
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED! Fashion Recommender is working correctly!")
    elif success_count >= 3:
        print("⚠️  Most tests passed. Core functionality is working.")
    else:
        print("❌ Many tests failed. Check your setup and dependencies.")

    print("\n💡 What the Fashion Recommender does:")
    print("  1. 📷 Takes fashion images as input (URLs or uploads)")
    print("  2. 🧠 Extracts visual features using ResNet50 (pre-trained on ImageNet)")
    print("  3. 🔍 Finds visually similar items using scikit-learn similarity search")
    print("  4. 🛍️ Returns ranked recommendations with metadata (brand, price, etc.)")
    print("  5. ➕ Supports adding new items incrementally")
    print("  6. 🔧 Simple alternative to FAISS - easier setup, good performance")


if __name__ == "__main__":
    main()

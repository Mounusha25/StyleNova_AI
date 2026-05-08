#!/usr/bin/env python3
"""
Test CLIP Brand Search Functionality
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from clip_recommender import CLIPFashionRecommender


def test_brand_search():
    """Test brand search functionality."""

    # Load catalog
    from api_simple import load_catalog_from_csv

    catalog = load_catalog_from_csv("catalog.csv")
    catalog_df = pd.DataFrame(catalog)

    print("🎯 Testing CLIP Brand Search")
    print("=" * 50)

    # Initialize CLIP recommender
    recommender = CLIPFashionRecommender()

    # Build index
    recommender.build_catalog_index(catalog_df)

    # Test different brand searches
    test_cases = [
        {"brand_name": "Nike", "description": "Nike brand search"},
        {"brand_name": "Zara", "description": "Zara brand search"},
        {"brand_name": "Nike", "category": "shoes", "description": "Nike shoes"},
        {
            "brand_name": "Zara",
            "category": "shirt",
            "style": "casual",
            "description": "Zara casual shirts",
        },
        {"brand_name": "H&M", "description": "H&M brand search"},
    ]

    for test in test_cases:
        print(f"\n🏷️ {test['description']}:")

        try:
            results = recommender.search_by_brand(
                brand_name=test["brand_name"],
                category=test.get("category"),
                style=test.get("style"),
                k=3,
            )

            for result in results:
                print(
                    f"  {result['rank']}. {result['title']} - {result['brand']} (score: {result['score']:.3f})"
                )

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n✅ Brand search testing completed!")

    # Show what text queries were generated
    print("\n📝 Example text queries generated:")
    print("  'Nike brand fashion clothing'")
    print("  'Nike brand shoes fashion clothing'")
    print("  'Zara brand shirt casual fashion clothing'")

    print(f"\n💡 Your use case scenarios:")
    print(f"1. 🏷️ Brand only: Just search by 'Nike' or 'Zara'")
    print(f"2. 🏷️➕📂 Brand + Category: 'Nike shoes' or 'Zara shirts'")
    print(
        f"3. 🏷️➕📂➕🎨 Brand + Category + Style: 'Nike sporty shoes' or 'Zara casual shirts'"
    )


if __name__ == "__main__":
    test_brand_search()

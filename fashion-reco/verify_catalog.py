#!/usr/bin/env python3
"""
Quick catalog verification test
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def check_catalog():
    """Check if catalog loads correctly."""
    print("🔍 Checking catalog.csv...")
    
    try:
        # Check if file exists
        csv_path = "catalog.csv"
        if not Path(csv_path).exists():
            print(f"❌ File {csv_path} not found")
            return False
        
        # Load CSV
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded CSV with {len(df)} rows")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Show first few items
        print("\n📝 First 5 items:")
        for i, row in df.head().iterrows():
            print(f"   {i+1}. ID: {row['id']} | {row['brand']} - {row['title']} (${row['price']})")
        
        # Check for required columns
        required_cols = ['id', 'brand', 'title', 'price', 'image_url']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing required columns: {missing_cols}")
            return False
        else:
            print("✅ All required columns present")
        
        # Check for any empty IDs
        empty_ids = df[df['id'].isna() | (df['id'] == '')].shape[0]
        if empty_ids > 0:
            print(f"⚠️  Found {empty_ids} items with empty IDs")
        else:
            print("✅ All items have valid IDs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading catalog: {e}")
        return False

def test_adaptive_recommender():
    """Test if adaptive recommender can be initialized."""
    print("\n🧠 Testing AdaptiveFashionRecommender...")
    
    try:
        from adaptive_recommender import AdaptiveFashionRecommender
        
        # Load catalog
        catalog = []
        df = pd.read_csv("catalog.csv")
        
        for _, row in df.iterrows():
            catalog.append({
                "id": row['id'],
                "brand": row['brand'],
                "title": row['title'],
                "price": float(row['price']),
                "tags": row.get('tags', '').split(',') if pd.notna(row.get('tags')) else [],
                "image_url": row['image_url']
            })
        
        print(f"📦 Processed {len(catalog)} catalog items")
        
        # Initialize recommender
        recommender = AdaptiveFashionRecommender()
        catalog_df = pd.DataFrame(catalog)
        
        print("🔧 Building catalog index...")
        recommender.build_catalog_index(catalog_df)
        
        print("✅ AdaptiveFashionRecommender initialized successfully!")
        
        # Test a simple recommendation
        print("\n🎯 Testing brand search...")
        results = recommender.search_by_brand("Nike", k=3)
        
        if results and len(results) > 0:
            print(f"✅ Found {len(results)} Nike items:")
            for result in results[:3]:
                print(f"   • {result['title']} (ID: {result['id']})")
        else:
            print("⚠️  No Nike items found (might be normal)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing adaptive recommender: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 CATALOG & SYSTEM VERIFICATION")
    print("=" * 50)
    
    # Check catalog
    catalog_ok = check_catalog()
    
    # Test recommender
    recommender_ok = test_adaptive_recommender()
    
    print(f"\n📊 RESULTS:")
    print(f"   Catalog: {'✅ OK' if catalog_ok else '❌ FAILED'}")
    print(f"   Recommender: {'✅ OK' if recommender_ok else '❌ FAILED'}")
    
    if catalog_ok and recommender_ok:
        print("\n🎉 Everything looks good! The system should work.")
        print("💡 Try starting the API server: python adaptive_api.py")
    else:
        print("\n⚠️  Issues found. Fix these before testing the API.")
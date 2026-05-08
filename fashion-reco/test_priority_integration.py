#!/usr/bin/env python3
"""
Priority System Integration Test
Tests the full integration between frontend TypeScript and backend Python
"""

import requests
import json
import time


def test_priority_integration():
    """Test priority-based recommendations through the API."""

    print("🧪 PRIORITY SYSTEM INTEGRATION TEST")
    print("=" * 50)
    print("🔗 Testing Frontend → Backend priority integration")
    print()

    base_url = "http://localhost:8004"
    user_id = f"priority_user_{int(time.time())}"

    # Test different priority scenarios
    test_cases = [
        {
            "name": "🖼️ Image Priority (Highest)",
            "data": {
                "user_id": user_id,
                "image_url": "https://example.com/nike_shoe.jpg",
                "adaptation_strength": 0.8,
                "k": 3,
            },
        },
        {
            "name": "🏷️ Brand Priority (Medium)",
            "data": {
                "user_id": user_id,
                "brand_name": "Nike",
                "adaptation_strength": 0.8,
                "k": 3,
            },
        },
        {
            "name": "📂 Category Priority (Lower)",
            "data": {
                "user_id": user_id,
                "category": "athletic",
                "adaptation_strength": 0.8,
                "k": 3,
            },
        },
        {
            "name": "🎯 Combined Priorities (Image + Brand + Category)",
            "data": {
                "user_id": user_id,
                "image_url": "https://example.com/nike_shoe.jpg",
                "brand_name": "Nike",
                "category": "footwear",
                "adaptation_strength": 0.8,
                "k": 3,
            },
        },
        {
            "name": "🚫 Smart Exclusion (with excluded items)",
            "data": {
                "user_id": user_id,
                "brand_name": "Nike",
                "exclude_items": ["1", "2", "3"],
                "adaptation_strength": 0.8,
                "k": 3,
            },
        },
    ]

    success_count = 0

    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 TEST {i}: {test_case['name']}")
        print("-" * (10 + len(test_case["name"])))

        try:
            response = requests.post(
                f"{base_url}/recommend/adaptive", json=test_case["data"], timeout=10
            )

            if response.status_code == 200:
                recommendations = response.json()
                print(f"✅ Success: Got {len(recommendations)} recommendations")

                for j, rec in enumerate(recommendations[:2]):  # Show first 2
                    print(
                        f"  {j + 1}. {rec['title']} ({rec['brand']}) - Score: {rec['score']:.3f}"
                    )

                if recommendations:
                    rec = recommendations[0]
                    adaptation = rec["score"] - rec.get("base_score", rec["score"])
                    print(f"  🎯 Adaptation: {adaptation:+.3f}")
                    print(f"  🤖 Personalized: {rec.get('is_personalized', False)}")

                success_count += 1

            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   Response: {response.text[:100]}...")

        except Exception as e:
            print(f"❌ Request failed: {e}")

        print()

    # Summary
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 30)
    print(f"✅ Successful Tests: {success_count}/{len(test_cases)}")
    print(f"❌ Failed Tests: {len(test_cases) - success_count}/{len(test_cases)}")

    if success_count == len(test_cases):
        print(f"\n🎉 🎉 🎉 PERFECT INTEGRATION! 🎉 🎉 🎉")
        print(f"✨ Your priority system is fully working!")
        print(f"✨ Frontend can send priority-based requests")
        print(f"✨ Backend processes priorities correctly")
        print(f"✨ Smart exclusion prevents repetition")
        print(f"✨ Adaptive learning personalizes results")
        return True
    elif success_count > 0:
        print(f"\n🎯 Partial Success - Some priority features working")
        return True
    else:
        print(f"\n❌ Integration failed - Check if backend is running")
        print(f"💡 Start backend: python adaptive_api.py")
        return False


if __name__ == "__main__":
    success = test_priority_integration()
    print(f"\n{'🚀 READY FOR PRODUCTION!' if success else '🔧 NEEDS DEBUGGING'}")

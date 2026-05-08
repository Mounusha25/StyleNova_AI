#!/usr/bin/env python3
"""
SOLUTION: How to combine Quiz Features + Visual Features for Fashion Recommendations

Your Problem:
- You have quiz-based features (shoe size, clothing preferences, etc.)
- ResNet50 only takes image URLs as input
- You want to combine both approaches

SOLUTION: Hybrid Recommendation System
"""


# APPROACH 1: Quiz Features → Numerical Vector → Similarity Search
def convert_quiz_to_features(quiz_data):
    """Convert user quiz responses to numerical feature vector."""

    features = []

    # Size features (categorical → numerical)
    size_mapping = {"XS": 0.0, "S": 0.25, "M": 0.5, "L": 0.75, "XL": 1.0}
    features.append(size_mapping.get(quiz_data.get("size", "M"), 0.5))

    # Category preferences (multi-hot encoding)
    categories = ["shirt", "pants", "shoes", "dress", "jacket", "accessories"]
    user_categories = quiz_data.get("preferred_categories", [])
    for cat in categories:
        features.append(1.0 if cat in user_categories else 0.0)

    # Color preferences (multi-hot encoding)
    colors = ["black", "white", "blue", "red", "gray", "brown", "green"]
    user_colors = quiz_data.get("preferred_colors", [])
    for color in colors:
        features.append(1.0 if color in user_colors else 0.0)

    # Price preference (normalized)
    max_price = quiz_data.get("max_price", 100)
    features.append(min(max_price / 200.0, 1.0))  # Normalize to 0-1

    # Brand preferences (multi-hot encoding)
    brands = ["zara", "hm", "nike", "adidas", "uniqlo", "gucci", "prada"]
    user_brands = [b.lower() for b in quiz_data.get("preferred_brands", [])]
    for brand in brands:
        features.append(1.0 if brand in user_brands else 0.0)

    # Style preferences (multi-hot encoding)
    styles = ["casual", "formal", "sporty", "vintage", "trendy"]
    user_styles = quiz_data.get("preferred_styles", [])
    for style in styles:
        features.append(1.0 if style in user_styles else 0.0)

    return features


# APPROACH 2: Product Features → Numerical Vector (for catalog items)
def convert_product_to_features(product_data):
    """Convert product attributes to numerical feature vector."""

    features = []

    # Size (if applicable)
    size_mapping = {"XS": 0.0, "S": 0.25, "M": 0.5, "L": 0.75, "XL": 1.0}
    features.append(size_mapping.get(product_data.get("size", "M"), 0.5))

    # Category (one-hot)
    categories = ["shirt", "pants", "shoes", "dress", "jacket", "accessories"]
    product_category = product_data.get("category", "").lower()
    for cat in categories:
        features.append(1.0 if cat == product_category else 0.0)

    # Color (extracted from title/description)
    colors = ["black", "white", "blue", "red", "gray", "brown", "green"]
    product_text = (
        product_data.get("title", "") + " " + product_data.get("description", "")
    ).lower()
    for color in colors:
        features.append(1.0 if color in product_text else 0.0)

    # Price (normalized)
    price = float(product_data.get("price", 50))
    features.append(min(price / 200.0, 1.0))

    # Brand (one-hot)
    brands = ["zara", "hm", "nike", "adidas", "uniqlo", "gucci", "prada"]
    product_brand = product_data.get("brand", "").lower()
    for brand in brands:
        features.append(1.0 if brand == product_brand else 0.0)

    # Style (extracted from tags/description)
    styles = ["casual", "formal", "sporty", "vintage", "trendy"]
    for style in styles:
        features.append(1.0 if style in product_text else 0.0)

    return features


# APPROACH 3: Hybrid Scoring System
def get_hybrid_recommendations(user_quiz, query_image_url=None, catalog=None):
    """
    Combine quiz-based and visual-based recommendations.

    Args:
        user_quiz: Dictionary with user preferences from quiz
        query_image_url: Optional image URL for visual similarity
        catalog: List of product dictionaries

    Returns:
        List of recommendations with hybrid scores
    """

    recommendations = []

    # Convert user quiz to feature vector
    user_features = convert_quiz_to_features(user_quiz)

    for product in catalog:
        # 1. Quiz-based scoring
        product_features = convert_product_to_features(product)

        # Calculate cosine similarity for quiz features
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        quiz_similarity = cosine_similarity([user_features], [product_features])[0][0]

        # 2. Visual-based scoring (if image provided)
        visual_similarity = 0.0
        if query_image_url and "image_url" in product:
            try:
                # Use your existing ResNet50 extractor
                # visual_similarity = calculate_visual_similarity(query_image_url, product['image_url'])
                visual_similarity = 0.5  # Placeholder
            except:
                visual_similarity = 0.0

        # 3. Combine scores with weights
        quiz_weight = 0.7 if query_image_url is None else 0.5
        visual_weight = 0.0 if query_image_url is None else 0.5

        hybrid_score = (quiz_weight * quiz_similarity) + (
            visual_weight * visual_similarity
        )

        recommendations.append(
            {
                "product": product,
                "quiz_score": quiz_similarity,
                "visual_score": visual_similarity,
                "hybrid_score": hybrid_score,
                "recommendation_type": "quiz_only"
                if query_image_url is None
                else "hybrid",
            }
        )

    # Sort by hybrid score
    recommendations.sort(key=lambda x: x["hybrid_score"], reverse=True)

    return recommendations


# USAGE EXAMPLE
def example_usage():
    """Example of how to use the hybrid system."""

    # 1. User fills out quiz
    user_quiz = {
        "size": "M",
        "preferred_categories": ["shirt", "pants"],
        "preferred_colors": ["white", "blue"],
        "max_price": 80,
        "preferred_brands": ["Zara", "H&M"],
        "preferred_styles": ["casual", "trendy"],
    }

    # 2. Sample catalog (your real catalog would come from database/CSV)
    catalog = [
        {
            "id": "1",
            "title": "White Cotton Shirt",
            "brand": "Zara",
            "price": 29.99,
            "category": "shirt",
            "image_url": "https://example.com/white-shirt.jpg",
        },
        {
            "id": "2",
            "title": "Blue Casual Pants",
            "brand": "H&M",
            "price": 45.99,
            "category": "pants",
            "image_url": "https://example.com/blue-pants.jpg",
        },
        {
            "id": "3",
            "title": "Black Sneakers",
            "brand": "Nike",
            "price": 89.99,
            "category": "shoes",
            "image_url": "https://example.com/black-sneakers.jpg",
        },
    ]

    # 3. Get recommendations (quiz only)
    print("📋 QUIZ-ONLY RECOMMENDATIONS:")
    quiz_recs = get_hybrid_recommendations(user_quiz, catalog=catalog)
    for i, rec in enumerate(quiz_recs[:3]):
        print(f"{i + 1}. {rec['product']['title']} (score: {rec['hybrid_score']:.3f})")

    # 4. Get recommendations (quiz + visual)
    print("\n🔄 HYBRID RECOMMENDATIONS (Quiz + Visual):")
    query_image = "https://example.com/user-uploaded-image.jpg"
    hybrid_recs = get_hybrid_recommendations(user_quiz, query_image, catalog)
    for i, rec in enumerate(hybrid_recs[:3]):
        print(
            f"{i + 1}. {rec['product']['title']} (hybrid: {rec['hybrid_score']:.3f}, quiz: {rec['quiz_score']:.3f}, visual: {rec['visual_score']:.3f})"
        )


# API INTEGRATION EXAMPLE
def api_integration_example():
    """How to integrate with your existing API."""

    # FastAPI endpoint structure
    api_example = """
    @app.post("/recommend/hybrid")
    async def hybrid_recommendations(
        quiz_features: QuizFeatures,
        image_url: Optional[str] = None,
        k: int = 10
    ):
        # Convert quiz to feature vector
        user_vector = convert_quiz_to_features(quiz_features.dict())
        
        # Get recommendations
        if image_url:
            # Use both quiz and visual features
            recs = get_hybrid_recommendations(quiz_features.dict(), image_url, catalog)
        else:
            # Use only quiz features
            recs = get_hybrid_recommendations(quiz_features.dict(), catalog=catalog)
        
        return recs[:k]
    """

    print("🚀 API Integration Example:")
    print(api_example)


if __name__ == "__main__":
    print("🎯 SOLUTION: Hybrid Fashion Recommender")
    print("=" * 50)
    print("✅ Combines Quiz Features + Visual Features")
    print("✅ Works with your existing ResNet50 system")
    print("✅ Flexible weighting between approaches")
    print("✅ Falls back to quiz-only when no image provided")
    print("\n")

    example_usage()
    print("\n")
    api_integration_example()

    print("\n💡 IMPLEMENTATION STEPS:")
    print("1. Map your quiz questions to numerical features")
    print("2. Extract similar features from your product catalog")
    print("3. Use cosine similarity for quiz-based matching")
    print("4. Keep your ResNet50 system for visual similarity")
    print("5. Combine both scores with adjustable weights")
    print("6. Return ranked recommendations")

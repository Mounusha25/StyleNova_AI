#!/usr/bin/env python3
"""
Hybrid Fashion Recommender - Combines Quiz Features + Visual Features
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from models.extractor import ResNet50FeatureExtractor
from indexing.sklearn_index import SklearnIndex

logger = logging.getLogger(__name__)


class HybridFashionRecommender:
    """
    Hybrid recommender combining quiz-based features and visual features.
    """

    def __init__(self):
        # Visual feature extractor
        self.visual_extractor = ResNet50FeatureExtractor()
        self.visual_index = None

        # Quiz feature processors
        self.quiz_scaler = StandardScaler()
        self.quiz_features_matrix = None

        # Combined system
        self.catalog_df = None

    def process_quiz_features(self, catalog_df):
        """Process quiz-based features from catalog."""

        # Example quiz features you might have
        quiz_features = []

        for _, row in catalog_df.iterrows():
            # Extract quiz-based features from your data
            features = []

            # Size features (normalize to 0-1)
            if "size" in row:
                size_mapping = {"XS": 0, "S": 0.25, "M": 0.5, "L": 0.75, "XL": 1.0}
                features.append(size_mapping.get(row["size"], 0.5))

            # Category features (one-hot encoding)
            categories = ["shirt", "pants", "shoes", "dress", "jacket"]
            for cat in categories:
                if "category" in row and cat in str(row.get("category", "")).lower():
                    features.append(1.0)
                else:
                    features.append(0.0)

            # Color features (one-hot encoding)
            colors = ["black", "white", "blue", "red", "gray"]
            for color in colors:
                if any(
                    color in str(row.get(col, "")).lower()
                    for col in ["title", "tags", "color"]
                    if col in row
                ):
                    features.append(1.0)
                else:
                    features.append(0.0)

            # Price features (normalized)
            if "price" in row:
                # Normalize price to 0-1 range (assuming max price 200)
                features.append(min(float(row["price"]) / 200.0, 1.0))

            # Brand features (you can expand this)
            brands = ["zara", "hm", "nike", "adidas", "uniqlo"]
            for brand in brands:
                if "brand" in row and brand in str(row["brand"]).lower():
                    features.append(1.0)
                else:
                    features.append(0.0)

            quiz_features.append(features)

        # Normalize quiz features
        self.quiz_features_matrix = self.quiz_scaler.fit_transform(quiz_features)

        logger.info(f"📋 Processed quiz features: {self.quiz_features_matrix.shape}")
        return self.quiz_features_matrix

    def build_visual_index(self, catalog_df):
        """Build visual similarity index."""

        visual_embeddings = []
        successful_items = []

        for idx, row in catalog_df.iterrows():
            try:
                features = self.visual_extractor.extract_from_url(row["image_url"])
                visual_embeddings.append(
                    {
                        "id": str(row["id"]),
                        "brand": str(row["brand"]),
                        "title": str(row["title"]),
                        "price": float(row["price"]),
                        "tags": row.get("tags", []),
                        "image_url": str(row["image_url"]),
                        "embedding": features.squeeze().numpy().tolist(),
                    }
                )
                successful_items.append(idx)

            except Exception as e:
                logger.warning(f"Failed to process {row['title']}: {e}")

        if visual_embeddings:
            visual_df = pd.DataFrame(visual_embeddings)
            self.visual_index = SklearnIndex(dimension=2048, metric="cosine")
            self.visual_index.build_index(visual_df)

            logger.info(f"🖼️ Built visual index with {len(visual_embeddings)} items")
            return successful_items

        return []

    def get_quiz_recommendations(self, user_quiz_features, k=10):
        """Get recommendations based on quiz features."""

        if self.quiz_features_matrix is None:
            raise ValueError("Quiz features not processed yet")

        # Normalize user features
        user_features = self.quiz_scaler.transform([user_quiz_features])

        # Calculate similarity with all items
        similarities = cosine_similarity(user_features, self.quiz_features_matrix)[0]

        # Get top k similar items
        top_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for i, idx in enumerate(top_indices):
            if idx < len(self.catalog_df):
                item = self.catalog_df.iloc[idx]
                results.append(
                    {
                        "rank": i + 1,
                        "id": str(item["id"]),
                        "brand": str(item["brand"]),
                        "title": str(item["title"]),
                        "price": float(item["price"]),
                        "score": float(similarities[idx]),
                        "recommendation_type": "quiz_based",
                    }
                )

        return results

    def get_visual_recommendations(self, image_url, k=10):
        """Get recommendations based on visual similarity."""

        if self.visual_index is None:
            raise ValueError("Visual index not built yet")

        # Extract features from query image
        query_features = self.visual_extractor.extract_from_url(image_url)
        query_features = query_features.squeeze().numpy()

        # Search visual index
        results = self.visual_index.search(query_features, k=k)

        # Add recommendation type
        for result in results:
            result["recommendation_type"] = "visual_based"

        return results

    def get_hybrid_recommendations(
        self,
        user_quiz_features=None,
        image_url=None,
        quiz_weight=0.5,
        visual_weight=0.5,
        k=10,
    ):
        """
        Get hybrid recommendations combining quiz and visual features.

        Args:
            user_quiz_features: List of quiz features
            image_url: URL of reference image
            quiz_weight: Weight for quiz-based recommendations (0-1)
            visual_weight: Weight for visual-based recommendations (0-1)
            k: Number of recommendations to return
        """

        results = []

        # Get quiz-based recommendations
        if user_quiz_features is not None:
            quiz_results = self.get_quiz_recommendations(user_quiz_features, k=k * 2)
            for result in quiz_results:
                result["score"] *= quiz_weight
                results.append(result)

        # Get visual-based recommendations
        if image_url is not None:
            visual_results = self.get_visual_recommendations(image_url, k=k * 2)
            for result in visual_results:
                result["score"] *= visual_weight
                results.append(result)

        # Combine and deduplicate
        combined_results = {}
        for result in results:
            item_id = result["id"]
            if item_id in combined_results:
                # Combine scores from different methods
                combined_results[item_id]["score"] += result["score"]
                combined_results[item_id]["recommendation_type"] = "hybrid"
            else:
                combined_results[item_id] = result

        # Sort by combined score and return top k
        final_results = list(combined_results.values())
        final_results.sort(key=lambda x: x["score"], reverse=True)

        # Update ranks
        for i, result in enumerate(final_results[:k]):
            result["rank"] = i + 1

        return final_results[:k]

    def build_system(self, catalog_df):
        """Build the complete hybrid system."""

        self.catalog_df = catalog_df

        logger.info("🏗️ Building hybrid recommendation system...")

        # Process quiz features
        self.process_quiz_features(catalog_df)

        # Build visual index
        visual_success_indices = self.build_visual_index(catalog_df)

        logger.info("✅ Hybrid system built successfully!")

        return {
            "total_items": len(catalog_df),
            "visual_items": len(visual_success_indices),
            "quiz_features_dim": self.quiz_features_matrix.shape[1]
            if self.quiz_features_matrix is not None
            else 0,
        }


# Example usage
def example_usage():
    """Example of how to use the hybrid recommender."""

    # Load your catalog
    from api_simple import load_catalog_from_csv

    catalog = load_catalog_from_csv("catalog.csv")
    catalog_df = pd.DataFrame(catalog)

    # Initialize hybrid recommender
    recommender = HybridFashionRecommender()

    # Build the system
    stats = recommender.build_system(catalog_df)
    print(f"System built: {stats}")

    # Example user quiz features
    # [size, shirt, pants, shoes, dress, jacket, black, white, blue, red, gray, price_norm, zara, h&m, nike, adidas, uniqlo]
    user_quiz = [
        0.5,
        1,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0.3,
        1,
        0,
        0,
        0,
        0,
    ]  # Medium size, shirt, white, low price, Zara

    # Get quiz-based recommendations
    quiz_recs = recommender.get_quiz_recommendations(user_quiz, k=5)
    print("📋 Quiz-based recommendations:")
    for rec in quiz_recs:
        print(f"  {rec['rank']}. {rec['title']} (score: {rec['score']:.3f})")

    # Get visual-based recommendations
    test_image = "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"
    visual_recs = recommender.get_visual_recommendations(test_image, k=5)
    print("\n🖼️ Visual-based recommendations:")
    for rec in visual_recs:
        print(f"  {rec['rank']}. {rec['title']} (score: {rec['score']:.3f})")

    # Get hybrid recommendations
    hybrid_recs = recommender.get_hybrid_recommendations(
        user_quiz_features=user_quiz,
        image_url=test_image,
        quiz_weight=0.6,
        visual_weight=0.4,
        k=5,
    )
    print("\n🔄 Hybrid recommendations:")
    for rec in hybrid_recs:
        print(
            f"  {rec['rank']}. {rec['title']} (score: {rec['score']:.3f}) [{rec['recommendation_type']}]"
        )


if __name__ == "__main__":
    example_usage()

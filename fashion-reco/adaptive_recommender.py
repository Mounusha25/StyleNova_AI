#!/usr/bin/env python3
"""
Adaptive Fashion Recommender with Like/Dislike Feedback
Implements Reinforcement Learning from Human Feedback (RLHF)

Features:
1. User feedback: like/dislike items
2. Negative feedback: temporary avoidance (not permanent)
3. Positive feedback: boost similar items
4. Temporal decay: negative feedback weakens over time
5. User profiles: learn individual preferences
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Optional
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from clip_recommender import CLIPFashionRecommender

logger = logging.getLogger(__name__)


class AdaptiveFashionRecommender(CLIPFashionRecommender):
    """
    Adaptive fashion recommender that learns from user feedback.

    Concepts implemented:
    - Positive reinforcement: Boost similar items when user likes something
    - Negative reinforcement: Temporarily avoid similar items when user dislikes
    - Temporal decay: Negative feedback weakens over time (not permanent)
    - User profiling: Individual preference learning
    """

    def __init__(self, model_name: str = "ViT-B/32"):
        super().__init__(model_name)

        # User feedback storage
        self.user_profiles = defaultdict(
            lambda: {
                "liked_items": [],
                "disliked_items": [],
                "feedback_history": [],
                "preference_vector": None,
            }
        )

        # Feedback weights and decay settings
        self.positive_boost = 0.3  # How much to boost similar items when liked
        self.negative_penalty = -0.4  # How much to penalize similar items when disliked
        self.decay_rate = 0.1  # How fast negative feedback decays (per day)
        self.min_negative_weight = (
            -0.1
        )  # Minimum negative impact (never completely ignore)

        logger.info("🧠 Adaptive Fashion Recommender initialized with RLHF")

    def add_feedback(
        self,
        user_id: str,
        item_id: str,
        feedback: str,
        item_embedding: np.ndarray = None,
    ):
        """
        Add user feedback for an item.

        Args:
            user_id: Unique user identifier
            item_id: Product ID that was recommended
            feedback: 'like' or 'dislike'
            item_embedding: CLIP embedding of the item (optional)
        """

        timestamp = datetime.now()

        # Find item in catalog
        item_data = None
        if self.catalog_df is not None:
            item_rows = self.catalog_df[self.catalog_df["id"] == item_id]
            if not item_rows.empty:
                item_data = item_rows.iloc[0].to_dict()

        # Get or compute item embedding
        if item_embedding is None and item_data is not None:
            try:
                # Try to get embedding from catalog or compute it
                if "image_url" in item_data:
                    item_embedding = self.encode_image_from_url(item_data["image_url"])
                else:
                    # Fallback to text description
                    text_desc = self.product_to_text_description(item_data)
                    item_embedding = self.encode_text(text_desc)
            except Exception as e:
                logger.warning(f"Could not get embedding for item {item_id}: {e}")
                return

        if item_embedding is None:
            logger.warning(f"No embedding available for item {item_id}")
            return

        # Store feedback
        feedback_entry = {
            "item_id": item_id,
            "feedback": feedback,
            "timestamp": timestamp,
            "embedding": item_embedding.tolist()
            if isinstance(item_embedding, np.ndarray)
            else item_embedding,
            "item_data": item_data,
        }

        profile = self.user_profiles[user_id]
        profile["feedback_history"].append(feedback_entry)

        if feedback == "like":
            profile["liked_items"].append(feedback_entry)
            logger.info(f"👍 User {user_id} liked item {item_id}")
        elif feedback == "dislike":
            profile["disliked_items"].append(feedback_entry)
            logger.info(f"👎 User {user_id} disliked item {item_id}")

        # Update user preference vector
        self._update_user_preferences(user_id)

    def _update_user_preferences(self, user_id: str):
        """Update user's preference vector based on feedback history."""

        profile = self.user_profiles[user_id]

        if not profile["feedback_history"]:
            return

        # Compute weighted average of liked/disliked items
        positive_embeddings = []
        negative_embeddings = []

        current_time = datetime.now()

        for feedback in profile["feedback_history"]:
            embedding = np.array(feedback["embedding"])

            if feedback["feedback"] == "like":
                positive_embeddings.append(embedding)
            elif feedback["feedback"] == "dislike":
                # Apply temporal decay to negative feedback
                time_diff = current_time - feedback["timestamp"]
                days_passed = time_diff.total_seconds() / (24 * 3600)

                # Exponential decay
                decay_factor = np.exp(-self.decay_rate * days_passed)
                weight = max(
                    self.min_negative_weight, self.negative_penalty * decay_factor
                )

                negative_embeddings.append(embedding * abs(weight))

        # Compute preference vector
        preference_vector = np.zeros(512)  # CLIP embedding dimension

        if positive_embeddings:
            positive_mean = np.mean(positive_embeddings, axis=0)
            preference_vector += self.positive_boost * positive_mean

        if negative_embeddings:
            negative_mean = np.mean(negative_embeddings, axis=0)
            preference_vector -= negative_mean

        # Normalize
        if np.linalg.norm(preference_vector) > 0:
            preference_vector = preference_vector / np.linalg.norm(preference_vector)

        profile["preference_vector"] = preference_vector

        logger.info(
            f"🔄 Updated preferences for user {user_id}: {len(positive_embeddings)} likes, {len(negative_embeddings)} dislikes"
        )

    def get_priority_adaptive_recommendations(
        self,
        user_id: str,
        image_url: str = None,
        brand_name: str = None,
        category: str = None,
        quiz_features: dict = None,
        k: int = 10,
        adaptation_strength: float = 0.5,
    ) -> List[Dict]:
        """
        Get adaptive recommendations with priority-based input weighting.

        Priority Order:
        1. Image URL (Highest Priority - 0.6 weight)
        2. Brand Name (Medium Priority - 0.3 weight)
        3. Category (Lower Priority - 0.1 weight)
        4. Quiz Features (Fallback)

        Args:
            user_id: User identifier
            image_url: Product image URL (highest priority)
            brand_name: Brand name filter (medium priority)
            category: Category filter (lower priority)
            quiz_features: Quiz results (fallback)
            k: Number of recommendations
            adaptation_strength: How much to adapt based on user feedback (0-1)
        """

        if self.catalog_embeddings is None:
            raise ValueError(
                "Catalog index not built. Call build_catalog_index() first."
            )

        # Priority weights for different input types
        IMAGE_WEIGHT = 0.6  # Highest priority
        BRAND_WEIGHT = 0.3  # Medium priority
        CATEGORY_WEIGHT = 0.1  # Lower priority

        combined_embedding = None
        query_info = []
        total_weight = 0

        # 1. HIGHEST PRIORITY: Image URL
        if image_url:
            try:
                image_embedding = self.encode_image_from_url(image_url)
                if combined_embedding is None:
                    combined_embedding = IMAGE_WEIGHT * image_embedding
                else:
                    combined_embedding += IMAGE_WEIGHT * image_embedding
                total_weight += IMAGE_WEIGHT
                query_info.append(f"🖼️ Image (weight: {IMAGE_WEIGHT})")
                logger.info(
                    f"🖼️ Applied image embedding with highest priority (weight: {IMAGE_WEIGHT})"
                )
            except Exception as e:
                logger.warning(f"Could not process image {image_url}: {e}")

        # 2. MEDIUM PRIORITY: Brand Name
        if brand_name:
            try:
                brand_text = f"{brand_name} brand fashion clothing"
                brand_embedding = self.encode_text(brand_text)
                if combined_embedding is None:
                    combined_embedding = BRAND_WEIGHT * brand_embedding
                else:
                    combined_embedding += BRAND_WEIGHT * brand_embedding
                total_weight += BRAND_WEIGHT
                query_info.append(f"🏷️ Brand '{brand_name}' (weight: {BRAND_WEIGHT})")
                logger.info(
                    f"🏷️ Applied brand embedding with medium priority (weight: {BRAND_WEIGHT})"
                )
            except Exception as e:
                logger.warning(f"Could not process brand {brand_name}: {e}")

        # 3. LOWER PRIORITY: Category
        if category:
            try:
                category_text = f"{category} clothing fashion"
                category_embedding = self.encode_text(category_text)
                if combined_embedding is None:
                    combined_embedding = CATEGORY_WEIGHT * category_embedding
                else:
                    combined_embedding += CATEGORY_WEIGHT * category_embedding
                total_weight += CATEGORY_WEIGHT
                query_info.append(
                    f"📂 Category '{category}' (weight: {CATEGORY_WEIGHT})"
                )
                logger.info(
                    f"📂 Applied category embedding with lower priority (weight: {CATEGORY_WEIGHT})"
                )
            except Exception as e:
                logger.warning(f"Could not process category {category}: {e}")

        # 4. FALLBACK: Quiz Features (if no other inputs)
        if combined_embedding is None and quiz_features:
            try:
                quiz_text = self.quiz_to_text_description(quiz_features)
                combined_embedding = self.encode_text(quiz_text)
                total_weight = 1.0
                query_info.append("📋 Quiz Features (fallback)")
                logger.info("📋 Applied quiz features as fallback")
            except Exception as e:
                logger.warning(f"Could not process quiz features: {e}")

        if combined_embedding is None:
            raise ValueError(
                "No valid input provided (image_url, brand_name, category, or quiz_features)"
            )

        # Normalize combined embedding
        if total_weight > 0:
            combined_embedding = combined_embedding / total_weight

        # Normalize to unit vector
        if np.linalg.norm(combined_embedding) > 0:
            combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)

        logger.info(f"🎯 Priority Query: {' + '.join(query_info)}")

        # Get base similarities using priority-weighted query
        base_similarities = np.dot(self.catalog_embeddings, combined_embedding)

        # Apply user preferences if available
        profile = self.user_profiles[user_id]
        adapted_similarities = base_similarities.copy()

        if profile["preference_vector"] is not None:
            # Calculate preference-based similarities
            preference_similarities = np.dot(
                self.catalog_embeddings, profile["preference_vector"]
            )

            # Combine base query with user preferences
            adapted_similarities = (
                1 - adaptation_strength
            ) * base_similarities + adaptation_strength * preference_similarities

            logger.info(
                f"🧠 Applied adaptive weighting for user {user_id} (strength: {adaptation_strength})"
            )

        # Apply direct item penalties for recently disliked items
        adapted_similarities = self._apply_item_penalties(user_id, adapted_similarities)

        # Get top k results
        top_indices = np.argsort(adapted_similarities)[::-1][:k]

        results = []
        for i, idx in enumerate(top_indices):
            if idx < len(self.catalog_df):
                item = self.catalog_df.iloc[idx]

                # Check if this item was previously rated
                user_feedback = self._get_item_feedback(user_id, str(item["id"]))

                results.append(
                    {
                        "rank": i + 1,
                        "id": str(item["id"]),
                        "brand": str(item["brand"]),
                        "title": str(item["title"]),
                        "price": float(item["price"]),
                        "score": float(adapted_similarities[idx]),
                        "base_score": float(base_similarities[idx]),
                        "image_url": str(item["image_url"]),
                        "recommendation_type": "priority_adaptive",
                        "query_info": query_info,
                        "user_feedback": user_feedback,
                        "is_personalized": profile["preference_vector"] is not None,
                    }
                )

        return results

    def get_adaptive_recommendations(
        self,
        user_id: str,
        query_embedding: np.ndarray,
        k: int = 10,
        adaptation_strength: float = 0.5,
    ) -> List[Dict]:
        """
        Get recommendations adapted to user's feedback history.

        Args:
            user_id: User identifier
            query_embedding: Query embedding (from quiz, image, or brand search)
            k: Number of recommendations
            adaptation_strength: How much to adapt based on user feedback (0-1)
        """

        if self.catalog_embeddings is None:
            raise ValueError(
                "Catalog index not built. Call build_catalog_index() first."
            )

        # Get base similarities
        base_similarities = np.dot(self.catalog_embeddings, query_embedding)

        # Apply user preferences if available
        profile = self.user_profiles[user_id]
        adapted_similarities = base_similarities.copy()

        if profile["preference_vector"] is not None:
            # Calculate preference-based similarities
            preference_similarities = np.dot(
                self.catalog_embeddings, profile["preference_vector"]
            )

            # Combine base query with user preferences
            adapted_similarities = (
                1 - adaptation_strength
            ) * base_similarities + adaptation_strength * preference_similarities

            logger.info(
                f"🎯 Applied adaptive weighting for user {user_id} (strength: {adaptation_strength})"
            )

        # Apply direct item penalties for recently disliked items
        adapted_similarities = self._apply_item_penalties(user_id, adapted_similarities)

        # Get top k results
        top_indices = np.argsort(adapted_similarities)[::-1][:k]

        results = []
        for i, idx in enumerate(top_indices):
            if idx < len(self.catalog_df):
                item = self.catalog_df.iloc[idx]

                # Check if this item was previously rated
                user_feedback = self._get_item_feedback(user_id, str(item["id"]))

                results.append(
                    {
                        "rank": i + 1,
                        "id": str(item["id"]),
                        "brand": str(item["brand"]),
                        "title": str(item["title"]),
                        "price": float(item["price"]),
                        "score": float(adapted_similarities[idx]),
                        "base_score": float(base_similarities[idx]),
                        "image_url": str(item["image_url"]),
                        "recommendation_type": "adaptive",
                        "user_feedback": user_feedback,
                        "is_personalized": profile["preference_vector"] is not None,
                    }
                )

        return results

    def _apply_item_penalties(
        self, user_id: str, similarities: np.ndarray
    ) -> np.ndarray:
        """Apply penalties for recently disliked specific items."""

        profile = self.user_profiles[user_id]
        current_time = datetime.now()

        for feedback in profile["disliked_items"]:
            # Find item index in catalog
            item_id = feedback["item_id"]
            item_indices = self.catalog_df[self.catalog_df["id"] == item_id].index

            if len(item_indices) > 0:
                idx = item_indices[0]

                # Apply temporal decay
                time_diff = current_time - feedback["timestamp"]
                days_passed = time_diff.total_seconds() / (24 * 3600)

                decay_factor = np.exp(-self.decay_rate * days_passed)
                penalty = max(
                    self.min_negative_weight, self.negative_penalty * decay_factor
                )

                # Apply penalty
                similarities[idx] += penalty

                logger.debug(
                    f"Applied penalty {penalty:.3f} to item {item_id} (disliked {days_passed:.1f} days ago)"
                )

        return similarities

    def _get_item_feedback(self, user_id: str, item_id: str) -> Optional[Dict]:
        """Get user's feedback for a specific item."""

        profile = self.user_profiles[user_id]

        for feedback in reversed(profile["feedback_history"]):  # Most recent first
            if feedback["item_id"] == item_id:
                return {
                    "feedback": feedback["feedback"],
                    "timestamp": feedback["timestamp"].isoformat(),
                    "days_ago": (datetime.now() - feedback["timestamp"]).days,
                }

        return None

    def get_user_stats(self, user_id: str) -> Dict:
        """Get user's feedback statistics."""

        profile = self.user_profiles[user_id]

        likes = len(profile["liked_items"])
        dislikes = len(profile["disliked_items"])
        total_feedback = len(profile["feedback_history"])

        # Count recent feedback (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_feedback = [
            f for f in profile["feedback_history"] if f["timestamp"] > week_ago
        ]

        return {
            "user_id": user_id,
            "total_feedback": total_feedback,
            "likes": likes,
            "dislikes": dislikes,
            "recent_feedback_7d": len(recent_feedback),
            "has_preference_profile": profile["preference_vector"] is not None,
            "preference_strength": float(np.linalg.norm(profile["preference_vector"]))
            if profile["preference_vector"] is not None
            else 0.0,
        }

    def save_user_profiles(self, filepath: str = "user_profiles.json"):
        """Save user profiles to file."""

        # Convert to serializable format
        serializable_profiles = {}

        for user_id, profile in self.user_profiles.items():
            serializable_profiles[user_id] = {
                "liked_items": [
                    {
                        **item,
                        "timestamp": item["timestamp"].isoformat(),
                        "embedding": item["embedding"],
                    }
                    for item in profile["liked_items"]
                ],
                "disliked_items": [
                    {
                        **item,
                        "timestamp": item["timestamp"].isoformat(),
                        "embedding": item["embedding"],
                    }
                    for item in profile["disliked_items"]
                ],
                "feedback_history": [
                    {
                        **item,
                        "timestamp": item["timestamp"].isoformat(),
                        "embedding": item["embedding"],
                    }
                    for item in profile["feedback_history"]
                ],
                "preference_vector": profile["preference_vector"].tolist()
                if profile["preference_vector"] is not None
                else None,
            }

        with open(filepath, "w") as f:
            json.dump(serializable_profiles, f, indent=2)

        logger.info(f"💾 Saved {len(self.user_profiles)} user profiles to {filepath}")

    def load_user_profiles(self, filepath: str = "user_profiles.json"):
        """Load user profiles from file."""

        try:
            with open(filepath, "r") as f:
                serializable_profiles = json.load(f)

            # Convert back to runtime format
            for user_id, profile in serializable_profiles.items():
                runtime_profile = {
                    "liked_items": [
                        {**item, "timestamp": datetime.fromisoformat(item["timestamp"])}
                        for item in profile["liked_items"]
                    ],
                    "disliked_items": [
                        {**item, "timestamp": datetime.fromisoformat(item["timestamp"])}
                        for item in profile["disliked_items"]
                    ],
                    "feedback_history": [
                        {**item, "timestamp": datetime.fromisoformat(item["timestamp"])}
                        for item in profile["feedback_history"]
                    ],
                    "preference_vector": np.array(profile["preference_vector"])
                    if profile["preference_vector"]
                    else None,
                }

                self.user_profiles[user_id] = runtime_profile

            logger.info(
                f"📁 Loaded {len(self.user_profiles)} user profiles from {filepath}"
            )

        except FileNotFoundError:
            logger.info(f"📁 No existing user profiles found at {filepath}")
        except Exception as e:
            logger.error(f"📁 Error loading user profiles: {e}")


# Example usage and testing
def example_adaptive_usage():
    """Example of how the adaptive system works."""

    print("🧠 Adaptive Fashion Recommender Example")
    print("=" * 50)

    # Load catalog
    from api_simple import load_catalog_from_csv

    catalog = load_catalog_from_csv("catalog.csv")
    catalog_df = pd.DataFrame(catalog)

    # Initialize adaptive recommender
    recommender = AdaptiveFashionRecommender()
    recommender.build_catalog_index(catalog_df)

    # Simulate user interactions
    user_id = "user_123"

    print(f"\n👤 User: {user_id}")

    # Initial search (no feedback yet)
    print("\n🔍 Initial search for 'Nike brand':")
    initial_query = recommender.encode_text("Nike brand fashion clothing")
    initial_results = recommender.get_adaptive_recommendations(
        user_id, initial_query, k=3
    )

    for result in initial_results:
        print(f"  {result['rank']}. {result['title']} (score: {result['score']:.3f})")

    # User likes first item
    if initial_results:
        liked_item = initial_results[0]
        print(f"\n👍 User likes: {liked_item['title']}")

        # Get item embedding
        item_embedding = recommender.catalog_embeddings[0]  # Simplified for demo
        recommender.add_feedback(user_id, liked_item["id"], "like", item_embedding)

    # User dislikes second item
    if len(initial_results) > 1:
        disliked_item = initial_results[1]
        print(f"👎 User dislikes: {disliked_item['title']}")

        item_embedding = recommender.catalog_embeddings[1]  # Simplified for demo
        recommender.add_feedback(
            user_id, disliked_item["id"], "dislike", item_embedding
        )

    # Search again with learned preferences
    print(f"\n🎯 Adaptive search for 'Nike brand' (after feedback):")
    adaptive_results = recommender.get_adaptive_recommendations(
        user_id, initial_query, k=3, adaptation_strength=0.7
    )

    for result in adaptive_results:
        feedback_info = (
            f" [{result['user_feedback']['feedback']}]"
            if result["user_feedback"]
            else ""
        )
        print(
            f"  {result['rank']}. {result['title']} (score: {result['score']:.3f}){feedback_info}"
        )

    # Show user stats
    print(f"\n📊 User Stats:")
    stats = recommender.get_user_stats(user_id)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print(f"\n✅ Adaptive learning demonstration complete!")
    print(f"💡 Key concepts:")
    print(f"  - Positive feedback boosts similar items")
    print(f"  - Negative feedback temporarily reduces similar items")
    print(f"  - Negative feedback decays over time (not permanent)")
    print(f"  - System learns individual user preferences")


if __name__ == "__main__":
    example_adaptive_usage()

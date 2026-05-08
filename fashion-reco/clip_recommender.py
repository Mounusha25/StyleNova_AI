#!/usr/bin/env python3
"""
CLIP-Based Fashion Recommender - Perfect for Quiz + Visual Features!

Why CLIP is PERFECT for your use case:
1. Handles both TEXT (quiz preferences) and IMAGES
2. Joint embedding space - can compare text to images directly
3. No need for separate feature extraction systems
4. More semantic understanding than ResNet50 alone
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Optional
import requests
from PIL import Image
import torch

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

logger = logging.getLogger(__name__)


class CLIPFashionRecommender:
    """
    CLIP-based fashion recommender that handles both quiz features and visual features.
    """

    def __init__(self, model_name: str = "ViT-B/32"):
        """Initialize CLIP model."""
        try:
            import clip

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model, self.preprocess = clip.load(model_name, device=self.device)
            logger.info(f"✅ CLIP model {model_name} loaded on {self.device}")
        except ImportError:
            logger.error(
                "❌ CLIP not installed. Install with: pip install git+https://github.com/openai/CLIP.git"
            )
            raise

        self.catalog_df = None
        self.catalog_embeddings = None

    def quiz_to_text_description(self, quiz_features: dict) -> str:
        """Convert quiz features to natural language description."""

        descriptions = []

        # Size
        if "size" in quiz_features:
            descriptions.append(f"size {quiz_features['size']}")

        # Categories
        if "preferred_categories" in quiz_features:
            categories = quiz_features["preferred_categories"]
            if categories:
                descriptions.append(f"{' or '.join(categories)} clothing")

        # Colors
        if "preferred_colors" in quiz_features:
            colors = quiz_features["preferred_colors"]
            if colors:
                descriptions.append(f"{' or '.join(colors)} colored")

        # Price
        if "max_price" in quiz_features:
            max_price = quiz_features["max_price"]
            if max_price < 50:
                descriptions.append("affordable budget-friendly")
            elif max_price < 100:
                descriptions.append("mid-range")
            else:
                descriptions.append("premium quality")

        # Brands
        if "preferred_brands" in quiz_features:
            brands = quiz_features["preferred_brands"]
            if brands:
                descriptions.append(f"{' or '.join(brands)} brand")

        # Style
        if "preferred_styles" in quiz_features:
            styles = quiz_features["preferred_styles"]
            if styles:
                descriptions.append(f"{' '.join(styles)} style")

        # Combine into natural language
        if descriptions:
            text = f"A {' '.join(descriptions)} fashion item"
        else:
            text = "A fashionable clothing item"

        logger.info(f"📝 Quiz converted to text: '{text}'")
        return text

    def product_to_text_description(self, product: dict) -> str:
        """Convert product details to text description."""

        parts = []

        # Brand and title
        if "brand" in product:
            parts.append(f"{product['brand']}")
        if "title" in product:
            parts.append(f"{product['title']}")

        # Category
        if "category" in product:
            parts.append(f"{product['category']} clothing")

        # Color (extract from title)
        colors = [
            "black",
            "white",
            "blue",
            "red",
            "gray",
            "brown",
            "green",
            "pink",
            "yellow",
        ]
        title_lower = product.get("title", "").lower()
        for color in colors:
            if color in title_lower:
                parts.append(f"{color} colored")
                break

        # Price range
        if "price" in product:
            price = float(product["price"])
            if price < 30:
                parts.append("affordable")
            elif price < 80:
                parts.append("mid-range")
            else:
                parts.append("premium")

        # Tags
        if "tags" in product and product["tags"]:
            if isinstance(product["tags"], list):
                parts.extend(product["tags"])
            elif isinstance(product["tags"], str):
                parts.extend(product["tags"].split(","))

        text = " ".join(parts)
        return text

    def encode_text(self, text: str) -> np.ndarray:
        """Encode text using CLIP."""
        import clip

        with torch.no_grad():
            text_tokens = clip.tokenize([text]).to(self.device)
            text_features = self.model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            return text_features.cpu().numpy().flatten()

    def encode_image_from_url(self, image_url: str) -> np.ndarray:
        """Encode image from URL using CLIP."""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            image = Image.open(requests.get(image_url, stream=True).raw)
            return self.encode_image(image)

        except requests.exceptions.HTTPError as e:
            if "403" in str(e) or "Forbidden" in str(e):
                logger.warning(f"Image URL inaccessible (403 Forbidden): {image_url}")
                return None
            else:
                logger.error(f"Failed to encode image from URL {image_url}: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to encode image from URL {image_url}: {e}")
            raise

    def encode_image(self, image: Image.Image) -> np.ndarray:
        """Encode PIL image using CLIP."""
        with torch.no_grad():
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            image_features = self.model.encode_image(image_tensor)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            return image_features.cpu().numpy().flatten()

    def build_catalog_index(self, catalog_df: pd.DataFrame):
        """Build CLIP embeddings for the entire catalog."""

        self.catalog_df = catalog_df
        embeddings = []
        valid_items = []

        logger.info(f"🏗️ Building CLIP index for {len(catalog_df)} items...")

        for idx, row in catalog_df.iterrows():
            try:
                # Method 1: Use product text description
                product_text = self.product_to_text_description(row.to_dict())
                text_embedding = self.encode_text(product_text)

                # Method 2: Use image (if available)
                image_embedding = None
                skip_item = False

                if "image_url" in row and pd.notna(row["image_url"]):
                    try:
                        image_embedding = self.encode_image_from_url(row["image_url"])
                        if image_embedding is None:
                            # 403 Forbidden - skip this item entirely
                            skip_item = True
                            logger.info(
                                f"  🚫 Skipping {row.get('title', 'unknown')} - inaccessible image"
                            )
                            continue
                    except Exception as e:
                        logger.warning(
                            f"Failed to encode image for {row.get('title', 'unknown')}: {e}"
                        )
                        # For other errors, we can still use text-only
                        image_embedding = None

                if skip_item:
                    continue

                # Combine text and image embeddings (if both available)
                if image_embedding is not None:
                    # Average text and image embeddings
                    combined_embedding = (text_embedding + image_embedding) / 2
                else:
                    # Use only text embedding
                    combined_embedding = text_embedding

                embeddings.append(combined_embedding)
                valid_items.append(row)
                logger.info(
                    f"  ✅ {row.get('title', 'unknown')} - {'text+image' if image_embedding is not None else 'text-only'}"
                )

            except Exception as e:
                logger.error(
                    f"  ❌ Failed to process {row.get('title', 'unknown')}: {e}"
                )
                # Skip items that fail completely

        # Update catalog with only valid items
        self.catalog_df = pd.DataFrame(valid_items).reset_index(drop=True)
        self.catalog_embeddings = np.array(embeddings)

        logger.info(f"✅ CLIP index built: {self.catalog_embeddings.shape}")
        logger.info(
            f"📊 Filtered catalog: {len(self.catalog_df)} valid items (removed {len(catalog_df) - len(self.catalog_df)} inaccessible)"
        )

    def search_by_quiz(self, quiz_features: dict, k: int = 10) -> List[Dict]:
        """Search using quiz-based text description."""

        if self.catalog_embeddings is None:
            raise ValueError(
                "Catalog index not built. Call build_catalog_index() first."
            )

        # Convert quiz to text and encode
        query_text = self.quiz_to_text_description(quiz_features)
        query_embedding = self.encode_text(query_text)

        # Calculate similarities
        similarities = np.dot(self.catalog_embeddings, query_embedding)

        # Get top k results
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
                        "image_url": str(item["image_url"]),
                        "recommendation_type": "quiz_based",
                    }
                )

        return results

    def search_by_image(self, image_url: str, k: int = 10) -> List[Dict]:
        """Search using visual similarity."""

        if self.catalog_embeddings is None:
            raise ValueError(
                "Catalog index not built. Call build_catalog_index() first."
            )

        # Encode query image
        query_embedding = self.encode_image_from_url(image_url)

        # Calculate similarities
        similarities = np.dot(self.catalog_embeddings, query_embedding)

        # Get top k results
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
                        "image_url": str(item["image_url"]),
                        "recommendation_type": "visual_based",
                    }
                )

        return results

    def search_by_brand(
        self, brand_name: str, category: str = None, style: str = None, k: int = 10
    ) -> List[Dict]:
        """Search using brand name with optional filters."""

        if self.catalog_embeddings is None:
            raise ValueError(
                "Catalog index not built. Call build_catalog_index() first."
            )

        # Create text description from brand
        text_parts = [brand_name, "brand"]

        if category:
            text_parts.append(category)

        if style:
            text_parts.append(style)

        # Create natural language query
        search_text = f"{' '.join(text_parts)} fashion clothing"

        logger.info(f"🏷️ Brand search text: '{search_text}'")

        # Encode query text
        query_embedding = self.encode_text(search_text)

        # Calculate similarities
        similarities = np.dot(self.catalog_embeddings, query_embedding)

        # Get top k results
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
                        "image_url": str(item["image_url"]),
                        "recommendation_type": "brand_based",
                    }
                )

        return results

    def search_hybrid(
        self,
        quiz_features: dict = None,
        image_url: str = None,
        quiz_weight: float = 0.5,
        visual_weight: float = 0.5,
        k: int = 10,
    ) -> List[Dict]:
        """Hybrid search combining quiz and visual features."""

        if self.catalog_embeddings is None:
            raise ValueError(
                "Catalog index not built. Call build_catalog_index() first."
            )

        combined_similarities = np.zeros(len(self.catalog_embeddings))

        # Quiz-based similarity
        if quiz_features:
            query_text = self.quiz_to_text_description(quiz_features)
            text_embedding = self.encode_text(query_text)
            text_similarities = np.dot(self.catalog_embeddings, text_embedding)
            combined_similarities += quiz_weight * text_similarities

        # Visual-based similarity
        if image_url:
            image_embedding = self.encode_image_from_url(image_url)
            image_similarities = np.dot(self.catalog_embeddings, image_embedding)
            combined_similarities += visual_weight * image_similarities

        # Get top k results
        top_indices = np.argsort(combined_similarities)[::-1][:k]

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
                        "score": float(combined_similarities[idx]),
                        "image_url": str(item["image_url"]),
                        "recommendation_type": "hybrid",
                    }
                )

        return results


# Example usage
def example_usage():
    """Example of how to use CLIP for fashion recommendations."""

    # Load catalog
    from api_simple import load_catalog_from_csv

    catalog = load_catalog_from_csv("catalog.csv")
    catalog_df = pd.DataFrame(catalog)

    # Initialize CLIP recommender
    recommender = CLIPFashionRecommender()

    # Build index
    recommender.build_catalog_index(catalog_df)

    # Example quiz features
    quiz_features = {
        "size": "M",
        "preferred_categories": ["shirt"],
        "preferred_colors": ["white"],
        "max_price": 50.0,
        "preferred_brands": ["Zara"],
        "preferred_styles": ["casual"],
    }

    print("📋 QUIZ-BASED RECOMMENDATIONS:")
    quiz_results = recommender.search_by_quiz(quiz_features, k=3)
    for result in quiz_results:
        print(f"  {result['rank']}. {result['title']} (score: {result['score']:.3f})")

    print("\n🖼️ VISUAL-BASED RECOMMENDATIONS:")
    test_image = "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"
    try:
        visual_results = recommender.search_by_image(test_image, k=3)
        for result in visual_results:
            print(
                f"  {result['rank']}. {result['title']} (score: {result['score']:.3f})"
            )
    except Exception as e:
        print(f"  ❌ Visual search failed: {e}")

    print("\n🔄 HYBRID RECOMMENDATIONS:")
    try:
        hybrid_results = recommender.search_hybrid(
            quiz_features=quiz_features,
            image_url=test_image,
            quiz_weight=0.6,
            visual_weight=0.4,
            k=3,
        )
        for result in hybrid_results:
            print(
                f"  {result['rank']}. {result['title']} (score: {result['score']:.3f})"
            )
    except Exception as e:
        print(f"  ❌ Hybrid search failed: {e}")


if __name__ == "__main__":
    print("🎯 CLIP Fashion Recommender")
    print("=" * 50)
    print("✅ Handles both quiz features (text) and images")
    print("✅ Joint embedding space for seamless comparison")
    print("✅ No separate feature extraction needed")
    print("✅ More semantic understanding than ResNet50")
    print()

    try:
        example_usage()
    except ImportError:
        print("❌ CLIP not installed. Run:")
        print("   pip install git+https://github.com/openai/CLIP.git")
    except Exception as e:
        print(f"❌ Error: {e}")

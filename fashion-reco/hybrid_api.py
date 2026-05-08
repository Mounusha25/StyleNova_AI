#!/usr/bin/env python3
"""
Hybrid Fashion Recommender API - Supports both quiz and visual features
"""

import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import numpy as np
import pandas as pd
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from models.extractor import ResNet50FeatureExtractor
from indexing.sklearn_index import SklearnIndex
from hybrid_recommender import HybridFashionRecommender

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hybrid Fashion Recommender API",
    description="Fashion recommendation API supporting both quiz features and visual similarity",
    version="2.0.0",
)

# Global variables
hybrid_recommender = None


# Pydantic models for API
class QuizFeatures(BaseModel):
    """User preferences from quiz."""

    size: Optional[str] = "M"  # XS, S, M, L, XL
    preferred_categories: List[str] = ["shirt"]  # shirt, pants, shoes, dress, jacket
    preferred_colors: List[str] = ["black"]  # black, white, blue, red, gray
    max_price: Optional[float] = 100.0
    preferred_brands: List[str] = ["zara"]  # zara, hm, nike, adidas, uniqlo


class HybridSearchRequest(BaseModel):
    """Request for hybrid recommendations."""

    # Quiz-based features (from your existing system)
    quiz_features: Optional[QuizFeatures] = None

    # Visual-based features (from image)
    image_url: Optional[str] = None

    # Weighting and parameters
    quiz_weight: float = 0.5
    visual_weight: float = 0.5
    k: int = 10


class RecommendationResponse(BaseModel):
    """Recommendation response."""

    rank: int
    id: str
    score: float
    brand: str
    title: str
    price: float
    tags: List[str]
    image_url: str
    recommendation_type: str  # "quiz_based", "visual_based", "hybrid"


def load_catalog_from_csv(csv_path: str = "catalog.csv"):
    """Load fashion catalog from CSV file."""
    try:
        df = pd.read_csv(csv_path)

        catalog = []
        for _, row in df.iterrows():
            # Handle tags - make it optional
            tags = []
            if "tags" in df.columns and not pd.isna(row.get("tags")):
                tags_value = row["tags"]
                if isinstance(tags_value, str):
                    tags = [tag.strip() for tag in tags_value.split(",")]

            # Add some sample category and color info for quiz features
            # In real implementation, these would come from your product data
            category = "shirt"  # Default
            if (
                "jean" in str(row["title"]).lower()
                or "pant" in str(row["title"]).lower()
            ):
                category = "pants"
            elif "shoe" in str(row["title"]).lower():
                category = "shoes"
            elif "dress" in str(row["title"]).lower():
                category = "dress"
            elif (
                "hoodie" in str(row["title"]).lower()
                or "jacket" in str(row["title"]).lower()
            ):
                category = "jacket"

            color = "black"  # Default
            title_lower = str(row["title"]).lower()
            for c in ["white", "blue", "red", "gray", "black"]:
                if c in title_lower:
                    color = c
                    break

            catalog.append(
                {
                    "id": str(row["id"]),
                    "brand": str(row["brand"]),
                    "title": str(row["title"]),
                    "price": float(row["price"]),
                    "tags": tags,
                    "image_url": str(row["image_url"]),
                    # Additional fields for quiz features
                    "category": category,
                    "color": color,
                    "size": "M",  # You would extract this from product data
                }
            )

        logger.info(f"📁 Loaded {len(catalog)} items from {csv_path}")
        return catalog

    except FileNotFoundError:
        logger.warning(f"📁 CSV file {csv_path} not found, using fallback catalog")
        return get_fallback_catalog()
    except Exception as e:
        logger.error(f"📁 Error loading CSV {csv_path}: {e}")
        return get_fallback_catalog()


def get_fallback_catalog():
    """Fallback catalog with quiz feature fields."""
    return [
        {
            "id": "test_1",
            "brand": "Zara",
            "title": "White Cotton T-Shirt",
            "price": 29.99,
            "tags": ["casual", "cotton", "white"],
            "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
            "category": "shirt",
            "color": "white",
            "size": "M",
        },
        {
            "id": "test_2",
            "brand": "H&M",
            "title": "Blue Denim Jeans",
            "price": 49.99,
            "tags": ["denim", "casual", "blue"],
            "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
            "category": "pants",
            "color": "blue",
            "size": "M",
        },
        {
            "id": "test_3",
            "brand": "Nike",
            "title": "Black Running Shoes",
            "price": 89.99,
            "tags": ["athletic", "running", "black"],
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            "category": "shoes",
            "color": "black",
            "size": "M",
        },
        {
            "id": "test_5",
            "brand": "Uniqlo",
            "title": "Gray Hoodie",
            "price": 39.99,
            "tags": ["casual", "hoodie", "gray"],
            "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400",
            "category": "jacket",
            "color": "gray",
            "size": "M",
        },
    ]


def quiz_features_to_vector(quiz: QuizFeatures) -> List[float]:
    """Convert quiz features to numerical vector."""

    features = []

    # Size features (normalize to 0-1)
    size_mapping = {"XS": 0, "S": 0.25, "M": 0.5, "L": 0.75, "XL": 1.0}
    features.append(size_mapping.get(quiz.size, 0.5))

    # Category features (one-hot encoding)
    categories = ["shirt", "pants", "shoes", "dress", "jacket"]
    for cat in categories:
        features.append(1.0 if cat in quiz.preferred_categories else 0.0)

    # Color features (one-hot encoding)
    colors = ["black", "white", "blue", "red", "gray"]
    for color in colors:
        features.append(1.0 if color in quiz.preferred_colors else 0.0)

    # Price feature (normalized)
    features.append(min(quiz.max_price / 200.0, 1.0) if quiz.max_price else 0.5)

    # Brand features (one-hot encoding)
    brands = ["zara", "hm", "nike", "adidas", "uniqlo"]
    for brand in brands:
        features.append(1.0 if brand in quiz.preferred_brands else 0.0)

    return features


def initialize_system():
    """Initialize the hybrid recommendation system."""
    global hybrid_recommender

    logger.info("🚀 Initializing Hybrid Fashion Recommender System...")

    # Load catalog
    catalog = load_catalog_from_csv()
    catalog_df = pd.DataFrame(catalog)

    # Initialize hybrid recommender
    hybrid_recommender = HybridFashionRecommender()

    # Build the system
    stats = hybrid_recommender.build_system(catalog_df)

    logger.info(f"✅ Hybrid system initialized: {stats}")


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    initialize_system()


@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "message": "Hybrid Fashion Recommender API",
        "status": "ready",
        "features": {
            "quiz_recommendations": "User preference based",
            "visual_recommendations": "ResNet50 + cosine similarity",
            "hybrid_recommendations": "Combined approach",
            "catalog_size": len(hybrid_recommender.catalog_df)
            if hybrid_recommender
            else 0,
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "hybrid_recommender": hybrid_recommender is not None,
        "visual_index": hybrid_recommender.visual_index is not None
        if hybrid_recommender
        else False,
        "quiz_features": hybrid_recommender.quiz_features_matrix is not None
        if hybrid_recommender
        else False,
    }


@app.post("/recommend", response_model=List[RecommendationResponse])
async def get_recommendations(request: HybridSearchRequest):
    """Get hybrid recommendations based on quiz features and/or visual similarity."""

    if not hybrid_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        logger.info(f"🔍 Processing hybrid recommendation request")

        # Convert quiz features to vector if provided
        user_quiz_features = None
        if request.quiz_features:
            user_quiz_features = quiz_features_to_vector(request.quiz_features)
            logger.info(f"📋 Quiz features: {request.quiz_features}")

        # Get hybrid recommendations
        results = hybrid_recommender.get_hybrid_recommendations(
            user_quiz_features=user_quiz_features,
            image_url=request.image_url,
            quiz_weight=request.quiz_weight,
            visual_weight=request.visual_weight,
            k=request.k,
        )

        # Convert to response format
        recommendations = [
            RecommendationResponse(
                rank=result["rank"],
                id=result["id"],
                score=result["score"],
                brand=result["brand"],
                title=result["title"],
                price=result["price"],
                tags=result.get("tags", []),
                image_url=result["image_url"],
                recommendation_type=result["recommendation_type"],
            )
            for result in results
        ]

        logger.info(f"✅ Found {len(recommendations)} recommendations")
        return recommendations

    except Exception as e:
        logger.error(f"❌ Recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@app.post("/recommend/quiz", response_model=List[RecommendationResponse])
async def get_quiz_recommendations(quiz_features: QuizFeatures, k: int = 10):
    """Get recommendations based only on quiz features."""

    if not hybrid_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        logger.info(f"📋 Processing quiz-only recommendation")

        user_quiz_features = quiz_features_to_vector(quiz_features)
        results = hybrid_recommender.get_quiz_recommendations(user_quiz_features, k=k)

        recommendations = [
            RecommendationResponse(
                rank=result["rank"],
                id=result["id"],
                score=result["score"],
                brand=result["brand"],
                title=result["title"],
                price=result["price"],
                tags=result.get("tags", []),
                image_url=result["image_url"],
                recommendation_type=result["recommendation_type"],
            )
            for result in results
        ]

        return recommendations

    except Exception as e:
        logger.error(f"❌ Quiz recommendation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Quiz recommendation failed: {str(e)}"
        )


@app.post("/recommend/visual", response_model=List[RecommendationResponse])
async def get_visual_recommendations(image_url: str, k: int = 10):
    """Get recommendations based only on visual similarity."""

    if not hybrid_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        logger.info(f"🖼️ Processing visual-only recommendation")

        results = hybrid_recommender.get_visual_recommendations(image_url, k=k)

        recommendations = [
            RecommendationResponse(
                rank=result["rank"],
                id=result["id"],
                score=result["score"],
                brand=result["brand"],
                title=result["title"],
                price=result["price"],
                tags=result.get("tags", []),
                image_url=result["image_url"],
                recommendation_type=result["recommendation_type"],
            )
            for result in results
        ]

        return recommendations

    except Exception as e:
        logger.error(f"❌ Visual recommendation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Visual recommendation failed: {str(e)}"
        )


@app.get("/demo/quiz")
async def demo_quiz_search():
    """Demo endpoint for quiz-based recommendations."""
    demo_quiz = QuizFeatures(
        size="M",
        preferred_categories=["shirt"],
        preferred_colors=["white"],
        max_price=50.0,
        preferred_brands=["zara"],
    )

    results = await get_quiz_recommendations(demo_quiz, k=3)
    return {"quiz_features": demo_quiz, "results": results}


@app.get("/demo/visual")
async def demo_visual_search():
    """Demo endpoint for visual-based recommendations."""
    demo_url = "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=400"

    results = await get_visual_recommendations(demo_url, k=3)
    return {"query_image": demo_url, "results": results}


@app.get("/demo/hybrid")
async def demo_hybrid_search():
    """Demo endpoint for hybrid recommendations."""
    demo_request = HybridSearchRequest(
        quiz_features=QuizFeatures(
            size="M",
            preferred_categories=["shirt"],
            preferred_colors=["white"],
            max_price=50.0,
            preferred_brands=["zara"],
        ),
        image_url="https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=400",
        quiz_weight=0.6,
        visual_weight=0.4,
        k=5,
    )

    results = await get_recommendations(demo_request)
    return {"request": demo_request, "results": results}


if __name__ == "__main__":
    print("🚀 Starting Hybrid Fashion Recommender API Server...")
    print("📝 API Documentation: http://localhost:8002/docs")
    print("🔍 Demo endpoints:")
    print("   Quiz only: http://localhost:8002/demo/quiz")
    print("   Visual only: http://localhost:8002/demo/visual")
    print("   Hybrid: http://localhost:8002/demo/hybrid")
    print("💡 Use Ctrl+C to stop the server")

    uvicorn.run(
        "hybrid_api:app", host="0.0.0.0", port=8002, reload=False, log_level="info"
    )

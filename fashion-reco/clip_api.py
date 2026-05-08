#!/usr/bin/env python3
"""
CLIP-Based Fashion Recommender API
Perfect solution for your quiz + visual features!

This API handles:
1. Quiz-based recommendations (text descriptions)
2. Visual-based recommendations (image similarity)
3. Hybrid recommendations (both combined)
"""

import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from clip_recommender import CLIPFashionRecommender

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CLIP Fashion Recommender API",
    description="Fashion recommendations using CLIP - handles both quiz features and visual similarity",
    version="3.0.0",
)

# Global variables
clip_recommender = None


# Pydantic models for API
class QuizFeatures(BaseModel):
    """User preferences from quiz."""

    size: Optional[str] = "M"
    preferred_categories: List[str] = ["shirt"]
    preferred_colors: List[str] = ["white"]
    max_price: Optional[float] = 100.0
    preferred_brands: List[str] = ["zara"]
    preferred_styles: List[str] = ["casual"]


class BrandSearchRequest(BaseModel):
    """Request for brand-based recommendations."""

    brand_name: str
    category: Optional[str] = None  # e.g., "shirt", "pants", "shoes"
    style: Optional[str] = None  # e.g., "casual", "formal", "sporty"
    k: int = 10


class HybridRequest(BaseModel):
    """Request for hybrid recommendations."""

    quiz_features: Optional[QuizFeatures] = None
    image_url: Optional[str] = None
    quiz_weight: float = 0.5
    visual_weight: float = 0.5
    k: int = 10


class RecommendationResponse(BaseModel):
    """Recommendation response."""

    rank: int
    id: str
    brand: str
    title: str
    price: float
    score: float
    image_url: str
    recommendation_type: str


def load_catalog_from_csv(csv_path: str = "catalog.csv"):
    """Load fashion catalog from CSV file."""
    try:
        df = pd.read_csv(csv_path)

        catalog = []
        for _, row in df.iterrows():
            # Handle tags
            tags = []
            if "tags" in df.columns and not pd.isna(row.get("tags")):
                tags_value = row["tags"]
                if isinstance(tags_value, str):
                    tags = [tag.strip() for tag in tags_value.split(",")]

            # Add category and color info for better text descriptions
            category = "clothing"
            title_lower = str(row["title"]).lower()
            if any(word in title_lower for word in ["shirt", "t-shirt", "blouse"]):
                category = "shirt"
            elif any(word in title_lower for word in ["jean", "pant", "trouser"]):
                category = "pants"
            elif any(word in title_lower for word in ["shoe", "sneaker", "boot"]):
                category = "shoes"
            elif any(word in title_lower for word in ["dress", "gown"]):
                category = "dress"
            elif any(word in title_lower for word in ["jacket", "hoodie", "coat"]):
                category = "jacket"

            catalog.append(
                {
                    "id": str(row["id"]),
                    "brand": str(row["brand"]),
                    "title": str(row["title"]),
                    "price": float(row["price"]),
                    "tags": tags,
                    "image_url": str(row["image_url"]),
                    "category": category,
                }
            )

        logger.info(f"📁 Loaded {len(catalog)} items from {csv_path}")
        return catalog

    except FileNotFoundError:
        logger.warning(f"📁 CSV file {csv_path} not found")
        raise HTTPException(
            status_code=404, detail=f"Catalog file {csv_path} not found"
        )
    except Exception as e:
        logger.error(f"📁 Error loading CSV {csv_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load catalog: {str(e)}")


def initialize_system():
    """Initialize the CLIP recommendation system."""
    global clip_recommender

    logger.info("🚀 Initializing CLIP Fashion Recommender System...")

    try:
        # Load catalog
        catalog = load_catalog_from_csv()
        catalog_df = pd.DataFrame(catalog)

        # Initialize CLIP recommender
        clip_recommender = CLIPFashionRecommender()

        # Build index
        clip_recommender.build_catalog_index(catalog_df)

        logger.info("✅ CLIP system initialized successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    initialize_system()


@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "message": "CLIP Fashion Recommender API",
        "status": "ready",
        "features": {
            "quiz_recommendations": "Natural language processing of user preferences",
            "visual_recommendations": "CLIP visual similarity",
            "hybrid_recommendations": "Combined text and visual matching",
            "model": "OpenAI CLIP ViT-B/32",
            "catalog_size": len(clip_recommender.catalog_df) if clip_recommender else 0,
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "clip_recommender": clip_recommender is not None,
        "catalog_ready": clip_recommender.catalog_embeddings is not None
        if clip_recommender
        else False,
        "embedding_dimension": clip_recommender.catalog_embeddings.shape[1]
        if clip_recommender and clip_recommender.catalog_embeddings is not None
        else 0,
    }


@app.post("/recommend/brand", response_model=List[RecommendationResponse])
async def brand_recommendations(request: BrandSearchRequest):
    """Get recommendations based on brand name (with optional category/style filters)."""

    if not clip_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        logger.info(f"🏷️ Processing brand-based recommendation: {request.brand_name}")

        # Create text description from brand search
        text_parts = [request.brand_name, "brand"]

        if request.category:
            text_parts.append(request.category)

        if request.style:
            text_parts.append(request.style)

        # Create natural language query
        search_text = f"{' '.join(text_parts)} fashion clothing"

        logger.info(f"📝 Brand search text: '{search_text}'")

        # Use CLIP text search
        text_embedding = clip_recommender.encode_text(search_text)

        # Calculate similarities
        similarities = np.dot(clip_recommender.catalog_embeddings, text_embedding)

        # Get top k results
        top_indices = np.argsort(similarities)[::-1][: request.k]

        results = []
        for i, idx in enumerate(top_indices):
            if idx < len(clip_recommender.catalog_df):
                item = clip_recommender.catalog_df.iloc[idx]
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

        recommendations = [
            RecommendationResponse(
                rank=result["rank"],
                id=result["id"],
                brand=result["brand"],
                title=result["title"],
                price=result["price"],
                score=result["score"],
                image_url=result["image_url"],
                recommendation_type=result["recommendation_type"],
            )
            for result in results
        ]

        return recommendations

    except Exception as e:
        logger.error(f"❌ Brand recommendation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Brand recommendation failed: {str(e)}"
        )


@app.post("/recommend/quiz", response_model=List[RecommendationResponse])
async def quiz_recommendations(quiz_features: QuizFeatures, k: int = 10):
    """Get recommendations based on quiz features (converted to text)."""

    if not clip_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        logger.info("📋 Processing quiz-based recommendation")

        results = clip_recommender.search_by_quiz(quiz_features.dict(), k=k)

        recommendations = [
            RecommendationResponse(
                rank=result["rank"],
                id=result["id"],
                brand=result["brand"],
                title=result["title"],
                price=result["price"],
                score=result["score"],
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
async def visual_recommendations(image_url: str, k: int = 10):
    """Get recommendations based on visual similarity."""

    if not clip_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        logger.info("🖼️ Processing visual-based recommendation")

        results = clip_recommender.search_by_image(image_url, k=k)

        recommendations = [
            RecommendationResponse(
                rank=result["rank"],
                id=result["id"],
                brand=result["brand"],
                title=result["title"],
                price=result["price"],
                score=result["score"],
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


@app.post("/recommend/hybrid", response_model=List[RecommendationResponse])
async def hybrid_recommendations(request: HybridRequest):
    """Get hybrid recommendations combining quiz and visual features."""

    if not clip_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    if not request.quiz_features and not request.image_url:
        raise HTTPException(
            status_code=400, detail="Either quiz_features or image_url must be provided"
        )

    try:
        logger.info("🔄 Processing hybrid recommendation")

        quiz_dict = request.quiz_features.dict() if request.quiz_features else None

        results = clip_recommender.search_hybrid(
            quiz_features=quiz_dict,
            image_url=request.image_url,
            quiz_weight=request.quiz_weight,
            visual_weight=request.visual_weight,
            k=request.k,
        )

        recommendations = [
            RecommendationResponse(
                rank=result["rank"],
                id=result["id"],
                brand=result["brand"],
                title=result["title"],
                price=result["price"],
                score=result["score"],
                image_url=result["image_url"],
                recommendation_type=result["recommendation_type"],
            )
            for result in results
        ]

        return recommendations

    except Exception as e:
        logger.error(f"❌ Hybrid recommendation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Hybrid recommendation failed: {str(e)}"
        )


@app.get("/demo/brand")
async def demo_brand():
    """Demo brand-based recommendations."""
    demo_request = BrandSearchRequest(
        brand_name="Nike", category="shoes", style="sporty", k=3
    )

    results = await brand_recommendations(demo_request)
    return {"request": demo_request, "results": results}


@app.get("/demo/brand-simple")
async def demo_brand_simple():
    """Demo simple brand search (brand name only)."""
    demo_request = BrandSearchRequest(brand_name="Zara", k=3)

    results = await brand_recommendations(demo_request)
    return {"request": demo_request, "results": results}


@app.get("/demo/quiz")
async def demo_quiz():
    """Demo quiz-based recommendations."""
    demo_quiz = QuizFeatures(
        size="M",
        preferred_categories=["shirt"],
        preferred_colors=["white"],
        max_price=50.0,
        preferred_brands=["zara"],
        preferred_styles=["casual"],
    )

    results = await quiz_recommendations(demo_quiz, k=3)
    return {"query": demo_quiz, "results": results}


@app.get("/demo/visual")
async def demo_visual():
    """Demo visual-based recommendations."""
    demo_url = "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"

    results = await visual_recommendations(demo_url, k=3)
    return {"query_image": demo_url, "results": results}


@app.get("/demo/hybrid")
async def demo_hybrid():
    """Demo hybrid recommendations."""
    demo_request = HybridRequest(
        quiz_features=QuizFeatures(
            size="M",
            preferred_categories=["shirt"],
            preferred_colors=["white"],
            max_price=50.0,
            preferred_brands=["zara"],
            preferred_styles=["casual"],
        ),
        image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
        quiz_weight=0.6,
        visual_weight=0.4,
        k=3,
    )

    results = await hybrid_recommendations(demo_request)
    return {"request": demo_request, "results": results}


if __name__ == "__main__":
    print("🚀 Starting CLIP Fashion Recommender API Server...")
    print("📝 API Documentation: http://localhost:8003/docs")
    print("🔍 Demo endpoints:")
    print("   Brand only: http://localhost:8003/demo/brand-simple")
    print("   Brand + filters: http://localhost:8003/demo/brand")
    print("   Quiz only: http://localhost:8003/demo/quiz")
    print("   Visual only: http://localhost:8003/demo/visual")
    print("   Hybrid: http://localhost:8003/demo/hybrid")
    print("💡 Use Ctrl+C to stop the server")

    uvicorn.run(
        "clip_api:app", host="0.0.0.0", port=8003, reload=False, log_level="info"
    )

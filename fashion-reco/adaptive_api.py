#!/usr/bin/env python3
"""
Adaptive Fashion Recommender API with Like/Dislike Feedback
Implements RLHF (Reinforcement Learning from Human Feedback)

Features:
1. 👍/👎 Like/Dislike feedback endpoints
2. 🧠 Adaptive recommendations based on user history
3. ⏰ Temporal decay - negative feedback weakens over time
4. 👤 Individual user profiles and preference learning
5. 💾 Persistent feedback storage
"""

import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from adaptive_recommender import AdaptiveFashionRecommender

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Adaptive Fashion Recommender API",
    description="Fashion recommendations with like/dislike feedback and adaptive learning",
    version="4.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Alternative port
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global variables
adaptive_recommender = None


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
    category: Optional[str] = None
    style: Optional[str] = None
    k: int = 10


class AdaptiveSearchRequest(BaseModel):
    """Request for adaptive recommendations."""

    user_id: str
    quiz_features: Optional[QuizFeatures] = None
    image_url: Optional[str] = None
    brand_name: Optional[str] = None
    category: Optional[str] = None
    adaptation_strength: float = 0.5  # How much to adapt based on user feedback (0-1)
    k: int = 10
    exclude_items: Optional[List[str]] = []  # Items to exclude from recommendations


class FeedbackRequest(BaseModel):
    """Request to add user feedback."""

    user_id: str
    item_id: str
    feedback: str  # "like" or "dislike"


class RecommendationResponse(BaseModel):
    """Adaptive recommendation response."""

    rank: int
    id: str
    brand: str
    title: str
    price: float
    score: float
    base_score: Optional[float] = None  # Original score before adaptation
    image_url: str
    recommendation_type: str
    user_feedback: Optional[dict] = None  # Previous feedback for this item
    is_personalized: bool = False


def load_catalog_from_csv(csv_path: str = "catalog.csv"):
    """Load fashion catalog from CSV file."""
    try:
        # Try filtered catalog first, fallback to original
        filtered_path = csv_path.replace(".csv", "_filtered.csv")
        if Path(filtered_path).exists():
            logger.info(f"📁 Using filtered catalog: {filtered_path}")
            csv_path = filtered_path

        df = pd.read_csv(csv_path)

        logger.info(f"📁 CSV columns found: {list(df.columns)}")

        catalog = []
        for _, row in df.iterrows():
            # Handle tags
            tags = []
            if "tags" in df.columns and not pd.isna(row.get("tags")):
                tags_value = row["tags"]
                if isinstance(tags_value, str):
                    tags = [tag.strip() for tag in tags_value.split(",")]

            # Map CSV columns to expected format
            # Your CSV: product_id, name, category, price, brand, pattern, available_sizes, tags, image_url
            # Expected: id, title, brand, price, image_url, tags

            product_id = str(row.get("product_id", row.get("id", "")))
            title = str(row.get("name", row.get("title", "")))
            brand = str(row.get("brand", ""))
            price = float(row.get("price", 0))
            image_url = str(row.get("image_url", ""))

            # Add category and color info for better text descriptions
            category = "clothing"
            title_lower = title.lower()
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
                    "id": product_id,
                    "brand": brand,
                    "title": title,
                    "price": price,
                    "tags": tags,
                    "image_url": image_url,
                    "category": category,
                }
            )

        logger.info(f"📁 Loaded {len(catalog)} items from {csv_path}")
        logger.info(f"📁 Sample item: {catalog[0] if catalog else 'No items loaded'}")
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
    """Initialize the adaptive recommendation system."""
    global adaptive_recommender

    logger.info("🚀 Initializing Adaptive Fashion Recommender System...")

    try:
        # Load catalog
        catalog = load_catalog_from_csv()
        catalog_df = pd.DataFrame(catalog)

        # Initialize adaptive recommender
        adaptive_recommender = AdaptiveFashionRecommender()

        # Build index
        adaptive_recommender.build_catalog_index(catalog_df)

        # Try to load existing user profiles
        adaptive_recommender.load_user_profiles()

        logger.info("✅ Adaptive system initialized successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    initialize_system()


@app.on_event("shutdown")
async def shutdown_event():
    """Save user profiles on shutdown."""
    if adaptive_recommender:
        adaptive_recommender.save_user_profiles()
        logger.info("💾 Saved user profiles on shutdown")


@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "message": "Adaptive Fashion Recommender API",
        "status": "ready",
        "features": {
            "adaptive_learning": "RLHF with like/dislike feedback",
            "temporal_decay": "Negative feedback weakens over time",
            "user_profiles": "Individual preference learning",
            "feedback_storage": "Persistent user feedback history",
            "model": "OpenAI CLIP + Adaptive Learning",
            "catalog_size": len(adaptive_recommender.catalog_df)
            if adaptive_recommender
            else 0,
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "adaptive_recommender": adaptive_recommender is not None,
        "catalog_ready": adaptive_recommender.catalog_embeddings is not None
        if adaptive_recommender
        else False,
        "total_users": len(adaptive_recommender.user_profiles)
        if adaptive_recommender
        else 0,
    }


@app.post("/recommend/adaptive", response_model=List[RecommendationResponse])
async def adaptive_recommendations(request: AdaptiveSearchRequest):
    """Get adaptive recommendations with priority-based input weighting."""

    if not adaptive_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        logger.info(
            f"🎯 Processing PRIORITY adaptive recommendation for user {request.user_id}"
        )

        # Use new priority-based recommendation system
        results = adaptive_recommender.get_priority_adaptive_recommendations(
            user_id=request.user_id,
            image_url=request.image_url,  # Highest priority
            brand_name=request.brand_name,  # Medium priority
            category=request.category,  # Lower priority
            quiz_features=request.quiz_features.dict()
            if request.quiz_features
            else None,  # Fallback
            k=request.k * 2,  # Get more results to account for filtering
            adaptation_strength=request.adaptation_strength,
        )

        # Filter out excluded items (already seen/disliked items)
        excluded_ids = set(request.exclude_items or [])
        filtered_results = []

        for result in results:
            if result["id"] not in excluded_ids:
                filtered_results.append(result)
                if len(filtered_results) >= request.k:
                    break

        logger.info(f"🚫 Filtered out {len(excluded_ids)} already seen items")
        logger.info(f"✅ Returning {len(filtered_results)} priority recommendations")

        # Convert to response format
        recommendations = [
            RecommendationResponse(
                rank=result["rank"],
                id=result["id"],
                brand=result["brand"],
                title=result["title"],
                price=result["price"],
                score=result["score"],
                base_score=result.get("base_score"),
                image_url=result["image_url"],
                recommendation_type=result["recommendation_type"],
                user_feedback=result.get("user_feedback"),
                is_personalized=result.get("is_personalized", False),
            )
            for result in filtered_results
        ]

        logger.info(
            f"✅ Found {len(recommendations)} NEW priority adaptive recommendations for user {request.user_id}"
        )
        return recommendations

    except Exception as e:
        logger.error(f"❌ Priority adaptive recommendation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Priority adaptive recommendation failed: {str(e)}"
        )


@app.get("/priority_adaptive_recommendations", response_model=dict)
async def priority_adaptive_recommendations_get(
    user_id: str,
    count: int = 10,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    image_url: Optional[str] = None,
):
    """GET endpoint for priority adaptive recommendations (for test scripts)."""

    if not adaptive_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        logger.info(
            f"🎯 Processing GET priority adaptive recommendation for user {user_id}"
        )

        # Use new priority-based recommendation system
        results = adaptive_recommender.get_priority_adaptive_recommendations(
            user_id=user_id,
            image_url=image_url,
            brand_name=brand,
            category=category,
            quiz_features=None,
            k=count,
            adaptation_strength=0.7,
        )

        # Convert to response format
        recommendations = []
        for result in results:
            recommendations.append(
                {
                    "id": result["id"],
                    "brand": result["brand"],
                    "name": result["title"],
                    "price": result["price"],
                    "score": result["score"],
                    "base_score": result.get("base_score"),
                    "image_url": result["image_url"],
                    "recommendation_type": result["recommendation_type"],
                    "user_feedback": result.get("user_feedback"),
                    "is_personalized": result.get("is_personalized", False),
                    "lift": result.get("lift", 0.0),
                }
            )

        logger.info(
            f"✅ Found {len(recommendations)} priority adaptive recommendations for user {user_id}"
        )

        return {
            "recommendations": recommendations,
            "user_id": user_id,
            "total_count": len(recommendations),
        }

    except Exception as e:
        logger.error(f"❌ Priority adaptive recommendation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Priority adaptive recommendation failed: {str(e)}"
        )


@app.post("/feedback")
async def add_feedback(request: FeedbackRequest):
    """Add user feedback (like/dislike) for a recommendation."""

    if not adaptive_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    if request.feedback not in ["like", "dislike"]:
        raise HTTPException(
            status_code=400, detail="Feedback must be 'like' or 'dislike'"
        )

    try:
        logger.info(
            f"📝 Adding {request.feedback} feedback from user {request.user_id} for item {request.item_id}"
        )

        # Find item in catalog to get embedding
        item_rows = adaptive_recommender.catalog_df[
            adaptive_recommender.catalog_df["id"] == request.item_id
        ]
        if item_rows.empty:
            raise HTTPException(
                status_code=404, detail=f"Item {request.item_id} not found in catalog"
            )

        # Get item embedding from catalog index
        item_index = item_rows.index[0]
        item_embedding = adaptive_recommender.catalog_embeddings[item_index]

        # Add feedback
        adaptive_recommender.add_feedback(
            user_id=request.user_id,
            item_id=request.item_id,
            feedback=request.feedback,
            item_embedding=item_embedding,
        )

        # Get updated user stats
        user_stats = adaptive_recommender.get_user_stats(request.user_id)

        return {
            "status": "success",
            "message": f"Added {request.feedback} feedback for item {request.item_id}",
            "user_stats": user_stats,
        }

    except Exception as e:
        logger.error(f"❌ Failed to add feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add feedback: {str(e)}")


@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user's feedback statistics and preference profile."""

    if not adaptive_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        stats = adaptive_recommender.get_user_stats(user_id)
        return stats

    except Exception as e:
        logger.error(f"❌ Failed to get user stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get user stats: {str(e)}"
        )


@app.get("/user_stats/{user_id}")
async def get_user_stats_alt(user_id: str):
    """Alternative endpoint for user stats (for test scripts)."""
    return await get_user_stats(user_id)


@app.get("/users/{user_id}/feedback")
async def get_user_feedback_history(user_id: str, limit: int = 50):
    """Get user's feedback history."""

    if not adaptive_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        profile = adaptive_recommender.user_profiles[user_id]

        # Get recent feedback
        feedback_history = profile["feedback_history"][-limit:]

        # Convert to response format
        history = []
        for feedback in reversed(feedback_history):  # Most recent first
            history.append(
                {
                    "item_id": feedback["item_id"],
                    "feedback": feedback["feedback"],
                    "timestamp": feedback["timestamp"].isoformat(),
                    "item_title": feedback["item_data"]["title"]
                    if feedback["item_data"]
                    else "Unknown",
                    "item_brand": feedback["item_data"]["brand"]
                    if feedback["item_data"]
                    else "Unknown",
                }
            )

        return {
            "user_id": user_id,
            "feedback_history": history,
            "total_feedback": len(profile["feedback_history"]),
        }

    except Exception as e:
        logger.error(f"❌ Failed to get feedback history: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get feedback history: {str(e)}"
        )


@app.post("/users/{user_id}/reset")
async def reset_user_profile(user_id: str):
    """Reset user's feedback profile (for testing/debugging)."""

    if not adaptive_recommender:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        if user_id in adaptive_recommender.user_profiles:
            del adaptive_recommender.user_profiles[user_id]
            logger.info(f"🔄 Reset profile for user {user_id}")

            return {"status": "success", "message": f"Reset profile for user {user_id}"}
        else:
            return {"status": "info", "message": f"No profile found for user {user_id}"}

    except Exception as e:
        logger.error(f"❌ Failed to reset user profile: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to reset user profile: {str(e)}"
        )


# Demo endpoints
@app.get("/demo/adaptive")
async def demo_adaptive():
    """Demo adaptive recommendations."""
    demo_request = AdaptiveSearchRequest(
        user_id="demo_user", brand_name="Nike", adaptation_strength=0.6, k=3
    )

    results = await adaptive_recommendations(demo_request)

    return {
        "request": demo_request,
        "results": results,
        "instructions": "Use POST /feedback to like/dislike items, then call this endpoint again to see adaptation",
    }


@app.get("/demo/feedback-flow")
async def demo_feedback_flow():
    """Demo the complete feedback learning flow."""

    instructions = {
        "step_1": "GET /demo/adaptive - Get initial recommendations for demo_user",
        "step_2": "POST /feedback - Like/dislike some items",
        "step_3": "GET /demo/adaptive - See how recommendations adapted",
        "step_4": "GET /users/demo_user/stats - View learning progress",
        "example_feedback": {
            "user_id": "demo_user",
            "item_id": "1",  # Use actual item ID from recommendations
            "feedback": "like",  # or "dislike"
        },
    }

    return instructions


if __name__ == "__main__":
    print("🚀 Starting Adaptive Fashion Recommender API Server...")
    print("📝 API Documentation: http://localhost:8004/docs")
    print("🔍 Demo endpoints:")
    print("   Adaptive demo: http://localhost:8004/demo/adaptive")
    print("   Feedback flow: http://localhost:8004/demo/feedback-flow")
    print("💡 Key features:")
    print("   👍👎 Like/dislike feedback: POST /feedback")
    print("   🧠 Adaptive recommendations: POST /recommend/adaptive")
    print("   📊 User stats: GET /users/{user_id}/stats")
    print("   📈 Feedback history: GET /users/{user_id}/feedback")
    print("💡 Use Ctrl+C to stop the server")

    uvicorn.run(
        "adaptive_api:app", host="0.0.0.0", port=8004, reload=False, log_level="info"
    )

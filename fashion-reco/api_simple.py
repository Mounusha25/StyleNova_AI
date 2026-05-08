#!/usr/bin/env python3
"""
Simple FastAPI test server for Fashion Recommender with scikit-learn
Supports loading catalog from CSV file
"""

import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from models.extractor import ResNet50FeatureExtractor
from indexing.sklearn_index import SklearnIndex

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Fashion Recommender API",
    description="Simple fashion recommendation API using ResNet50 + scikit-learn",
    version="1.0.0",
)

# Global variables
feature_extractor = None
similarity_index = None


# Pydantic models for API
class SearchRequest(BaseModel):
    image_url: str
    k: int = 10


class RecommendationResponse(BaseModel):
    rank: int
    id: str
    score: float
    brand: str
    title: str
    price: float
    tags: list
    image_url: str


def load_catalog_from_csv(csv_path: str = "catalog.csv"):
    """Load fashion catalog from CSV file."""
    try:
        # Load CSV using pandas
        df = pd.read_csv(csv_path)

        # Convert to list of dictionaries
        catalog = []
        for _, row in df.iterrows():
            # Handle tags - make it optional
            tags = []
            if "tags" in df.columns and not pd.isna(row.get("tags")):
                tags_value = row["tags"]
                if isinstance(tags_value, str):
                    tags = [tag.strip() for tag in tags_value.split(",")]

            catalog.append(
                {
                    "id": str(row["id"]),
                    "brand": str(row["brand"]),
                    "title": str(row["title"]),
                    "price": float(row["price"]),
                    "tags": tags,
                    "image_url": str(row["image_url"]),
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
    """Fallback catalog if CSV loading fails."""
    return [
        {
            "id": "test_1",
            "brand": "Zara",
            "title": "White Cotton T-Shirt",
            "price": 29.99,
            "tags": ["casual", "cotton", "white"],
            "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
        },
        {
            "id": "test_2",
            "brand": "H&M",
            "title": "Blue Denim Jeans",
            "price": 49.99,
            "tags": ["denim", "casual", "blue"],
            "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
        },
        {
            "id": "test_3",
            "brand": "Nike",
            "title": "Black Running Shoes",
            "price": 89.99,
            "tags": ["athletic", "running", "black"],
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        },
        {
            "id": "test_5",
            "brand": "Uniqlo",
            "title": "Gray Hoodie",
            "price": 39.99,
            "tags": ["casual", "hoodie", "gray"],
            "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400",
        },
    ]


def initialize_system():
    """Initialize the feature extractor and similarity index."""
    global feature_extractor, similarity_index

    logger.info("🚀 Initializing Fashion Recommender System...")

    # Initialize feature extractor
    feature_extractor = ResNet50FeatureExtractor()
    logger.info("✅ Feature extractor initialized")

    # Load catalog from CSV
    catalog = load_catalog_from_csv()

    # Process catalog and build index
    logger.info("📊 Processing catalog...")
    embeddings_data = []

    for item in catalog:
        try:
            logger.info(f"  Processing: {item['title']}")
            features = feature_extractor.extract_from_url(item["image_url"])
            features = features.squeeze().numpy()

            embeddings_data.append(
                {
                    "id": item["id"],
                    "brand": item["brand"],
                    "title": item["title"],
                    "price": item["price"],
                    "tags": item["tags"],
                    "image_url": item["image_url"],
                    "embedding": features.tolist(),
                }
            )

        except Exception as e:
            logger.warning(f"  Failed to process {item['title']}: {e}")
            continue

    # Build similarity index
    if embeddings_data:
        embeddings_df = pd.DataFrame(embeddings_data)
        similarity_index = SklearnIndex(dimension=2048, metric="cosine")
        similarity_index.build_index(embeddings_df)
        logger.info(f"✅ Index built with {len(embeddings_data)} items")
    else:
        raise RuntimeError("Failed to process any catalog items")


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    initialize_system()


@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "message": "Fashion Recommender API",
        "status": "ready",
        "features": {
            "feature_extraction": "ResNet50",
            "similarity_search": "scikit-learn cosine similarity",
            "catalog_size": len(similarity_index.embeddings_matrix)
            if similarity_index
            else 0,
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "feature_extractor": feature_extractor is not None,
        "similarity_index": similarity_index is not None,
        "index_stats": similarity_index.get_stats() if similarity_index else None,
    }


@app.post("/search", response_model=list[RecommendationResponse])
async def search_similar_items(request: SearchRequest):
    """Search for similar fashion items by image URL."""

    if not feature_extractor or not similarity_index:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        # Extract features from query image
        logger.info(f"🔍 Processing search request for: {request.image_url}")
        query_features = feature_extractor.extract_from_url(request.image_url)
        query_features = query_features.squeeze().numpy()

        # Search for similar items
        results = similarity_index.search(query_features, k=request.k)

        # Convert to response format
        recommendations = [
            RecommendationResponse(
                rank=result["rank"],
                id=result["id"],
                score=result["score"],
                brand=result["brand"],
                title=result["title"],
                price=result["price"],
                tags=result["tags"],
                image_url=result["image_url"],
            )
            for result in results
        ]

        logger.info(f"✅ Found {len(recommendations)} similar items")
        return recommendations

    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/catalog")
async def get_catalog():
    """Get the current catalog."""
    if not similarity_index:
        raise HTTPException(status_code=503, detail="System not initialized")

    # Load current catalog
    catalog = load_catalog_from_csv()
    return {"catalog": catalog, "stats": similarity_index.get_stats()}


@app.get("/demo")
async def demo_search():
    """Demo endpoint with a predefined search."""
    demo_url = "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=400"

    request = SearchRequest(image_url=demo_url, k=3)
    results = await search_similar_items(request)

    return {"query_image": demo_url, "results": results}


if __name__ == "__main__":
    print("🚀 Starting Fashion Recommender API Server...")
    print("📝 API Documentation will be available at: http://localhost:8001/docs")
    print("🔍 Try the demo endpoint: http://localhost:8001/demo")
    print("💡 Use Ctrl+C to stop the server")

    uvicorn.run(
        "api_simple:app", host="0.0.0.0", port=8001, reload=False, log_level="info"
    )

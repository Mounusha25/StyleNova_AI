import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from typing import List, Dict, Any
import logging
import time
from sklearn.neighbors import NearestNeighbors

logger = logging.getLogger(__name__)


class SklearnIndex:
    """Scikit-learn based similarity search index for fashion recommendations."""

    def __init__(self, dimension: int = 2048, metric: str = "cosine"):
        self.dimension = dimension
        self.metric = metric
        self.index = None
        self.id_map = None
        self.metadata_df = None
        self.embeddings_matrix = None
        self.build_time = None

    def build_index(self, embeddings_df: pd.DataFrame) -> None:
        """Build scikit-learn index from embeddings DataFrame."""

        if len(embeddings_df) == 0:
            raise ValueError("Cannot build index from empty DataFrame")

        # Extract embeddings matrix
        self.embeddings_matrix = np.array(embeddings_df["embedding"].tolist()).astype(
            "float32"
        )

        # Validate embeddings
        if self.embeddings_matrix.shape[1] != self.dimension:
            raise ValueError(
                f"Expected {self.dimension}D embeddings, got {self.embeddings_matrix.shape[1]}D"
            )

        logger.info("🔨 Building scikit-learn index...")
        logger.info(f"  📊 Metric: {self.metric}")
        logger.info(f"  📏 Dimension: {self.dimension}")
        logger.info(f"  🔢 Number of vectors: {self.embeddings_matrix.shape[0]}")

        start_time = time.time()

        # Create NearestNeighbors index
        # For cosine similarity, we need to normalize vectors first
        if self.metric == "cosine":
            # Normalize embeddings for cosine similarity
            from sklearn.preprocessing import normalize

            self.embeddings_matrix = normalize(
                self.embeddings_matrix, norm="l2", axis=1
            )
            # Use euclidean distance on normalized vectors (equivalent to cosine similarity)
            self.index = NearestNeighbors(
                n_neighbors=50, metric="euclidean", algorithm="auto"
            )
        else:
            self.index = NearestNeighbors(
                n_neighbors=50, metric=self.metric, algorithm="auto"
            )

        # Fit the index
        self.index.fit(self.embeddings_matrix)

        # Store metadata mapping
        self.id_map = embeddings_df["id"].tolist()
        self.metadata_df = embeddings_df[
            ["id", "brand", "title", "price", "tags", "image_url"]
        ].copy()

        self.build_time = time.time() - start_time

        logger.info(f"✅ Index built successfully in {self.build_time:.2f}s!")
        logger.info(f"  🔍 Total vectors in index: {len(self.embeddings_matrix)}")

    def search(self, query_embedding: np.ndarray, k: int = 12) -> List[Dict[str, Any]]:
        """Search for k most similar items."""

        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")

        # Ensure query is the right shape and type
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        query_embedding = query_embedding.astype("float32")

        # Validate query dimension
        if query_embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Query embedding dimension {query_embedding.shape[1]} doesn't match index dimension {self.dimension}"
            )

        # Normalize query for cosine similarity
        if self.metric == "cosine":
            from sklearn.preprocessing import normalize

            query_embedding = normalize(query_embedding, norm="l2", axis=1)

        # Search index
        k = min(
            k, len(self.embeddings_matrix)
        )  # Don't search for more items than we have
        distances, indices = self.index.kneighbors(query_embedding, n_neighbors=k)

        # Convert distances to similarity scores
        # For cosine similarity with normalized vectors: similarity = 1 - (euclidean_distance^2 / 2)
        if self.metric == "cosine":
            # Convert euclidean distances on normalized vectors to cosine similarity
            similarities = 1 - (distances[0] ** 2) / 2
        else:
            # For other metrics, convert distance to similarity (closer = higher score)
            similarities = 1 / (1 + distances[0])

        # Format results
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities, indices[0])):
            try:
                item_id = self.id_map[idx]
                metadata = self.metadata_df[self.metadata_df["id"] == item_id].iloc[0]

                results.append(
                    {
                        "rank": i + 1,
                        "id": item_id,
                        "score": float(similarity),
                        "brand": metadata["brand"],
                        "title": metadata["title"],
                        "price": float(metadata["price"]) if metadata["price"] else 0.0,
                        "tags": metadata["tags"],
                        "image_url": metadata["image_url"],
                    }
                )
            except Exception as e:
                logger.warning(f"Error formatting result for index {idx}: {e}")
                continue

        return results

    def save_index(self, index_path: Path, metadata_path: Path) -> None:
        """Save scikit-learn index and metadata to disk."""
        if self.index is None:
            raise ValueError("No index to save")

        # Ensure parent directories exist
        index_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        # Save index and embeddings
        index_data = {
            "index": self.index,
            "embeddings_matrix": self.embeddings_matrix,
            "metric": self.metric,
        }

        with open(index_path, "wb") as f:
            pickle.dump(index_data, f)

        # Save metadata
        metadata = {
            "id_map": self.id_map,
            "dimension": self.dimension,
            "metric": self.metric,
            "total_vectors": len(self.embeddings_matrix),
            "build_time": self.build_time,
            "created_at": time.time(),
        }

        with open(metadata_path, "wb") as f:
            pickle.dump(metadata, f)

        # Save metadata DataFrame
        self.metadata_df.to_parquet(metadata_path.with_suffix(".parquet"))

        logger.info(f"💾 Index saved to: {index_path}")
        logger.info(f"💾 Metadata saved to: {metadata_path}")

    def load_index(self, index_path: Path, metadata_path: Path) -> None:
        """Load scikit-learn index and metadata from disk."""

        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        # Load index and embeddings
        with open(index_path, "rb") as f:
            index_data = pickle.load(f)

        self.index = index_data["index"]
        self.embeddings_matrix = index_data["embeddings_matrix"]
        self.metric = index_data["metric"]

        # Load metadata
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)

        self.id_map = metadata["id_map"]
        self.dimension = metadata["dimension"]
        self.build_time = metadata.get("build_time")

        # Load metadata DataFrame
        parquet_path = metadata_path.with_suffix(".parquet")
        if parquet_path.exists():
            self.metadata_df = pd.read_parquet(parquet_path)
        else:
            logger.warning("Metadata DataFrame not found, some features may not work")

        logger.info(f"📂 Index loaded from: {index_path}")
        logger.info(f"📂 Metadata loaded from: {metadata_path}")
        logger.info(f"  🔍 Total vectors: {len(self.embeddings_matrix)}")
        logger.info(f"  📏 Dimension: {self.dimension}")
        logger.info(
            f"  🕐 Original build time: {self.build_time:.2f}s"
            if self.build_time
            else ""
        )

    def add_vectors(self, new_embeddings_df: pd.DataFrame) -> None:
        """Add new vectors to existing index (requires rebuilding with scikit-learn)."""
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")

        if len(new_embeddings_df) == 0:
            logger.warning("No new embeddings to add")
            return

        # Combine old and new data
        combined_df = pd.concat(
            [
                self.metadata_df,
                new_embeddings_df[
                    ["id", "brand", "title", "price", "tags", "image_url"]
                ],
            ],
            ignore_index=True,
        )

        # Add embeddings column
        old_embeddings = [emb for emb in self.embeddings_matrix]
        new_embeddings = new_embeddings_df["embedding"].tolist()
        combined_embeddings = old_embeddings + new_embeddings

        # Create new DataFrame with embeddings
        combined_df["embedding"] = combined_embeddings

        # Rebuild index
        self.build_index(combined_df)

        logger.info(f"➕ Added {len(new_embeddings_df)} new vectors to index (rebuilt)")
        logger.info(f"  🔍 Total vectors now: {len(self.embeddings_matrix)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        if self.index is None:
            return {"status": "not_built"}

        stats = {
            "status": "ready",
            "total_vectors": len(self.embeddings_matrix),
            "dimension": self.dimension,
            "metric": self.metric,
            "build_time": self.build_time,
        }

        if self.metadata_df is not None:
            stats.update(
                {
                    "unique_brands": self.metadata_df["brand"].nunique(),
                    "price_range": [
                        float(self.metadata_df["price"].min()),
                        float(self.metadata_df["price"].max()),
                    ],
                    "sample_brands": self.metadata_df["brand"]
                    .value_counts()
                    .head(5)
                    .to_dict(),
                }
            )

        return stats

    def validate_index(self) -> Dict[str, Any]:
        """Validate index integrity."""
        if self.index is None:
            return {"valid": False, "error": "Index not built"}

        try:
            # Check if index and metadata are consistent
            index_size = len(self.embeddings_matrix)
            id_map_size = len(self.id_map) if self.id_map else 0
            metadata_size = len(self.metadata_df) if self.metadata_df is not None else 0

            issues = []

            if index_size != id_map_size:
                issues.append(
                    f"Index size ({index_size}) != ID map size ({id_map_size})"
                )

            if index_size != metadata_size:
                issues.append(
                    f"Index size ({index_size}) != Metadata size ({metadata_size})"
                )

            # Test a simple search
            if index_size > 0:
                dummy_query = np.random.random((1, self.dimension)).astype("float32")
                distances, indices = self.index.kneighbors(
                    dummy_query, n_neighbors=min(1, index_size)
                )
                if len(indices[0]) == 0:
                    issues.append("Search test failed - no results returned")

            return {
                "valid": len(issues) == 0,
                "index_size": index_size,
                "id_map_size": id_map_size,
                "metadata_size": metadata_size,
                "issues": issues,
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

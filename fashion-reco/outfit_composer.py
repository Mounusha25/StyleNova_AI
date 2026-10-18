"""Compatibility-aware outfit composition over the validated product catalog."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


TOPS = {"top", "blouse", "sweater", "sports bra", "bodysuit"}
BOTTOMS = {"pants", "shorts", "skirt"}
FULL_BODY = {"dress", "mini dress", "maxi dress", "romper", "swimsuit", "bikini set"}
LAYERS = {"coat", "jacket", "blazer"}
FOOTWEAR = {"footwear"}
ACCESSORIES = {"bag", "accessory"}
NEUTRALS = {"black", "white", "gray", "grey", "beige", "brown", "cream", "navy"}
COLORS = NEUTRALS | {"red", "blue", "green", "pink", "yellow", "orange", "purple"}


@dataclass(frozen=True)
class Slot:
    name: str
    categories: frozenset[str]


def required_slots(category: str) -> list[Slot]:
    """Return complementary garment slots for an anchor category."""
    category = category.lower().strip()
    if category in TOPS:
        return [Slot("bottom", frozenset(BOTTOMS)), Slot("layer", frozenset(LAYERS)), Slot("shoes", frozenset(FOOTWEAR))]
    if category in BOTTOMS:
        return [Slot("top", frozenset(TOPS)), Slot("layer", frozenset(LAYERS)), Slot("shoes", frozenset(FOOTWEAR))]
    if category in FULL_BODY:
        return [Slot("layer", frozenset(LAYERS)), Slot("shoes", frozenset(FOOTWEAR)), Slot("accessory", frozenset(ACCESSORIES))]
    if category in LAYERS:
        return [Slot("base", frozenset(TOPS | FULL_BODY)), Slot("bottom", frozenset(BOTTOMS)), Slot("shoes", frozenset(FOOTWEAR))]
    if category in FOOTWEAR:
        return [Slot("base", frozenset(TOPS | FULL_BODY)), Slot("bottom", frozenset(BOTTOMS)), Slot("layer", frozenset(LAYERS))]
    if category in ACCESSORIES:
        return [Slot("base", frozenset(TOPS | FULL_BODY)), Slot("bottom", frozenset(BOTTOMS)), Slot("shoes", frozenset(FOOTWEAR))]
    return [Slot("base", frozenset(TOPS | FULL_BODY)), Slot("bottom", frozenset(BOTTOMS)), Slot("layer", frozenset(LAYERS))]


class OutfitComposer:
    """Build complete looks using category, semantic, color, and price compatibility."""

    def __init__(self, catalog: pd.DataFrame, embeddings: np.ndarray | None = None):
        self.catalog = self._normalize_catalog(catalog)
        descriptions = self.catalog.apply(self._description, axis=1).tolist()
        self.metadata_vectors = TfidfVectorizer(ngram_range=(1, 2)).fit_transform(descriptions)
        self.embeddings = self._normalize_embeddings(embeddings)

    @staticmethod
    def _normalize_catalog(catalog: pd.DataFrame) -> pd.DataFrame:
        normalized = catalog.rename(columns={"product_id": "id", "name": "title"}).copy()
        required = {"id", "title", "category", "brand", "price", "image_url"}
        missing = required - set(normalized.columns)
        if missing:
            raise ValueError(f"Catalog missing required columns: {sorted(missing)}")
        for column in ("id", "title", "category", "brand", "image_url"):
            normalized[column] = normalized[column].fillna("").astype(str)
        for column in ("pattern", "tags"):
            if column not in normalized:
                normalized[column] = ""
            normalized[column] = normalized[column].fillna("").astype(str)
        normalized["category"] = normalized["category"].str.lower().str.strip()
        normalized["price"] = pd.to_numeric(normalized["price"], errors="coerce").fillna(0.0)
        return normalized.reset_index(drop=True)

    def _normalize_embeddings(self, embeddings: np.ndarray | None) -> np.ndarray | None:
        if embeddings is None or len(embeddings) != len(self.catalog):
            return None
        values = np.asarray(embeddings, dtype=float)
        norms = np.linalg.norm(values, axis=1, keepdims=True)
        return values / np.maximum(norms, 1e-12)

    @staticmethod
    def _description(row: pd.Series) -> str:
        return " ".join(str(row.get(field, "")) for field in ("title", "category", "brand", "pattern", "tags"))

    @staticmethod
    def _colors(title: str) -> set[str]:
        words = {word.strip("-/,.").lower() for word in title.split()}
        return words & COLORS

    def _compatibility(self, anchor_index: int, candidate_index: int) -> tuple[float, dict[str, float], list[str]]:
        anchor = self.catalog.iloc[anchor_index]
        candidate = self.catalog.iloc[candidate_index]

        metadata = float((self.metadata_vectors[anchor_index] @ self.metadata_vectors[candidate_index].T).toarray()[0, 0])
        semantic = metadata
        if self.embeddings is not None:
            clip_similarity = float(np.dot(self.embeddings[anchor_index], self.embeddings[candidate_index]))
            semantic = 0.65 * ((clip_similarity + 1.0) / 2.0) + 0.35 * metadata

        high_price = max(float(anchor["price"]), float(candidate["price"]), 1.0)
        price_cohesion = min(float(anchor["price"]), float(candidate["price"])) / high_price

        anchor_colors = self._colors(anchor["title"])
        candidate_colors = self._colors(candidate["title"])
        if not anchor_colors or not candidate_colors:
            color_harmony = 0.65
        elif anchor_colors & candidate_colors:
            color_harmony = 1.0
        elif anchor_colors & NEUTRALS or candidate_colors & NEUTRALS:
            color_harmony = 0.9
        else:
            color_harmony = 0.55

        brand_variety = 0.35 if anchor["brand"].lower() == candidate["brand"].lower() else 1.0
        signals = {
            "category_compatibility": 1.0,
            "semantic_cohesion": semantic,
            "price_cohesion": price_cohesion,
            "color_harmony": color_harmony,
            "brand_variety": brand_variety,
        }
        score = (
            0.30
            + 0.25 * semantic
            + 0.20 * price_cohesion
            + 0.15 * color_harmony
            + 0.10 * brand_variety
        )

        reasons = ["Completes a complementary outfit category"]
        if semantic >= 0.55:
            reasons.append("Strong visual and style cohesion")
        if price_cohesion >= 0.70:
            reasons.append("Fits the anchor item's price tier")
        if color_harmony >= 0.90:
            reasons.append("Color palette coordinates with the anchor")
        if brand_variety == 1.0:
            reasons.append("Adds brand variety")
        return score, signals, reasons[:3]

    @staticmethod
    def _product(row: pd.Series) -> dict:
        return {
            "id": str(row["id"]),
            "title": str(row["title"]),
            "brand": str(row["brand"]),
            "category": str(row["category"]),
            "price": float(row["price"]),
            "image_url": str(row["image_url"]),
        }

    def compose(self, anchor_id: str, max_total: float | None = None) -> dict:
        """Compose a three-piece complement around one catalog item."""
        start = perf_counter()
        matches = self.catalog.index[self.catalog["id"] == str(anchor_id)].tolist()
        if not matches:
            raise KeyError(f"Product {anchor_id} was not found")

        anchor_index = matches[0]
        anchor = self.catalog.iloc[anchor_index]
        chosen: list[dict] = []
        used_ids = {str(anchor["id"])}
        running_total = float(anchor["price"])

        for slot in required_slots(str(anchor["category"])):
            candidates: list[tuple[float, int, dict[str, float], list[str]]] = []
            for candidate_index, candidate in self.catalog.iterrows():
                candidate_id = str(candidate["id"])
                if candidate_id in used_ids or candidate["category"] not in slot.categories:
                    continue
                if max_total is not None and running_total + float(candidate["price"]) > max_total:
                    continue
                score, signals, reasons = self._compatibility(anchor_index, candidate_index)
                if any(item["product"]["brand"].lower() == str(candidate["brand"]).lower() for item in chosen):
                    score -= 0.04
                candidates.append((score, candidate_index, signals, reasons))

            if not candidates:
                continue
            score, candidate_index, signals, reasons = max(candidates, key=lambda value: value[0])
            candidate = self.catalog.iloc[candidate_index]
            used_ids.add(str(candidate["id"]))
            running_total += float(candidate["price"])
            chosen.append(
                {
                    "slot": slot.name,
                    "product": self._product(candidate),
                    "compatibility_score": round(float(max(0.0, min(score, 1.0))), 4),
                    "signals": {key: round(float(value), 4) for key, value in signals.items()},
                    "reasons": reasons,
                }
            )

        outfit_score = float(np.mean([item["compatibility_score"] for item in chosen])) if chosen else 0.0
        return {
            "anchor": self._product(anchor),
            "items": chosen,
            "outfit_score": round(outfit_score, 4),
            "total_price": round(running_total, 2),
            "complete": len(chosen) == len(required_slots(str(anchor["category"]))),
            "latency_ms": round((perf_counter() - start) * 1000, 3),
        }


def evaluate_outfit_composer(composer: OutfitComposer, anchor_ids: Iterable[str]) -> dict:
    """Evaluate structural validity over a set of catalog anchors."""
    outfits = [composer.compose(anchor_id) for anchor_id in anchor_ids]
    items = [item for outfit in outfits for item in outfit["items"]]
    valid_slots = 0
    for outfit in outfits:
        slot_map = {slot.name: slot.categories for slot in required_slots(outfit["anchor"]["category"])}
        valid_slots += sum(item["product"]["category"] in slot_map[item["slot"]] for item in outfit["items"])
    selected_ids = {item["product"]["id"] for item in items}
    return {
        "anchors": len(outfits),
        "complete_outfit_rate": sum(outfit["complete"] for outfit in outfits) / max(len(outfits), 1),
        "slot_validity_rate": valid_slots / max(len(items), 1),
        "catalog_coverage": len(selected_ids) / max(len(composer.catalog), 1),
        "mean_outfit_score": float(np.mean([outfit["outfit_score"] for outfit in outfits])),
        "p50_latency_ms": float(np.median([outfit["latency_ms"] for outfit in outfits])),
    }

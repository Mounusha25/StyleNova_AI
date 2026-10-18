from __future__ import annotations

import csv
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    category: str
    price: float
    brand: str
    pattern: str
    tags: str

    @property
    def text(self) -> str:
        return " ".join(
            [self.name, self.category, self.brand, self.pattern, self.tags]
        ).lower()


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    query: str
    preferred_categories: tuple[str, ...]
    preferred_brands: tuple[str, ...]
    preferred_patterns: tuple[str, ...]
    max_price: float | None
    relevant_product_ids: frozenset[str]


def load_catalog(path: Path) -> list[Product]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return [
            Product(
                product_id=row["product_id"],
                name=row["name"],
                category=row["category"].strip().lower(),
                price=float(row["price"]),
                brand=row["brand"].strip().lower(),
                pattern=row["pattern"].strip().lower(),
                tags=row["tags"].strip().lower(),
            )
            for row in rows
        ]


def load_benchmark(path: Path) -> list[BenchmarkCase]:
    raw: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    return [
        BenchmarkCase(
            case_id=item["id"],
            query=item["query"],
            preferred_categories=tuple(v.lower() for v in item["preferred_categories"]),
            preferred_brands=tuple(v.lower() for v in item["preferred_brands"]),
            preferred_patterns=tuple(v.lower() for v in item["preferred_patterns"]),
            max_price=item["max_price"],
            relevant_product_ids=frozenset(item["relevant_product_ids"]),
        )
        for item in raw
    ]


class CatalogOrderRanker:
    """Deterministic non-personalized baseline using source catalog order."""

    name = "catalog-order-baseline"

    def __init__(self, products: Sequence[Product]) -> None:
        self.products = list(products)

    def rank(self, _: BenchmarkCase, k: int) -> list[Product]:
        return self.products[:k]


class TfidfRanker:
    name = "tfidf-v1"

    def __init__(self, products: Sequence[Product]) -> None:
        self.products = list(products)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self.matrix = self.vectorizer.fit_transform(p.text for p in self.products)

    def rank(self, case: BenchmarkCase, k: int) -> list[Product]:
        query = self.vectorizer.transform([case.query])
        scores = (self.matrix @ query.T).toarray().ravel()
        order = np.argsort(-scores, kind="stable")[:k]
        return [self.products[index] for index in order]


class HybridRanker(TfidfRanker):
    """TF-IDF retrieval reranked with explicit quiz/profile constraints."""

    name = "hybrid-profile-v1"

    def rank(self, case: BenchmarkCase, k: int) -> list[Product]:
        query = self.vectorizer.transform([case.query])
        text_scores = (self.matrix @ query.T).toarray().ravel()
        scores: list[float] = []

        for product, text_score in zip(self.products, text_scores, strict=True):
            score = float(text_score)
            if case.preferred_categories and product.category in case.preferred_categories:
                score += 0.45
            if case.preferred_brands and product.brand in case.preferred_brands:
                score += 0.55
            if case.preferred_patterns and product.pattern in case.preferred_patterns:
                score += 0.50
            if case.max_price is not None:
                score += 0.15 if product.price <= case.max_price else -0.20
            scores.append(score)

        order = np.argsort(-np.asarray(scores), kind="stable")[:k]
        return [self.products[index] for index in order]


def precision_at_k(ranked_ids: Sequence[str], relevant: set[str] | frozenset[str], k: int) -> float:
    selected = ranked_ids[:k]
    return sum(product_id in relevant for product_id in selected) / k


def recall_at_k(ranked_ids: Sequence[str], relevant: set[str] | frozenset[str], k: int) -> float:
    if not relevant:
        return 0.0
    return sum(product_id in relevant for product_id in ranked_ids[:k]) / len(relevant)


def ndcg_at_k(ranked_ids: Sequence[str], relevant: set[str] | frozenset[str], k: int) -> float:
    gains = [1.0 if product_id in relevant else 0.0 for product_id in ranked_ids[:k]]
    dcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(gains))
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(index + 2) for index in range(ideal_hits))
    return dcg / idcg if idcg else 0.0


def _jaccard_distance(left: Product, right: Product) -> float:
    left_tokens = set(left.text.split())
    right_tokens = set(right.text.split())
    union = left_tokens | right_tokens
    return 1.0 - (len(left_tokens & right_tokens) / len(union)) if union else 0.0


def intra_list_diversity(products: Sequence[Product]) -> float:
    if len(products) < 2:
        return 0.0
    distances = [
        _jaccard_distance(products[left], products[right])
        for left in range(len(products))
        for right in range(left + 1, len(products))
    ]
    return float(np.mean(distances))


def evaluate_ranker(
    ranker: CatalogOrderRanker | TfidfRanker | HybridRanker,
    cases: Iterable[BenchmarkCase],
    catalog_size: int,
    k: int = 10,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    surfaced: set[str] = set()

    for case in cases:
        started = time.perf_counter()
        ranked = ranker.rank(case, k)
        latency_ms = (time.perf_counter() - started) * 1000
        ranked_ids = [product.product_id for product in ranked]
        surfaced.update(ranked_ids)
        rows.append(
            {
                "case_id": case.case_id,
                "precision_at_10": precision_at_k(ranked_ids, case.relevant_product_ids, k),
                "recall_at_10": recall_at_k(ranked_ids, case.relevant_product_ids, k),
                "ndcg_at_10": ndcg_at_k(ranked_ids, case.relevant_product_ids, k),
                "diversity": intra_list_diversity(ranked),
                "latency_ms": latency_ms,
                "ranked_product_ids": ranked_ids,
            }
        )

    def mean(field: str) -> float:
        return float(np.mean([row[field] for row in rows]))

    return {
        "ranker": ranker.name,
        "cases": len(rows),
        "k": k,
        "precision_at_10": mean("precision_at_10"),
        "recall_at_10": mean("recall_at_10"),
        "ndcg_at_10": mean("ndcg_at_10"),
        "intra_list_diversity": mean("diversity"),
        "catalog_coverage": len(surfaced) / catalog_size,
        "p50_latency_ms": float(np.median([row["latency_ms"] for row in rows])),
        "details": rows,
    }


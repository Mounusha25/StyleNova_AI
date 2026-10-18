from __future__ import annotations

import argparse
import json
from pathlib import Path

from evals.core import (
    CatalogOrderRanker,
    HybridRanker,
    TfidfRanker,
    evaluate_ranker,
    load_benchmark,
    load_catalog,
)


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate StyleNova recommendation rankers.")
    parser.add_argument("--catalog", type=Path, default=ROOT / "fashion-reco/catalog_clean.csv")
    parser.add_argument("--benchmark", type=Path, default=ROOT / "evals/benchmark.json")
    parser.add_argument("--output", type=Path, default=ROOT / "evals/results/latest.json")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--fail-under-ndcg", type=float, default=0.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    products = load_catalog(args.catalog)
    cases = load_benchmark(args.benchmark)
    rankers = [CatalogOrderRanker(products), TfidfRanker(products), HybridRanker(products)]
    reports = [evaluate_ranker(ranker, cases, len(products), args.k) for ranker in rankers]

    summary = {
        "benchmark_type": "curated offline relevance benchmark",
        "catalog_items": len(products),
        "cases": len(cases),
        "results": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    for report in reports:
        print(
            f"{report['ranker']:<24} "
            f"P@10={report['precision_at_10']:.3f} "
            f"R@10={report['recall_at_10']:.3f} "
            f"NDCG@10={report['ndcg_at_10']:.3f} "
            f"diversity={report['intra_list_diversity']:.3f} "
            f"coverage={report['catalog_coverage']:.3f} "
            f"p50={report['p50_latency_ms']:.2f}ms"
        )

    candidate = next(report for report in reports if report["ranker"] == "hybrid-profile-v1")
    if candidate["ndcg_at_10"] < args.fail_under_ndcg:
        print(
            f"Quality gate failed: NDCG@10 {candidate['ndcg_at_10']:.3f} "
            f"< {args.fail_under_ndcg:.3f}"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


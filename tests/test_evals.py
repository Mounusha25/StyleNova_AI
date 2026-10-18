from pathlib import Path
import unittest

from evals.core import (
    HybridRanker,
    evaluate_ranker,
    load_benchmark,
    load_catalog,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


ROOT = Path(__file__).resolve().parents[1]


class MetricTests(unittest.TestCase):
    def test_binary_ranking_metrics(self) -> None:
        ranked = ["a", "x", "b", "y"]
        relevant = {"a", "b"}
        self.assertEqual(precision_at_k(ranked, relevant, 4), 0.5)
        self.assertEqual(recall_at_k(ranked, relevant, 4), 1.0)
        self.assertGreater(ndcg_at_k(ranked, relevant, 4), 0.8)

    def test_hybrid_ranker_quality_gate(self) -> None:
        products = load_catalog(ROOT / "fashion-reco/catalog_clean.csv")
        cases = load_benchmark(ROOT / "evals/benchmark.json")
        report = evaluate_ranker(HybridRanker(products), cases, len(products), k=10)
        self.assertGreaterEqual(report["ndcg_at_10"], 0.80)
        self.assertGreaterEqual(report["recall_at_10"], 0.80)


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import sys
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "fashion-reco"))

from outfit_composer import OutfitComposer, evaluate_outfit_composer, required_slots  # noqa: E402


class OutfitComposerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = pd.read_csv(ROOT / "fashion-reco/catalog_clean.csv")
        cls.composer = OutfitComposer(cls.catalog)

    def test_top_anchor_gets_complementary_categories(self) -> None:
        anchor = self.catalog[self.catalog["category"] == "top"].iloc[0]
        outfit = self.composer.compose(str(anchor["product_id"]))
        expected = {slot.name: slot.categories for slot in required_slots("top")}
        self.assertTrue(outfit["complete"])
        self.assertEqual(len(outfit["items"]), 3)
        self.assertEqual(len({item["product"]["id"] for item in outfit["items"]}), 3)
        for item in outfit["items"]:
            self.assertIn(item["product"]["category"], expected[item["slot"]])

    def test_budget_cap_is_respected(self) -> None:
        anchor = self.catalog[self.catalog["category"] == "mini dress"].iloc[0]
        cap = float(anchor["price"]) + 100
        outfit = self.composer.compose(str(anchor["product_id"]), max_total=cap)
        self.assertLessEqual(outfit["total_price"], cap)

    def test_full_catalog_structural_quality_gate(self) -> None:
        report = evaluate_outfit_composer(
            self.composer, self.catalog["product_id"].astype(str)
        )
        self.assertGreaterEqual(report["complete_outfit_rate"], 0.95)
        self.assertEqual(report["slot_validity_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()

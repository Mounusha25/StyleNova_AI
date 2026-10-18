from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from catalog_quality.pipeline import infer_category, process_catalog


ROOT = Path(__file__).resolve().parents[1]


class CatalogQualityTests(unittest.TestCase):
    def test_title_backed_category_normalization(self) -> None:
        self.assertEqual(infer_category("Mini Suede Crossbody Tote", "mini dress"), "bag")
        self.assertEqual(infer_category("Low Waist Jeans", "coat"), "pants")
        self.assertEqual(infer_category("Flowy Knitted Midi Skirt", "midi dress"), "skirt")
        self.assertEqual(infer_category("Fortworth Texas Baby Tee", "maxi dress"), "top")

    def test_repository_catalog_passes_required_field_gate(self) -> None:
        with TemporaryDirectory() as directory:
            report = process_catalog(
                ROOT / "fashion-reco/catalog.csv",
                Path(directory) / "catalog_clean.csv",
                Path(directory) / "report.json",
            )
        self.assertTrue(report["quality_gate_passed"])
        self.assertEqual(report["rows_input"], 100)
        self.assertEqual(report["rows_output"], 100)
        self.assertGreater(report["issue_counts"]["category_normalized"], 0)


if __name__ == "__main__":
    unittest.main()

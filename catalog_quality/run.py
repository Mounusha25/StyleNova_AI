from __future__ import annotations

import argparse
from pathlib import Path

from catalog_quality.pipeline import process_catalog


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and normalize the StyleNova catalog.")
    parser.add_argument("--source", type=Path, default=ROOT / "fashion-reco/catalog.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "fashion-reco/catalog_clean.csv")
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "catalog_quality/reports/catalog_quality.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = process_catalog(args.source, args.output, args.report)
    counts = report["issue_counts"]
    print(f"Rows: {report['rows_input']} -> {report['rows_output']}")
    print(f"Category corrections: {counts.get('category_normalized', 0)}")
    print(f"Possible duplicate rows: {counts.get('possible_duplicate', 0)}")
    print(f"Missing size values: {sum(1 for issue in report['issues'] if issue['field'] == 'available_sizes')}")
    print(f"Missing tag values: {sum(1 for issue in report['issues'] if issue['field'] == 'tags')}")
    print(f"Quality gate: {'PASS' if report['quality_gate_passed'] else 'FAIL'}")
    return 0 if report["quality_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "fashion-reco"))

from outfit_composer import OutfitComposer, evaluate_outfit_composer  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate StyleNova outfit composition.")
    parser.add_argument("--catalog", type=Path, default=ROOT / "fashion-reco/catalog_clean.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "evals/results/outfits.json")
    parser.add_argument("--fail-under-complete", type=float, default=0.0)
    parser.add_argument("--fail-under-validity", type=float, default=0.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog = pd.read_csv(args.catalog)
    composer = OutfitComposer(catalog)
    report = {
        "benchmark_type": "offline structural outfit-composition audit",
        **evaluate_outfit_composer(composer, catalog["product_id"].astype(str)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["complete_outfit_rate"] < args.fail_under_complete:
        return 1
    if report["slot_validity_rate"] < args.fail_under_validity:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

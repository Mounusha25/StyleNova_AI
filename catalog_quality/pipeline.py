from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


REQUIRED_FIELDS = ("product_id", "name", "price", "brand", "image_url")
OUTPUT_FIELDS = (
    "product_id",
    "name",
    "category",
    "source_category",
    "price",
    "brand",
    "pattern",
    "available_sizes",
    "tags",
    "image_url",
)


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    product_id: str
    field: str
    message: str


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def normalize_list(value: str) -> str:
    values = [normalize_text(item) for item in value.split(",") if normalize_text(item)]
    return ", ".join(dict.fromkeys(values))


def infer_category(name: str, fallback: str) -> str:
    """Map noisy source labels into a small title-backed fashion taxonomy."""
    title = name.lower()
    rules: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("bag", ("bag", "tote", "crossbody", "handbag")),
        ("footwear", ("boot", "shoe", "sneaker", "sandal")),
        ("accessory", ("headband", "hat", "scarf", "belt")),
        ("bikini set", ("bikini",)),
        ("swimsuit", ("swimsuit", "one-piece")),
        ("sports bra", ("sports bra", "essential bra", "line up bra")),
        ("bodysuit", ("bodysuit",)),
        ("romper", ("romper",)),
        ("maxi dress", ("maxi dress",)),
        ("midi dress", ("midi dress",)),
        ("mini dress", ("mini dress", "sleep dress")),
        ("dress", ("dress", "gown")),
        ("skirt", ("skirt", "skort")),
        ("coat", ("coat", "trench")),
        ("jacket", ("jacket",)),
        ("blazer", ("blazer",)),
        ("sweater", ("sweater", "cardigan")),
        ("pants", ("pant", "trouser", "sweatpant", "legging", "jean")),
        ("shorts", ("short",)),
        ("blouse", ("blouse",)),
        ("top", ("shirt", "tee", "top", "vest", "tank")),
        ("set", (" set",)),
    )
    for category, keywords in rules:
        if any(keyword in title for keyword in keywords):
            return category
    normalized_fallback = normalize_text(fallback).lower()
    return normalized_fallback if normalized_fallback else "other"


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _duplicate_groups(rows: Iterable[dict[str, str]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for row in rows:
        key = (row["name"].casefold(), row["brand"].casefold(), row["price"])
        groups[key].append(row["product_id"])
    return [
        {"name": key[0], "brand": key[1], "price": key[2], "product_ids": ids}
        for key, ids in sorted(groups.items())
        if len(ids) > 1
    ]


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def process_catalog(source: Path, output: Path, report_path: Path) -> dict[str, object]:
    with source.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle))

    issues: list[Issue] = []
    clean_rows: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for raw in source_rows:
        product_id = normalize_text(raw.get("product_id", ""))
        for field in REQUIRED_FIELDS:
            if not normalize_text(raw.get(field, "")):
                issues.append(Issue("error", "missing_required", product_id, field, "Required value is empty"))

        if product_id in seen_ids:
            issues.append(Issue("error", "duplicate_id", product_id, "product_id", "Product ID is not unique"))
        seen_ids.add(product_id)

        price_raw = normalize_text(raw.get("price", ""))
        try:
            price = float(price_raw)
            if price <= 0:
                raise ValueError
            normalized_price = f"{price:.2f}"
        except ValueError:
            normalized_price = price_raw
            issues.append(Issue("error", "invalid_price", product_id, "price", f"Invalid positive price: {price_raw!r}"))

        image_url = normalize_text(raw.get("image_url", ""))
        if image_url and not _valid_url(image_url):
            issues.append(Issue("error", "invalid_url", product_id, "image_url", "Expected an absolute HTTP(S) URL"))

        name = normalize_text(raw.get("name", ""))
        source_category = normalize_text(raw.get("category", "")).lower()
        category = infer_category(name, source_category)
        if source_category and category != source_category:
            issues.append(
                Issue(
                    "warning",
                    "category_normalized",
                    product_id,
                    "category",
                    f"{source_category!r} -> {category!r} based on product title",
                )
            )

        sizes = normalize_list(raw.get("available_sizes", ""))
        tags = normalize_list(raw.get("tags", ""))
        if not sizes:
            issues.append(Issue("info", "missing_optional", product_id, "available_sizes", "No size metadata"))
        if not tags:
            issues.append(Issue("info", "missing_optional", product_id, "tags", "No tag metadata"))

        clean_rows.append(
            {
                "product_id": product_id,
                "name": name,
                "category": category,
                "source_category": source_category,
                "price": normalized_price,
                "brand": normalize_text(raw.get("brand", "")),
                "pattern": normalize_text(raw.get("pattern", "")).lower() or "other",
                "available_sizes": sizes,
                "tags": tags,
                "image_url": image_url,
            }
        )

    duplicate_groups = _duplicate_groups(clean_rows)
    for group in duplicate_groups:
        for product_id in group["product_ids"]:
            issues.append(
                Issue(
                    "warning",
                    "possible_duplicate",
                    str(product_id),
                    "name",
                    "Same normalized name, brand, and price as another catalog row",
                )
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(clean_rows)

    severity_counts = Counter(issue.severity for issue in issues)
    code_counts = Counter(issue.code for issue in issues)
    report: dict[str, object] = {
        "source": _display_path(source),
        "output": _display_path(output),
        "rows_input": len(source_rows),
        "rows_output": len(clean_rows),
        "quality_gate_passed": severity_counts["error"] == 0,
        "severity_counts": dict(sorted(severity_counts.items())),
        "issue_counts": dict(sorted(code_counts.items())),
        "source_categories": dict(sorted(Counter(row.get("category", "") for row in source_rows).items())),
        "normalized_categories": dict(sorted(Counter(row["category"] for row in clean_rows).items())),
        "possible_duplicate_groups": duplicate_groups,
        "issues": [asdict(issue) for issue in issues],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


#!/usr/bin/env python3
"""
Pre-filter catalog to remove items with inaccessible images (403 Forbidden)
This helps avoid warnings during API startup.
"""

import pandas as pd
import requests
import logging
from typing import List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_image_accessibility(url: str, timeout: int = 5) -> bool:
    """Check if an image URL is accessible."""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def filter_accessible_items(input_csv: str, output_csv: str) -> None:
    """Filter catalog to keep only items with accessible images."""

    logger.info(f"📁 Loading catalog from {input_csv}")
    df = pd.read_csv(input_csv)

    logger.info(f"📊 Original catalog size: {len(df)} items")

    accessible_items = []
    inaccessible_count = 0

    for idx, row in df.iterrows():
        image_url = row.get("image_url", "")

        if pd.isna(image_url) or image_url == "":
            # Keep items without images (will use text-only)
            accessible_items.append(row)
            logger.info(f"  ✅ {row.get('name', 'unknown')} - no image URL")
        else:
            # Check if image is accessible
            if check_image_accessibility(image_url):
                accessible_items.append(row)
                logger.info(f"  ✅ {row.get('name', 'unknown')} - image accessible")
            else:
                inaccessible_count += 1
                logger.warning(
                    f"  🚫 {row.get('name', 'unknown')} - image inaccessible: {image_url}"
                )

    # Create filtered dataframe
    filtered_df = pd.DataFrame(accessible_items)

    # Save filtered catalog
    filtered_df.to_csv(output_csv, index=False)

    logger.info(f"📊 Filtered catalog saved to {output_csv}")
    logger.info(f"📊 Final size: {len(filtered_df)} items")
    logger.info(f"📊 Removed: {inaccessible_count} inaccessible items")
    logger.info(f"📊 Retention rate: {len(filtered_df) / len(df) * 100:.1f}%")


def main():
    """Main function to filter catalog."""

    print("🔍 CATALOG IMAGE ACCESSIBILITY FILTER")
    print("=" * 45)
    print("This tool removes items with inaccessible images (403 Forbidden)")
    print("to prevent warnings during API startup.")
    print()

    # Filter the catalog
    filter_accessible_items("catalog.csv", "catalog_filtered.csv")

    print()
    print("✅ Filtering complete!")
    print("💡 Update your API to use 'catalog_filtered.csv' instead of 'catalog.csv'")


if __name__ == "__main__":
    main()

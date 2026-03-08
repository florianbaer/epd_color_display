"""
Backfill sidecar JSON metadata for existing images by matching
them to prompt_history.csv entries via timestamp proximity.

Usage:
    python -m backend.scripts.backfill_metadata
"""

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def parse_csv_timestamp(ts: str) -> datetime:
    return datetime.strptime(ts.strip(), "%Y-%m-%d %H:%M:%S")


def parse_image_timestamp(filename: str) -> datetime | None:
    """Extract timestamp from filename like landscape_20260125_141405.png"""
    stem = Path(filename).stem
    parts = stem.split("_")
    if len(parts) >= 3:
        try:
            return datetime.strptime(f"{parts[-2]}_{parts[-1]}", "%Y%m%d_%H%M%S")
        except ValueError:
            pass
    return None


def load_prompt_history(csv_path: str) -> list[tuple[datetime, str]]:
    entries = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return entries
        for row in reader:
            if len(row) >= 2:
                try:
                    ts = parse_csv_timestamp(row[0])
                    entries.append((ts, row[1]))
                except ValueError:
                    continue
    entries.sort(key=lambda x: x[0])
    return entries


def find_best_prompt(image_ts: datetime, entries: list[tuple[datetime, str]]) -> str | None:
    """Find the nearest CSV entry with timestamp <= image timestamp."""
    best = None
    for ts, prompt in entries:
        if ts <= image_ts:
            best = prompt
        else:
            break
    return best


def main():
    # Resolve paths relative to project root
    project_root = Path(__file__).resolve().parent.parent.parent
    csv_path = project_root / "prompt_history.csv"
    image_dir = project_root / "generated_images"

    if not csv_path.exists():
        print(f"No prompt_history.csv found at {csv_path}")
        sys.exit(1)

    if not image_dir.exists():
        print(f"No generated_images directory at {image_dir}")
        sys.exit(1)

    entries = load_prompt_history(str(csv_path))
    print(f"Loaded {len(entries)} prompt history entries")

    png_files = sorted(image_dir.glob("*.png"))
    created = 0
    skipped = 0

    for img_path in png_files:
        json_path = img_path.with_suffix(".json")
        if json_path.exists():
            skipped += 1
            continue

        image_ts = parse_image_timestamp(img_path.name)
        if image_ts is None:
            # Fall back to file mtime
            image_ts = datetime.fromtimestamp(img_path.stat().st_mtime)

        prompt = find_best_prompt(image_ts, entries)
        if prompt is None:
            prompt = ""

        metadata = {
            "prompt": prompt,
            "generated_at": image_ts.isoformat(),
            "model": "",
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        created += 1
        print(f"  Created: {json_path.name} -> {prompt[:60]}...")

    print(f"\nDone: {created} created, {skipped} skipped (already exist)")


if __name__ == "__main__":
    main()

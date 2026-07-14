"""Report persistence helpers."""

from __future__ import annotations

import csv
from pathlib import Path


def export_runs_csv(runs: list[dict], path: str | Path) -> None:
    """Export optimization runs to CSV using the Python standard library."""

    output_path = Path(path)
    fieldnames = sorted({key for run in runs for key in run})
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(runs)

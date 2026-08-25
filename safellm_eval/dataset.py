from __future__ import annotations

import csv
from pathlib import Path

from .schemas import TestCase


REQUIRED_COLUMNS = {
    "id",
    "risk_type",
    "prompt",
    "expected_behavior",
    "severity",
    "source",
}


def load_test_cases(path: str | Path) -> list[TestCase]:
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Dataset missing required columns: {sorted(missing)}")

        cases: list[TestCase] = []
        for row in reader:
            case = TestCase(
                id=row["id"].strip(),
                risk_type=row["risk_type"].strip(),
                prompt=row["prompt"].strip(),
                expected_behavior=row["expected_behavior"].strip(),
                severity=row["severity"].strip(),
                source=row["source"].strip(),
            )
            if not case.id or not case.prompt:
                raise ValueError("Each row must include non-empty id and prompt")
            cases.append(case)

    return cases

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestCase:
    id: str
    risk_type: str
    prompt: str
    expected_behavior: str
    severity: str
    source: str


@dataclass(frozen=True)
class ModelResponse:
    model_name: str
    content: str
    latency_ms: int


@dataclass(frozen=True)
class EvaluationResult:
    test_case: TestCase
    model_response: ModelResponse
    verdict: str
    score: float
    reason: str
    needs_review: bool

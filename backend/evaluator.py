"""Accuracy Evaluation & Benchmarking Module for OmniRisk.

Evaluates KRI detection accuracy, verdict alignment, and latency
against established actuarial ground truth test cases.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from backend.schemas import InputRiskPayload
from backend.agent import RiskSummarizerAgent


class AccuracyEvaluator:
    """Evaluates agent performance against ground truth benchmark data."""

    def __init__(self, ground_truth_path: str = "data/ground_truth_eval.json"):
        p = Path(ground_truth_path)
        if not p.exists():
            candidate = Path(__file__).resolve().parent.parent / ground_truth_path
            if candidate.exists():
                p = candidate
        self.ground_truth_path = p
        self.agent = RiskSummarizerAgent()

    def run_benchmark(self) -> Dict[str, Any]:
        """Runs the benchmark suite and returns precision, recall, and overall accuracy."""
        if not self.ground_truth_path.exists():
            raise FileNotFoundError(f"Benchmark file not found: {self.ground_truth_path}")

        with open(self.ground_truth_path, "r", encoding="utf-8") as f:
            cases = json.load(f)

        total_cases = len(cases)
        total_kris_expected = 0
        total_kris_detected = 0
        true_positives_kri = 0
        verdict_matches = 0
        latencies_ms = []
        case_results = []

        for case in cases:
            payload = InputRiskPayload(**case["payload"])
            report = self.agent.synthesize(payload)

            detected_kri_codes = {kri.code for kri in report.key_risk_indicators}
            expected_kri_codes = set(case.get("expected_kri_codes", []))

            # Calculate KRI intersection
            tp = len(detected_kri_codes.intersection(expected_kri_codes))
            true_positives_kri += tp
            total_kris_expected += len(expected_kri_codes)
            total_kris_detected += len(detected_kri_codes)

            # Check verdict alignment
            expected_verdict = case.get("expected_verdict")
            acceptable = case.get("acceptable_verdicts", [expected_verdict])
            verdict_matched = (report.verdict == expected_verdict) or (report.verdict in acceptable)
            if verdict_matched:
                verdict_matches += 1

            # Latency check (< 10 seconds / 10,000 ms per user SLA)
            latencies_ms.append(report.processing_time_ms)
            passes_speed_constraint = report.processing_time_ms < 10000.0

            case_results.append({
                "test_id": case.get("test_id"),
                "description": case.get("description"),
                "expected_verdict": expected_verdict,
                "actual_verdict": report.verdict,
                "verdict_matched": verdict_matched,
                "expected_kri_codes": list(expected_kri_codes),
                "actual_kri_codes": list(detected_kri_codes),
                "latency_ms": report.processing_time_ms,
                "speed_compliant": passes_speed_constraint,
            })

        # Precision, Recall, and Accuracy computation
        precision = (true_positives_kri / total_kris_detected) if total_kris_detected > 0 else 1.0
        recall = (true_positives_kri / total_kris_expected) if total_kris_expected > 0 else 1.0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 1.0

        verdict_accuracy_pct = round((verdict_matches / total_cases) * 100.0, 1)
        kri_accuracy_pct = round(f1_score * 100.0, 1)
        composite_accuracy_pct = round((verdict_accuracy_pct * 0.5) + (kri_accuracy_pct * 0.5), 1)

        avg_latency_ms = round(sum(latencies_ms) / len(latencies_ms), 2) if latencies_ms else 0.0

        return {
            "total_benchmark_cases": total_cases,
            "verdict_accuracy_pct": verdict_accuracy_pct,
            "kri_f1_accuracy_pct": kri_accuracy_pct,
            "composite_accuracy_pct": composite_accuracy_pct,
            "target_threshold_pct": 85.0,
            "accuracy_target_met": composite_accuracy_pct >= 85.0,
            "average_latency_ms": avg_latency_ms,
            "max_latency_allowed_ms": 10000.0,
            "speed_target_met": avg_latency_ms < 10000.0,
            "case_breakdowns": case_results,
        }

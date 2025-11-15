"""
analyze_bias.py
Performs simple quantitative analysis of LLM outputs to detect bias patterns.

Input:
    results.jsonl  (from run_experiment.py or manual collection)

Output:
    Prints summary statistics to the console.

This is dataset-agnostic and only looks for generic language patterns
(e.g. "inefficient", "developing", "defensive liability").
"""

import json
from collections import defaultdict
from typing import Dict, Any


def load_results(path: str = "results.jsonl"):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def label_primary_scorer_response(text: str) -> str:
    """
    Naive classifier for primary-scorer answers.
    Returns one of {"inefficient", "developing", "neutral_or_mixed"}.
    """
    lower = text.lower()
    if "inefficient" in lower or "low-efficiency" in lower or "inefficiency" in lower:
        return "inefficient"
    if "developing" in lower or "primary scorer" in lower or "carrying the offense" in lower:
        return "developing"
    return "neutral_or_mixed"


def label_playerB_response(text: str) -> str:
    """
    Naive labels for Player B: {"defensive_liability", "offensive_spacing", "balanced"}.
    """
    lower = text.lower()
    if "defensive liability" in lower or "weak defender" in lower:
        return "defensive_liability"
    if "spacing" in lower or "floor-spacing" in lower or "offensive weapon" in lower:
        return "offensive_spacing"
    return "balanced"


def label_playerC_response(text: str) -> str:
    """
    Naive labels for Player C: {"anchor", "weakness_focus", "balanced"}.
    """
    lower = text.lower()
    if "anchor" in lower or "anchors the defense" in lower or "anchors the interior" in lower:
        return "anchor"
    if "liability" in lower or "major weakness" in lower:
        return "weakness_focus"
    return "balanced"


def analyze_bias(path: str = "results.jsonl") -> None:
    """
    For each hypothesis, compute simple counts of how many responses
    fall into each label bucket per condition.
    """
    counts: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )

    for row in load_results(path):
        hyp = row.get("hypothesis")
        cond = row.get("condition")
        resp = row.get("response", "")

        if hyp == "H1_framing_primary_scorer":
            label = label_primary_scorer_response(resp)
        elif hyp == "H2_selection_playerB":
            label = label_playerB_response(resp)
        elif hyp == "H4_framing_playerC":
            label = label_playerC_response(resp)
        elif hyp == "H3_confirmation_causeA_vs_causeB":
            # For H3, we look for which explanation is emphasized.
            lower = resp.lower()
            if "turnover" in lower or "turnovers" in lower:
                label = "causeA_focus"
            elif "three-point" in lower or "3-point" in lower or "3pt" in lower or "long-range" in lower:
                label = "causeB_focus"
            else:
                label = "mixed_or_other"
        else:
            label = "unclassified"

        counts[hyp][cond][label] += 1

    # Print summary
    for hyp, cond_dict in counts.items():
        print(f"\n=== Hypothesis: {hyp} ===")
        for cond, label_dict in cond_dict.items():
            print(f"  Condition: {cond}")
            total = sum(label_dict.values())
            for label, c in label_dict.items():
                pct = (c / total * 100) if total else 0.0
                print(f"    {label}: {c} ({pct:.1f}%)")


if __name__ == "__main__":
    analyze_bias()

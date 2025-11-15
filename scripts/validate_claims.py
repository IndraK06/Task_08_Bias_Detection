"""
validate_claims.py
Checks LLM statements against simple ground truth data.

This version is generic:
- You provide a small ground-truth dictionary with key stats for
  Player A (primary scorer), Player B (wing/role player), Player C (interior),
  and team-level stats.
- We then look for obvious mismatches between the language used and the stats.

Input:
    results.jsonl  (from run_experiment.py or manual collection)

Output:
    Prints a simple validation report to console.

IMPORTANT:
- Replace the example values in GROUND_TRUTH with real values
  from your dataset.
"""

import json
from typing import Dict, Any


# --- Ground truth example (replace with your dataset’s actual numbers) ---

GROUND_TRUTH: Dict[str, Any] = {
    "primary_scorer": {
        # Example structure; fill in from your data
        "ppg": 0.0,    # points per game
        "fg": 0.0,     # field-goal percentage (0–1)
        "tp": 0.0,     # three-point percentage (0–1) if relevant
        "ft": 0.0,     # free-throw percentage (0–1)
    },
    "playerB": {
        # Example: wing / role player
        "ppg": 0.0,
        "fg": 0.0,
        "tp": 0.0,     # outside shooting
        "rpg": 0.0,    # rebounds per game
        "stl": 0.0,    # steals (total or per game)
        "blk": 0.0,    # blocks (total or per game)
    },
    "playerC": {
        # Example: interior player / big
        "ppg": 0.0,
        "rpg": 0.0,
        "blk": 0.0,    # blocks per game
        "ft": 0.0,     # free-throw percentage
    },
    "team": {
        # Example: team-level stats
        "ppg": 0.0,
        "opp_ppg": 0.0,
        "tov": 0.0,
        "opp_tov": 0.0,
        "tp": 0.0,
        "opp_tp": 0.0,
        "rebound_margin_positive": True,  # set based on your data
    },
}


def load_results(path: str = "results.jsonl"):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def validate_primary_scorer(text: str) -> Dict[str, Any]:
    """
    Rough consistency check: does the response describe the primary scorer
    in a way that clearly contradicts the basic efficiency stats?
    """
    lower = text.lower()
    gt = GROUND_TRUTH["primary_scorer"]

    issues = []

    # If the model calls them "very efficient" but fg/tp are low
    if "very efficient" in lower or "highly efficient" in lower:
        if gt["fg"] and gt["fg"] < 0.44:
            issues.append("Describes primary scorer as very efficient despite relatively low FG%.")
        if gt["tp"] and gt["tp"] < 0.32:
            issues.append("Describes primary scorer as very efficient despite relatively low 3P%.")

    # If the model calls them low-usage when ppg is high
    if "low-usage" in lower or "limited usage" in lower:
        if gt["ppg"] and gt["ppg"] > 10:  # threshold is arbitrary; adjust to domain
            issues.append("Describes primary scorer as low-usage despite high scoring volume.")

    return {"issues": issues}


def validate_playerB(text: str) -> Dict[str, Any]:
    """
    Check claims about Player B (e.g., spacing vs defense).
    """
    lower = text.lower()
    gt = GROUND_TRUTH["playerB"]

    issues = []

    # If the model calls them a poor shooter but 3P% is actually solid
    if "poor shooter" in lower or "weak shooter" in lower:
        if gt["tp"] and gt["tp"] >= 0.35:
            issues.append("Calls Player B a poor shooter despite solid outside shooting percentage.")

    # If the model strongly praises defense despite low defensive stats
    if "elite defender" in lower or "high defensive playmaking" in lower:
        if gt["stl"] < 1 and gt["blk"] < 1:  # per game thresholds; adjust if you use totals
            issues.append("Overstates Player B’s defensive playmaking given low steals/blocks.")

    return {"issues": issues}


def validate_playerC(text: str) -> Dict[str, Any]:
    """
    Check claims about Player C (e.g., anchor vs free-throw liability).
    """
    lower = text.lower()
    gt = GROUND_TRUTH["playerC"]

    issues = []

    # Free-throw accuracy
    if "excellent free-throw shooter" in lower or "very strong at the free-throw line" in lower:
        if gt["ft"] and gt["ft"] < 0.75:
            issues.append("Calls Player C excellent at free throws despite relatively low FT%.")

    # Shot blocking / rim protection
    if "elite rim protector" in lower or "dominant shot blocker" in lower:
        if gt["blk"] and gt["blk"] < 1.5:
            issues.append("Calls Player C an elite rim protector despite low blocks per game.")

    return {"issues": issues}


def validate_team(text: str) -> Dict[str, Any]:
    """
    Check team-level exaggerations (e.g., about rebounding, turnovers).
    """
    lower = text.lower()
    gt = GROUND_TRUTH["team"]

    issues = []

    # Rebounding claims
    if "terrible rebounding" in lower or "very poor on the boards" in lower:
        if gt.get("rebound_margin_positive", False):
            issues.append("Claims team is terrible at rebounding despite positive rebounding profile.")

    return {"issues": issues}


def validate_row(row: Dict[str, Any]) -> Dict[str, Any]:
    hyp = row.get("hypothesis")
    resp = row.get("response", "")

    if hyp == "H1_framing_primary_scorer":
        return validate_primary_scorer(resp)
    if hyp == "H2_selection_playerB":
        return validate_playerB(resp)
    if hyp == "H4_framing_playerC":
        return validate_playerC(resp)
    if hyp == "H3_confirmation_causeA_vs_causeB":
        return validate_team(resp)

    return {"issues": []}


def run_validation(results_path: str = "results.jsonl") -> None:
    """
    Iterate through all results, apply simple consistency checks,
    and print a summary of potential misalignments with ground truth.
    """
    total = 0
    with_issues = 0

    for row in load_results(results_path):
        total += 1
        outcome = validate_row(row)
        issues = outcome["issues"]
        if issues:
            with_issues += 1
            print(f"\n[ISSUES] prompt_id={row.get('prompt_id')}  hypothesis={row.get('hypothesis')}")
            for issue in issues:
                print(f"  - {issue}")

    print("\n=== Validation Summary ===")
    print(f"Total responses checked: {total}")
    print(f"Responses with at least one potential issue: {with_issues}")


if __name__ == "__main__":
    run_validation()

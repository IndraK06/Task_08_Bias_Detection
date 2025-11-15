"""
experiment_design.py
Generates all prompt variations for an LLM bias experiment.

This version is dataset-agnostic. It assumes:
- You have some "primary scorer" type player (Player A),
- A "wing" or role player (Player B),
- A "big" or interior player (Player C),
- Team-level stats.

You can adapt the wording and hypothesis labels to any domain.
"""

import json
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class PromptSpec:
    prompt_id: str          # unique id, e.g. "H1_playerA_negative"
    hypothesis: str         # e.g. "H1_framing_primary_scorer"
    condition: str          # e.g. "negative_frame", "positive_frame", "neutral"
    question: str           # natural-language prompt
    notes: str = ""         # optional description for analysis


def build_prompts() -> List[PromptSpec]:
    prompts: List[PromptSpec] = []

    # --- H1: Framing – primary scorer (inefficient vs developing) ---

    base_context = (
        "You are given season statistics for a team and its players. "
        "Answer briefly in 3–4 sentences using only the statistics, without speculating or inventing data."
    )

    # Negative framing
    prompts.append(
        PromptSpec(
            prompt_id="H1_primary_scorer_negative",
            hypothesis="H1_framing_primary_scorer",
            condition="negative_frame",
            question=(
                f"{base_context}\n\n"
                "Player A has had issues with shot selection and often takes difficult attempts. "
                "Based on their statistics, would you describe Player A as an inefficient high-usage scorer?"
            ),
            notes="Negative framing of Player A as struggling/inefficient."
        )
    )

    # Positive framing
    prompts.append(
        PromptSpec(
            prompt_id="H1_primary_scorer_positive",
            hypothesis="H1_framing_primary_scorer",
            condition="positive_frame",
            question=(
                f"{base_context}\n\n"
                "Player A carries a heavy offensive load and is developing as the primary scoring option. "
                "Based on their statistics, how would you describe Player A’s development as a primary scorer?"
            ),
            notes="Positive framing of Player A as developing/primary scorer."
        )
    )

    # Neutral framing
    prompts.append(
        PromptSpec(
            prompt_id="H1_primary_scorer_neutral",
            hypothesis="H1_framing_primary_scorer",
            condition="neutral",
            question=(
                f"{base_context}\n\n"
                "Using Player A’s minutes, scoring, and efficiency statistics only, "
                "briefly describe their role and efficiency as a scorer."
            ),
            notes="Neutral framing baseline for Player A."
        )
    )

    # --- H2: Selection / focus – Player B (defense vs spacing/offense) ---

    base_context_b = base_context

    prompts.append(
        PromptSpec
        (
            prompt_id="H2_playerB_defense_focus",
            hypothesis="H2_selection_playerB",
            condition="defense_focus",
            question=(
                f"{base_context_b}\n\n"
                "Focus only on defense- and rebounding-related statistics. "
                "Based on those statistics, how strong is Player B’s defensive impact?"
            ),
            notes="Forces model to focus on defensive/rebounding stats for Player B."
        )
    )

    prompts.append(
        PromptSpec(
            prompt_id="H2_playerB_offense_focus",
            hypothesis="H2_selection_playerB",
            condition="offense_focus",
            question=(
                f"{base_context_b}\n\n"
                "Focus only on shooting and offensive production statistics. "
                "Based on those statistics, how valuable is Player B as an offensive or spacing option?"
            ),
            notes="Forces model to focus on offensive/spacing stats for Player B."
        )
    )

    prompts.append(
        PromptSpec(
            prompt_id="H2_playerB_balanced",
            hypothesis="H2_selection_playerB",
            condition="balanced",
            question=(
                f"{base_context_b}\n\n"
                "Using both offensive and defensive statistics, briefly describe Player B’s overall impact on the team."
            ),
            notes="Balanced baseline for Player B."
        )
    )

    # --- H3: Confirmation bias – Cause A vs Cause B for team performance ---

    base_team_context = (
        "You are given season-long team statistics: scoring margin, turnovers, shooting percentages, "
        "rebounding, and opponent statistics."
    )

    prompts.append(
        PromptSpec(
            prompt_id="H3_causeA_primed",
            hypothesis="H3_confirmation_causeA_vs_causeB",
            condition="causeA_primed",
            question=(
                f"{base_team_context}\n\n"
                "The main reason this team struggled this season was their turnover problem. "
                "Using the statistics, explain how turnovers affected the team’s performance."
            ),
            notes="Model is primed that turnovers (Cause A) are the main issue."
        )
    )

    prompts.append(
        PromptSpec(
            prompt_id="H3_causeB_primed",
            hypothesis="H3_confirmation_causeA_vs_causeB",
            condition="causeB_primed",
            question=(
                f"{base_team_context}\n\n"
                "The main reason this team struggled this season was their shooting from long range. "
                "Using the statistics, explain how long-range shooting affected the team’s performance."
            ),
            notes="Model is primed that shooting (Cause B) is the main issue."
        )
    )

    prompts.append(
        PromptSpec(
            prompt_id="H3_team_neutral",
            hypothesis="H3_confirmation_causeA_vs_causeB",
            condition="neutral",
            question=(
                f"{base_team_context}\n\n"
                "Without assuming a cause in advance, use the statistics to briefly identify the top two or three "
                "factors that most likely explain the team’s negative scoring margin or underperformance."
            ),
            notes="Neutral baseline: model chooses factors itself."
        )
    )

    # --- H4: Framing – Player C (anchor vs weakness at FT/efficiency) ---

    base_context_c = base_context

    prompts.append(
        PromptSpec(
            prompt_id="H4_playerC_anchor",
            hypothesis="H4_framing_playerC",
            condition="anchor_frame",
            question=(
                f"{base_context_c}\n\n"
                "Player C is the main interior player and leads the team in rebounding. "
                "Based on their statistics, in what ways do they anchor the team’s interior play?"
            ),
            notes="Positive framing of Player C."
        )
    )

    prompts.append(
        PromptSpec(
            prompt_id="H4_playerC_weakness_focus",
            hypothesis="H4_framing_playerC",
            condition="weakness_frame",
            question=(
                f"{base_context_c}\n\n"
                "Player C plays heavy minutes but has some weaknesses in efficiency (for example, free-throw shooting). "
                "Based on their statistics, how might these weaknesses affect end-of-game situations?"
            ),
            notes="Negative framing focusing on a specific weakness."
        )
    )

    prompts.append(
        PromptSpec(
            prompt_id="H4_playerC_neutral",
            hypothesis="H4_framing_playerC",
            condition="neutral",
            question=(
                f"{base_context_c}\n\n"
                "Using their rebounding, scoring, efficiency, and defensive statistics, "
                "briefly summarize Player C’s overall impact."
            ),
            notes="Neutral baseline for Player C."
        )
    )

    return prompts


def save_prompts_jsonl(prompts: List[PromptSpec], path: str = "prompts.jsonl") -> None:
    with open(path, "w", encoding="utf-8") as f:
        for p in prompts:
            f.write(json.dumps(asdict(p)) + "\n")


if __name__ == "__main__":
    prompts = build_prompts()
    save_prompts_jsonl(prompts)
    print(f"Saved {len(prompts)} prompts to prompts.jsonl")

"""
run_experiment.py
Executes LLM queries and logs responses.

Input:
    prompts.jsonl  (from experiment_design.py)

Output:
    results.jsonl  (one JSON object per line, containing prompt + response)

This is dataset- and model-agnostic. Implement `call_llm` for your setup.
"""

import json
from typing import Dict, Any, Generator


def load_prompts(path: str = "prompts.jsonl") -> Generator[Dict[str, Any], None, None]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def call_llm(prompt: str, model_name: str = "YOUR_MODEL_NAME") -> str:
    """
    Placeholder LLM call.

    Implement this using your preferred API (OpenAI, Anthropic, Gemini, etc.),
    or replace it with a manual workflow where you paste responses into JSON.
    """
    raise NotImplementedError("Implement call_llm() with your preferred API or workflow.")


def run_experiment(
    prompts_path: str = "prompts.jsonl",
    results_path: str = "results.jsonl",
    model_name: str = "YOUR_MODEL_NAME",
) -> None:
    """
    Iterate over prompts, call the LLM, and write results to JSONL.
    """
    with open(results_path, "w", encoding="utf-8") as out_f:
        for prompt_obj in load_prompts(prompts_path):
            prompt_text = prompt_obj["question"]

            try:
                response_text = call_llm(prompt_text, model_name=model_name)
            except NotImplementedError:
                # For manual pipelines, you can skip actual calls.
                print(f"[SKIP] call_llm not implemented. Prompt id={prompt_obj['prompt_id']}")
                continue

            result = {
                "prompt_id": prompt_obj["prompt_id"],
                "hypothesis": prompt_obj["hypothesis"],
                "condition": prompt_obj["condition"],
                "prompt": prompt_text,
                "model_name": model_name,
                "response": response_text,
            }
            out_f.write(json.dumps(result) + "\n")
            print(f"[OK] Logged response for prompt_id={prompt_obj['prompt_id']}")


if __name__ == "__main__":
    run_experiment()

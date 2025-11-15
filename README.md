# 🔍 LLM Bias Detection Framework

This repository contains a dataset-agnostic framework for analyzing how Large Language Models (LLMs) respond to controlled prompt variations. The goal is to detect framing bias, confirmation bias, and selection bias using a fully anonymized numerical dataset. All references to real individuals or teams have been removed and replaced with neutral placeholders (e.g., *Player A*, *Metric A*).

---

## 📂 Repository Contents

**/scripts**  
- `experiment_design.py` – Automatically generates all prompt variations  
- `run_experiment.py` – Executes prompts against an LLM and logs responses  
- `analyze_bias.py` – Performs sentiment, focus, and framing analysis  
- `validate_claims.py` – Checks LLM claims against ground-truth statistics  

**Report.pdf** – Complete findings, methodology, visualizations, and mitigation strategies.

---

## ⚙️ Workflow Overview

1. **Prompt Generation**  
   Structured prompts are created to isolate specific bias variables (positive vs negative framing, hypothesis priming, selective focus).

2. **LLM Execution**  
   Prompts are submitted to any LLM (ChatGPT, Claude, Gemini, etc.), and responses are saved in JSONL format.

3. **Bias Analysis**  
   Responses are coded automatically for tone, emphasis, and narrative pattern to identify systematic shifts across conditions.

4. **Ground-Truth Validation**  
   A simple validation script checks whether LLM outputs remain consistent with the actual dataset.

---

## 🎯 Objective

- Demonstrate how minor wording changes can influence LLM interpretations.  
- Provide a replicable framework for cross-model bias studies.  
- Enable transparent evaluation of LLM fidelity vs narrative sensitivity.

---

## 📘 Acknowledgement

This project was developed as part of a research-based study and is intended solely for educational and analytical purposes. All data has been anonymized, and no outputs represent real individuals or real events.


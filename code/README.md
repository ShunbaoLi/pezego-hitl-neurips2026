# Pezego-HITL NeurIPS 2026 Reproducibility Package

This repository contains a lightweight reproducibility package for the paper:

"An Evaluation Architecture for Policy-Grounded LLM Pest Management: Cross-Context Expert Review, Deployment Telemetry, and Human Feedback"

## Repository URL (for NeurIPS submission)

Public code repository:

- Code URL: https://github.com/ShunbaoLi/pezego-hitl-neurips2026

For anonymous review, you can use an anonymized mirror (for example 4open):

- Anonymous URL: https://anonymous.4open.science/r/<repo-id>/

Note: this repository is code-only and does not include manuscript files.

## What This Package Reproduces

- Main benchmark table from Ghana stream (`code/data/main_results.csv`)
- Figure 3: main comparison (`figures/fig03_main_comparison.png`, generated)
- Figure 4: latency distribution (`figures/fig04_latency_distribution.png`, generated)
- Figure 5: HITL trend (`figures/fig05_hitl_trend.png`, generated)
- Figure 6: tau ablation (`figures/fig06_tau_ablation.png`, generated)
- Figure 7: user profile (`figures/fig07_user_profile.png`, generated)
- Summary markdown and LaTeX table exports in `code/outputs/`

## Environment Setup

```bash
cd code
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Reproduction

From the repository root:

```bash
python code/src/reproduce.py
```

This regenerates the figure files in the top-level `figures/` folder and writes:

- `code/outputs/reproduction_summary.md`
- `code/outputs/table_main_results.tex`

## Publish and Get the URL

```bash
git init
git add .
git commit -m "Add NeurIPS reproducibility package"
git branch -M main
git remote add origin https://github.com/ShunbaoLi/pezego-hitl-neurips2026.git
git push -u origin main
```

Your code URL will be:

- `https://github.com/ShunbaoLi/pezego-hitl-neurips2026`

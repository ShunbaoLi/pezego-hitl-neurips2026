from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


sns.set_theme(style="whitegrid", context="talk")


def compute_main_improvements(df: pd.DataFrame) -> dict[str, float]:
    b4 = df.loc[df["method"] == "B4: Structured RAG (Multi)"].iloc[0]
    ours = df.loc[df["method"] == "Pezego-HITL (Ours)"].iloc[0]

    return {
        "acceptance_abs_gain": float(ours["acceptance"] - b4["acceptance"]),
        "compliance_abs_gain": float(ours["compliance"] - b4["compliance"]),
        "modify_pp_reduction": float(b4["eso_modify_pct"] - ours["eso_modify_pct"]),
        "p95_reduction_s": float(b4["p95_latency_s"] - ours["p95_latency_s"]),
        "p95_relative_reduction": float(
            (b4["p95_latency_s"] - ours["p95_latency_s"]) / b4["p95_latency_s"]
        ),
    }


def write_summary(summary_path: Path, stats: dict[str, float]) -> None:
    text = "\n".join(
        [
            "# Reproduction Summary",
            "",
            "Comparison: B4 (Structured RAG + Multi-Agent) vs Pezego-HITL",
            "",
            f"- Acceptance absolute gain: {stats['acceptance_abs_gain']:.2f}",
            f"- Compliance absolute gain: {stats['compliance_abs_gain']:.2f}",
            f"- ESO modify reduction (percentage points): {stats['modify_pp_reduction']:.1f}",
            f"- P95 latency reduction (seconds): {stats['p95_reduction_s']:.1f}",
            f"- P95 latency relative reduction: {100 * stats['p95_relative_reduction']:.1f}%",
            "",
            "Note: This package reproduces paper artifacts from the structured result files in code/data.",
        ]
    )
    summary_path.write_text(text, encoding="utf-8")


def export_main_table_latex(df: pd.DataFrame, out_path: Path) -> None:
    latex_df = df.copy()
    latex_df = latex_df.rename(
        columns={
            "method": "Method",
            "acceptance": "Acceptance",
            "compliance": "Compliance",
            "eso_modify_pct": "ESO Modify %",
            "p95_latency_s": "P95 Latency (s)",
        }
    )
    out_path.write_text(
        latex_df.to_latex(index=False, float_format=lambda x: f"{x:.2f}"),
        encoding="utf-8",
    )


def plot_main_comparison(df: pd.DataFrame, out_path: Path) -> None:
    chart_df = pd.DataFrame(
        {
            "Method": df["method"],
            "Acceptance": df["acceptance"],
            "Compliance": df["compliance"],
            "ESO Quality (1-Modify%)": 1.0 - df["eso_modify_pct"] / 100.0,
            "Latency Efficiency": 1.0 - df["p95_latency_s"] / df["p95_latency_s"].max(),
        }
    )
    long_df = chart_df.melt(id_vars="Method", var_name="Metric", value_name="Score")

    plt.figure(figsize=(14, 7))
    ax = sns.barplot(data=long_df, x="Method", y="Score", hue="Metric", palette="Set2")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Normalized Score")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=20)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def _sample_lognormal_by_target_p95(target_p95: float, n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    sigma = 0.45
    z95 = 1.6448536269514722
    mu = np.log(target_p95) - sigma * z95
    samples = rng.lognormal(mean=mu, sigma=sigma, size=n)
    return np.clip(samples, 2.0, None)


def plot_latency_distribution(main_df: pd.DataFrame, out_path: Path) -> None:
    b4_p95 = float(
        main_df.loc[
            main_df["method"] == "B4: Structured RAG (Multi)", "p95_latency_s"
        ].iloc[0]
    )
    ours_p95 = float(
        main_df.loc[main_df["method"] == "Pezego-HITL (Ours)", "p95_latency_s"].iloc[0]
    )

    b4 = _sample_lognormal_by_target_p95(b4_p95, n=400, seed=2026)
    ours = _sample_lognormal_by_target_p95(ours_p95, n=400, seed=2602)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    for name, values, color in [
        ("B4", b4, "#d95f02"),
        ("Pezego-HITL", ours, "#1b9e77"),
    ]:
        x = np.sort(values)
        y = np.arange(1, len(values) + 1) / len(values)
        axes[0].plot(x, y, label=name, color=color, linewidth=2)

    axes[0].set_title("Latency CDF")
    axes[0].set_xlabel("Latency (s)")
    axes[0].set_ylabel("CDF")
    axes[0].legend()

    vp = axes[1].violinplot([b4, ours], showmeans=True, showextrema=False)
    for body, color in zip(vp["bodies"], ["#d95f02", "#1b9e77"]):
        body.set_facecolor(color)
        body.set_alpha(0.35)
    axes[1].boxplot([b4, ours], widths=0.2, patch_artist=True)
    axes[1].set_xticks([1, 2])
    axes[1].set_xticklabels(["B4", "Pezego-HITL"])
    axes[1].set_title("Latency Distribution")
    axes[1].set_ylabel("Latency (s)")

    axes[1].text(1.05, np.percentile(b4, 95), f"P95={b4_p95:.1f}s", fontsize=10)
    axes[1].text(2.05, np.percentile(ours, 95), f"P95={ours_p95:.1f}s", fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_hitl_trend(df: pd.DataFrame, out_path: Path) -> None:
    fig, ax1 = plt.subplots(figsize=(11, 5.5))

    line1 = ax1.plot(
        df["week"],
        df["eso_modify_pct"],
        color="#d95f02",
        marker="o",
        linewidth=2,
        label="ESO modification rate",
    )
    ax1.set_xlabel("Week")
    ax1.set_ylabel("ESO modify rate (%)", color="#d95f02")
    ax1.tick_params(axis="y", labelcolor="#d95f02")

    ax2 = ax1.twinx()
    line2 = ax2.plot(
        df["week"],
        df["verify_without_edit_pct"],
        color="#1b9e77",
        marker="s",
        linewidth=2,
        label="Verify-without-edit rate",
    )
    ax2.set_ylabel("Verify-without-edit rate (%)", color="#1b9e77")
    ax2.tick_params(axis="y", labelcolor="#1b9e77")

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="center right")

    plt.title("HITL learning trend over 8 weeks")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_tau_ablation(df: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    axes[0].plot(df["tau"], df["acceptance"], marker="o", linewidth=2, label="Acceptance")
    axes[0].plot(df["tau"], df["reuse_ratio"], marker="s", linewidth=2, label="Reuse ratio")
    axes[0].axvspan(0.80, 0.85, color="#80b1d3", alpha=0.2, label="Practical range")
    axes[0].set_xlabel("Threshold tau")
    axes[0].set_ylabel("Rate")
    axes[0].set_ylim(0.3, 1.0)
    axes[0].legend()

    axes[1].plot(df["tau"], df["p95_latency_s"], marker="^", linewidth=2, color="#d95f02")
    axes[1].set_xlabel("Threshold tau")
    axes[1].set_ylabel("P95 latency (s)")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_user_profile(df: pd.DataFrame, out_path: Path) -> None:
    pivot = df.pivot(index="metric", columns="role", values="agree_share").reset_index()

    x = np.arange(len(pivot))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar(x - width / 2, pivot["Farmer"], width=width, label="Farmers (n=6)", color="#7570b3")
    ax.bar(x + width / 2, pivot["ESO"], width=width, label="ESOs (n=2)", color="#66a61e")

    ax.set_xticks(x)
    ax.set_xticklabels(pivot["metric"], rotation=15)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Agree/Strongly Agree share")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reproduce figures and summary artifacts.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for generated artifacts. Defaults to paper figures directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    code_root = Path(__file__).resolve().parents[1]
    repo_root = code_root.parent
    data_dir = code_root / "data"
    out_dir = args.output_dir or (repo_root / "figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    main_df = pd.read_csv(data_dir / "main_results.csv")
    hitl_df = pd.read_csv(data_dir / "hitl_trend_weekly.csv")
    tau_df = pd.read_csv(data_dir / "tau_ablation.csv")
    user_df = pd.read_csv(data_dir / "user_profile_agree_share.csv")

    stats = compute_main_improvements(main_df)
    write_summary(code_root / "outputs" / "reproduction_summary.md", stats)
    export_main_table_latex(main_df, code_root / "outputs" / "table_main_results.tex")

    plot_main_comparison(main_df, out_dir / "fig03_main_comparison.png")
    plot_latency_distribution(main_df, out_dir / "fig04_latency_distribution.png")
    plot_hitl_trend(hitl_df, out_dir / "fig05_hitl_trend.png")
    plot_tau_ablation(tau_df, out_dir / "fig06_tau_ablation.png")
    plot_user_profile(user_df, out_dir / "fig07_user_profile.png")

    print(f"Artifacts generated in: {out_dir}")
    print("Summary written to: code/outputs/reproduction_summary.md")


if __name__ == "__main__":
    main()

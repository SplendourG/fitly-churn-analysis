"""Visualization module for churn analysis."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def create_visuals(customer: pd.DataFrame, summaries: dict, output_dir: Path) -> None:
    """
    Generate publication-quality visualizations.
    
    Creates:
    - Plan distribution
    - Activity distribution histogram
    - Churn rate by plan
    - Support ticket volume by churn status
    - Churn heatmap (plan x support volume)
    
    Args:
        customer: Customer-level dataset.
        summaries: Dictionary of summary tables.
        output_dir: Path to save PNG files.
    """
    sns.set_theme(style="whitegrid", palette="Set2")

    # 01: Customers by plan
    plt.figure(figsize=(8, 5))
    order = customer["plan"].value_counts().index
    ax = sns.countplot(data=customer, x="plan", order=order)
    ax.set_title("Customers by subscription plan")
    ax.set_xlabel("Plan")
    ax.set_ylabel("Customers")
    plt.tight_layout()
    plt.savefig(output_dir / "01_customers_by_plan.png", dpi=180)
    plt.close()

    # 02: Activity distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(
        data=customer,
        x="activity_events",
        bins=range(0, int(customer["activity_events"].max()) + 2),
        ax=ax,
        color="#4C78A8",
    )
    ax.set_title("Activity Events per Customer")
    ax.set_xlabel("Activity events")
    ax.set_ylabel("Customers")
    fig.tight_layout()
    fig.savefig(output_dir / "02_activity_distribution.png", dpi=180)
    plt.close(fig)

    # 03: Churn rate by plan
    plt.figure(figsize=(8, 5))
    plan_summary = summaries["plan_summary"].copy()
    plan_summary["churn_rate_pct"] = plan_summary["churn_rate"] * 100
    ax = sns.barplot(data=plan_summary, x="plan", y="churn_rate_pct", color="#F58518")
    ax.set_title("Churn rate by plan")
    ax.set_xlabel("Plan")
    ax.set_ylabel("Churn rate (%)")
    ax.bar_label(ax.containers[0], fmt="%.1f%%", padding=3)
    plt.tight_layout()
    plt.savefig(output_dir / "03_churn_rate_by_plan.png", dpi=180)
    plt.close()

    # 04: Support tickets by churn status
    plt.figure(figsize=(8, 5))
    ax = sns.boxplot(data=customer, x="churned", y="support_tickets", color="#54A24B")
    ax.set_title("Support ticket volume by churn status")
    ax.set_xlabel("Churned (0 = retained, 1 = churned)")
    ax.set_ylabel("Support tickets")
    plt.tight_layout()
    plt.savefig(output_dir / "04_support_tickets_by_churn.png", dpi=180)
    plt.close()

    # 05: Churn heatmap (plan x support volume)
    plt.figure(figsize=(8, 5))
    heatmap_data = customer.pivot_table(
        index="plan",
        columns=pd.cut(
            customer["support_tickets"],
            bins=[-1, 0, 1, 3, customer["support_tickets"].max()],
            labels=["0", "1", "2-3", "4+"],
            include_lowest=True,
        ),
        values="churned",
        aggfunc="mean",
        observed=False,
    )
    ax = sns.heatmap(
        heatmap_data * 100,
        annot=True,
        fmt=".1f",
        cmap="rocket_r",
        cbar_kws={"label": "Churn rate (%)"},
    )
    ax.set_title("Churn rate by plan and support volume")
    ax.set_xlabel("Support tickets")
    ax.set_ylabel("Plan")
    plt.tight_layout()
    plt.savefig(output_dir / "05_churn_heatmap_plan_support.png", dpi=180)
    plt.close()

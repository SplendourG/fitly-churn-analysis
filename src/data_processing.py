"""Data aggregation and feature engineering module."""
from typing import Dict

import pandas as pd


def create_summaries(
    customer: pd.DataFrame,
    activity: pd.DataFrame,
    support: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """
    Create summary tables for churn analysis.
    
    Generates:
    - Overall retention metrics
    - Churn by plan
    - Churn by engagement level
    - Churn by support volume
    - Event type distribution
    - Support topic distribution
    - Impact of delete requests on churn
    
    Args:
        customer: Customer-level dataset with all features.
        activity: Activity records (used for event summary).
        support: Support records (used for topic summary).
    
    Returns:
        Dictionary of summary dataframes.
    """
    # Overall metrics
    overall = pd.DataFrame(
        [
            {
                "customers": len(customer),
                "churned_customers": int(customer["churned"].sum()),
                "retained_customers": int((customer["churned"] == 0).sum()),
                "retention_rate": 1 - customer["churned"].mean(),
                "churn_rate": customer["churned"].mean(),
                "avg_plan_list_price": customer["plan_list_price"].mean(),
                "avg_activity_events": customer["activity_events"].mean(),
                "avg_support_tickets": customer["support_tickets"].mean(),
                "delete_request_rate": customer["has_delete_request"].mean(),
            }
        ]
    )

    # Churn by plan
    plan_summary = (
        customer.groupby("plan", dropna=False)
        .agg(
            customers=("user_id", "size"),
            churned=("churned", "sum"),
            churn_rate=("churned", "mean"),
            avg_plan_list_price=("plan_list_price", "mean"),
            avg_activity_events=("activity_events", "mean"),
            avg_support_tickets=("support_tickets", "mean"),
            avg_resolution_hours=("avg_resolution_hours", "mean"),
            delete_request_rate=("has_delete_request", "mean"),
        )
        .reset_index()
        .sort_values("churn_rate", ascending=False)
    )

    # Churn by engagement band
    engagement_summary = (
        customer.assign(
            engagement_band=pd.cut(
                customer["activity_events"],
                bins=[-1, 0, 1, 3, customer["activity_events"].max()],
                labels=["No events", "1 event", "2-3 events", "4+ events"],
                include_lowest=True,
            )
        )
        .groupby("engagement_band", observed=False)
        .agg(customers=("user_id", "size"), churn_rate=("churned", "mean"))
        .reset_index()
    )

    # Churn by support volume band
    support_volume_summary = (
        customer.assign(
            support_band=pd.cut(
                customer["support_tickets"],
                bins=[-1, 0, 1, 3, customer["support_tickets"].max()],
                labels=["No tickets", "1 ticket", "2-3 tickets", "4+ tickets"],
                include_lowest=True,
            )
        )
        .groupby("support_band", observed=False)
        .agg(customers=("user_id", "size"), churn_rate=("churned", "mean"))
        .reset_index()
    )

    # Event type distribution
    event_summary = (
        activity.groupby("event_type")
        .agg(events=("user_id", "size"), users=("user_id", "nunique"))
        .reset_index()
        .sort_values("events", ascending=False)
    )

    # Support topic distribution and resolution metrics
    support_topic_summary = (
        support.groupby("topic")
        .agg(
            tickets=("user_id", "size"),
            users=("user_id", "nunique"),
            avg_resolution_hours=("resolution_time_hours", "mean"),
            delete_request_rate=("has_delete_request", "mean"),
        )
        .reset_index()
        .sort_values("tickets", ascending=False)
    )

    # Impact of delete requests on churn
    churn_by_delete = (
        customer.groupby("has_delete_request")
        .agg(customers=("user_id", "size"), churn_rate=("churned", "mean"))
        .reset_index()
    )

    return {
        "overall": overall,
        "plan_summary": plan_summary,
        "engagement_summary": engagement_summary,
        "support_volume_summary": support_volume_summary,
        "event_summary": event_summary,
        "support_topic_summary": support_topic_summary,
        "churn_by_delete": churn_by_delete,
    }

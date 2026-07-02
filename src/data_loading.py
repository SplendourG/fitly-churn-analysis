"""Data loading and initial cleaning module."""
import re
from pathlib import Path
from typing import Dict

import pandas as pd


def clean_customer_id(value) -> int:
    """
    Extract numeric customer ID from strings like "C10000".
    
    Args:
        value: Raw customer ID value (may contain letters/formatting).
    
    Returns:
        Numeric customer ID or pd.NA if extraction fails.
    """
    if pd.isna(value):
        return pd.NA
    match = re.search(r"(\d+)", str(value))
    return int(match.group(1)) if match else pd.NA


def yes_no_to_binary(value) -> int:
    """
    Convert yes/no values to binary 1/0.
    
    Missing values treated as 0 (not churned).
    
    Args:
        value: Raw yes/no value (case-insensitive).
    
    Returns:
        1 for yes/true, 0 for no/false/missing.
    """
    if pd.isna(value):
        return 0
    value = str(value).strip().upper()
    if value in {"Y", "YES", "1", "TRUE"}:
        return 1
    if value in {"N", "NO", "0", "FALSE"}:
        return 0
    return pd.NA


def load_and_clean(
    data_dir: Path = Path("data/raw"),
) -> Dict[str, pd.DataFrame]:
    """
    Load, clean, and merge three datasets into a customer-level table.
    
    This function:
    1. Loads account, activity, and support CSV files
    2. Normalizes column names and data types
    3. Creates derived features (e.g., delete requests)
    4. Deduplicates records
    5. Aggregates activity and support to customer level
    6. Left-joins to account records to retain all customers
    
    Args:
        data_dir: Directory containing raw CSV files.
    
    Returns:
        Dictionary with cleaned dataframes:
        - account_raw, activity_raw, support_raw: Original data
        - account, activity, support: Cleaned single-source data
        - customer: Final customer-level analysis table
        - validation: Data quality summary
    """
    # Load raw data
    account_raw = pd.read_csv(data_dir / "da_fitly_account_info.csv")
    activity_raw = pd.read_csv(data_dir / "da_fitly_user_activity.csv")
    support_raw = pd.read_csv(data_dir / "da_fitly_customer_support.csv")

    # Make working copies
    account = account_raw.copy()
    support = support_raw.copy()
    activity = activity_raw.copy()

    # Normalize column names
    account.columns = account.columns.str.strip().str.lower()
    support.columns = support.columns.str.strip().str.lower()
    activity.columns = activity.columns.str.strip().str.lower()

    # Rename ambiguous columns
    account = account.rename(columns={"state": "customer_state", "churn_status": "churn"})
    support = support.rename(columns={"state": "ticket_closed"})

    # Clean account table
    account["user_id"] = account["customer_id"].apply(clean_customer_id).astype("Int64")
    account["email"] = account["email"].astype("string").str.strip().str.lower()
    account["customer_state"] = (
        account["customer_state"].astype("string").str.strip().str.title()
    )
    account["plan"] = account["plan"].astype("string").str.strip().str.title()
    account["plan_list_price"] = pd.to_numeric(account["plan_list_price"], errors="coerce")
    account["churned"] = account["churn"].apply(yes_no_to_binary).astype("Int64")
    account["churned"] = account["churned"].fillna(0).astype(int)

    # Clean activity table
    activity["event_time"] = pd.to_datetime(activity["event_time"], errors="coerce")
    activity["user_id"] = pd.to_numeric(activity["user_id"], errors="coerce").astype("Int64")
    activity["event_type"] = activity["event_type"].astype("string").str.strip().str.lower()

    # Clean support table
    support["ticket_time"] = pd.to_datetime(support["ticket_time"], errors="coerce")
    support["user_id"] = pd.to_numeric(support["user_id"], errors="coerce").astype("Int64")
    support["channel"] = support["channel"].astype("string").str.strip().str.lower()
    support["topic"] = support["topic"].astype("string").str.strip().str.lower()
    support["resolution_time_hours"] = pd.to_numeric(
        support["resolution_time_hours"], errors="coerce"
    )
    support["ticket_closed"] = pd.to_numeric(support["ticket_closed"], errors="coerce").astype(
        "Int64"
    )
    support["comments"] = support["comments"].astype("string").fillna("").str.strip()

    # Create delete request flag
    support["has_delete_request"] = support["comments"].str.contains(
        r"\b(?:delete|erase|remove|wipe|forgotten|erasure|deletion)\b.*\b(?:data|account|profile|information|records|details)\b|"
        r"\b(?:data|account|profile|information|records|details)\b.*\b(?:delete|erase|remove|wipe|forgotten|erasure|deletion)\b",
        case=False,
        regex=True,
        na=False,
    )

    # Remove duplicates
    account = account.drop_duplicates(subset=["user_id"], keep="first")
    activity = activity.drop_duplicates()
    support = support.drop_duplicates()

    # Aggregate activity to customer level
    activity_summary = (
        activity.groupby("user_id", dropna=False)
        .agg(
            activity_events=("event_type", "size"),
            active_days=("event_time", lambda s: s.dt.date.nunique()),
            first_event=("event_time", "min"),
            last_event=("event_time", "max"),
        )
        .reset_index()
    )

    # Pivot event types into separate columns
    event_mix = (
        activity.pivot_table(
            index="user_id",
            columns="event_type",
            values="event_time",
            aggfunc="size",
            fill_value=0,
        )
        .add_prefix("event_")
        .reset_index()
    )

    # Aggregate support to customer level
    support_summary = (
        support.groupby("user_id", dropna=False)
        .agg(
            support_tickets=("topic", "size"),
            avg_resolution_hours=("resolution_time_hours", "mean"),
            max_resolution_hours=("resolution_time_hours", "max"),
            unresolved_tickets=("ticket_closed", lambda s: (s == 0).sum()),
            delete_request_count=("has_delete_request", "sum"),
        )
        .reset_index()
    )
    support_summary["has_delete_request"] = support_summary["delete_request_count"] > 0

    # Merge all tables at customer level
    customer = (
        account.merge(activity_summary, on="user_id", how="left")
        .merge(event_mix, on="user_id", how="left")
        .merge(support_summary, on="user_id", how="left")
    )

    # Clean up merged columns
    count_columns = [
        "activity_events",
        "active_days",
        "support_tickets",
        "unresolved_tickets",
        "delete_request_count",
    ] + [c for c in customer.columns if c.startswith("event_")]
    for col in count_columns:
        if col in customer.columns:
            customer[col] = customer[col].fillna(0).astype(int)
    customer["avg_resolution_hours"] = customer["avg_resolution_hours"].fillna(0)
    customer["max_resolution_hours"] = customer["max_resolution_hours"].fillna(0)
    customer["has_delete_request"] = customer["has_delete_request"].fillna(False)

    # Generate validation summary
    validation = []
    for name, df in [
        ("account_info_raw", account_raw),
        ("user_activity_raw", activity_raw),
        ("customer_support_raw", support_raw),
        ("customer_clean", customer),
    ]:
        validation.append(
            {
                "table": name,
                "rows": len(df),
                "columns": len(df.columns),
                "duplicate_rows": int(df.duplicated().sum()),
                "missing_cells": int(df.isna().sum().sum()),
            }
        )

    return {
        "account_raw": account_raw,
        "activity_raw": activity_raw,
        "support_raw": support_raw,
        "account": account,
        "activity": activity,
        "support": support,
        "customer": customer,
        "validation": pd.DataFrame(validation),
    }

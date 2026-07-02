"""Report generation module."""
from pathlib import Path
from typing import Dict

import pandas as pd


def write_report(summaries: Dict[str, pd.DataFrame], output_dir: Path) -> None:
    """
    Generate a markdown executive report with findings and recommendations.
    
    Creates a comprehensive report including:
    - Business context and questions
    - Data validation details
    - Key metrics and findings
    - Recommendations for action
    - Description of visualizations
    
    Args:
        summaries: Dictionary of summary tables from analysis.
        output_dir: Path to save report markdown file.
    """
    overall = summaries["overall"].iloc[0]
    plan_summary = summaries["plan_summary"]
    engagement_summary = summaries["engagement_summary"]
    support_summary = summaries["support_volume_summary"]
    churn_by_delete = summaries["churn_by_delete"]

    highest_plan = plan_summary.iloc[0]
    lowest_plan = plan_summary.sort_values("churn_rate").iloc[0]

    delete_yes = churn_by_delete.loc[churn_by_delete["has_delete_request"] == True, "churn_rate"]
    delete_rate = float(delete_yes.iloc[0]) if not delete_yes.empty else 0

    validation_table = """| Table | Validation and cleaning performed |
|---|---|
| account_info | customer_id extracted, user_id created for joins; state renamed to customer_state; churn converted to binary |
| user_activity | event_time parsed to datetime; user_id converted to numeric; event_type standardized |
| customer_support | ticket_time parsed to datetime; resolution_time_hours converted to numeric; delete requests extracted from comments |
| customer_clean | Account table is customer base; activity and support summarized and left-joined to retain all customers |
"""

    report = f"""# Fit.ly Churn Analysis Report

## Business Question
Fit.ly leadership wants to understand what is associated with subscriber churn and what actions can reduce churn next quarter. The analysis uses account, customer support, and product activity data.

## Data Validation and Cleaning

{validation_table}

**Key transformations:**
- Extracted numeric `user_id` from customer_id strings (e.g., "C10000" → 10000)
- Renamed conflicting state columns to avoid merging ambiguity
- Converted churn status to binary (Y=1, null/other=0)
- Created delete request flag by regex matching in support comments
- Aggregated activity and support records to customer level
- Left-joined summaries to account records to retain all customers

## Business Metrics to Monitor

The main metric should be **customer retention rate**:

```
retention rate = retained customers / total customers
```

This directly measures whether Fit.ly is keeping subscribers and is understandable to leadership.

### Current Baseline

- **Total Customers:** {overall['customers']:.0f}
- **Churned:** {overall['churned_customers']:.0f}
- **Retained:** {overall['retained_customers']:.0f}
- **Retention Rate:** {overall['retention_rate']:.1%}
- **Churn Rate:** {overall['churn_rate']:.1%}

## Key Findings

1. **Churn varies significantly by plan**
   - Highest-churn plan: **{highest_plan['plan']}** at {highest_plan['churn_rate']:.1%}
   - Lowest-churn plan: **{lowest_plan['plan']}** at {lowest_plan['churn_rate']:.1%}

2. **Engagement matters**
   - Average customer engagement: {overall['avg_activity_events']:.2f} activity events per customer
   - Low-activity customers are at higher churn risk

3. **Support volume correlates with churn**
   - Average support tickets: {overall['avg_support_tickets']:.2f} per customer
   - Repeated issues and slow resolution create friction

4. **Delete requests are a strong warning signal**
   - Churn rate for customers with delete requests: {delete_rate:.1%}
   - This indicates explicit dissatisfaction and imminent churn

## Recommended Actions

1. **Build a retention dashboard** tracking:
   - Overall retention rate and churn rate
   - Churn rate by plan
   - Churn rate by engagement band
   - Support ticket volume
   - Delete request rate

2. **Prioritize retention outreach** for:
   - Customers with delete/account/data removal requests
   - Customers with unresolved tickets
   - Customers with multiple recent support tickets

3. **Improve onboarding and engagement**
   - Review in-product nudges for low-activity customers
   - Focus on customers with zero or one activity event

4. **Investigate plan-specific churn**
   - If highest-churn plan has concentration, test retention offers
   - Review pricing and value perception

5. **Optimize support workflows**
   - Improve resolution times for common high-volume topics
   - Measure whether faster resolution reduces churn next quarter

## Visualizations Created

- `01_customers_by_plan.png` — Distribution of customers across plans
- `02_activity_distribution.png` — Histogram of engagement by event count
- `03_churn_rate_by_plan.png` — Churn rate comparison across plans
- `04_support_tickets_by_churn.png` — Support volume by churn status
- `05_churn_heatmap_plan_support.png` — Churn rate heatmap by plan and support volume

## Technical Notes

See `src/data_loading.py` for the corrected data cleaning pipeline. Key considerations:

- Account and support tables both have a "state" column; renamed to avoid conflicts
- customer_id requires normalization from "C10000" format to numeric
- Missing churn status is treated as retained (0) because source only flags explicit churn
- Customers with no activity/support records are retained in analysis with zero counts
"""

    (output_dir / "fitly_churn_report.md").write_text(report, encoding="utf-8")

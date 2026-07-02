"""Unit tests for data processing and aggregation."""
import pandas as pd
import pytest
from src.data_processing import create_summaries


class TestCreateSummaries:
    """Tests for create_summaries function."""

    @pytest.fixture
    def sample_customer_data(self):
        """Create sample customer dataset for testing."""
        return pd.DataFrame(
            {
                "user_id": [1, 2, 3, 4, 5],
                "plan": ["Basic", "Pro", "Basic", "Premium", "Pro"],
                "churned": [0, 1, 0, 1, 0],
                "activity_events": [0, 5, 2, 10, 1],
                "support_tickets": [0, 3, 1, 5, 0],
                "avg_resolution_hours": [0, 10, 5, 20, 0],
                "has_delete_request": [False, True, False, True, False],
                "plan_list_price": [9.99, 29.99, 9.99, 99.99, 29.99],
            }
        )

    @pytest.fixture
    def sample_activity_data(self):
        """Create sample activity dataset."""
        return pd.DataFrame(
            {
                "user_id": [1, 1, 2, 3, 4, 4],
                "event_type": ["login", "workout", "login", "login", "workout", "login"],
                "event_time": pd.date_range("2024-01-01", periods=6),
            }
        )

    @pytest.fixture
    def sample_support_data(self):
        """Create sample support dataset."""
        return pd.DataFrame(
            {
                "user_id": [2, 2, 3, 4],
                "topic": ["billing", "technical", "general", "billing"],
                "resolution_time_hours": [10, 15, 5, 20],
                "has_delete_request": [False, True, False, True],
            }
        )

    def test_overall_metrics(self, sample_customer_data, sample_activity_data, sample_support_data):
        """Should calculate correct overall metrics."""
        summaries = create_summaries(
            sample_customer_data,
            sample_activity_data,
            sample_support_data,
        )
        overall = summaries["overall"].iloc[0]

        assert overall["customers"] == 5
        assert overall["churned_customers"] == 2
        assert overall["retained_customers"] == 3
        assert overall["churn_rate"] == pytest.approx(0.4)

    def test_plan_summary_exists(self, sample_customer_data, sample_activity_data, sample_support_data):
        """Should create plan summary with expected columns."""
        summaries = create_summaries(
            sample_customer_data,
            sample_activity_data,
            sample_support_data,
        )
        plan_summary = summaries["plan_summary"]

        assert "plan" in plan_summary.columns
        assert "churn_rate" in plan_summary.columns
        assert "customers" in plan_summary.columns
        assert len(plan_summary) >= 1

    def test_all_summaries_returned(self, sample_customer_data, sample_activity_data, sample_support_data):
        """Should return all expected summary tables."""
        summaries = create_summaries(
            sample_customer_data,
            sample_activity_data,
            sample_support_data,
        )

        expected_keys = {
            "overall",
            "plan_summary",
            "engagement_summary",
            "support_volume_summary",
            "event_summary",
            "support_topic_summary",
            "churn_by_delete",
        }
        assert set(summaries.keys()) == expected_keys

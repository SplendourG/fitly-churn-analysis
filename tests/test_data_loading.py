"""Unit tests for data loading and cleaning."""
import pytest
import pandas as pd
from src.data_loading import clean_customer_id, yes_no_to_binary


class TestCleanCustomerId:
    """Tests for clean_customer_id function."""

    def test_extract_from_string(self):
        """Should extract numeric ID from string like 'C10000'."""
        assert clean_customer_id("C10000") == 10000
        assert clean_customer_id("C123") == 123

    def test_extract_from_numeric(self):
        """Should handle numeric input."""
        assert clean_customer_id(10000) == 10000

    def test_handles_nan(self):
        """Should return pd.NA for NaN input."""
        assert pd.isna(clean_customer_id(pd.NA))
        assert pd.isna(clean_customer_id(None))

    def test_no_numeric_found(self):
        """Should return pd.NA if no numeric part found."""
        assert pd.isna(clean_customer_id("ABC"))


class TestYesNoToBinary:
    """Tests for yes_no_to_binary function."""

    def test_yes_values(self):
        """Should convert yes/true values to 1."""
        assert yes_no_to_binary("Y") == 1
        assert yes_no_to_binary("YES") == 1
        assert yes_no_to_binary("yes") == 1
        assert yes_no_to_binary("1") == 1
        assert yes_no_to_binary("TRUE") == 1

    def test_no_values(self):
        """Should convert no/false values to 0."""
        assert yes_no_to_binary("N") == 0
        assert yes_no_to_binary("NO") == 0
        assert yes_no_to_binary("no") == 0
        assert yes_no_to_binary("0") == 0
        assert yes_no_to_binary("FALSE") == 0

    def test_missing_values(self):
        """Should treat NaN/missing as 0 (not churned)."""
        assert yes_no_to_binary(pd.NA) == 0
        assert yes_no_to_binary(None) == 0

    def test_invalid_values(self):
        """Should return pd.NA for unrecognized values."""
        assert pd.isna(yes_no_to_binary("MAYBE"))
        assert pd.isna(yes_no_to_binary("unknown"))

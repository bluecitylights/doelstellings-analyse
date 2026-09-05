import pandas as pd
import pytest
from join_parquet import join_data


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def df_a():
    return pd.DataFrame({
        "artikelnr": [1, 2, 3],
        "f1": ["a1", "a2", "a3"],
        "f2": ["b1", "b2", "b3"],
        "f3": ["c1", "c2", "c3"],
        "extra_col": ["x", "y", "z"],  # should NOT appear in result (not selected)
    })


@pytest.fixture
def df_b():
    return pd.DataFrame({
        "artikelnr": [1, 2, 4],           # artikelnr 3 absent, 4 only in B
        "startdatum": pd.to_datetime(["2024-01-08", "2024-01-15", "2024-01-22"]),
        "einddatum":  pd.to_datetime(["2024-03-31", "2024-04-30", "2024-05-31"]),
        "omschrijving": ["desc1", "desc2", "desc4"],
    })


@pytest.fixture
def df_c():
    return pd.DataFrame({
        "artikelnr": [1, 2, 5],           # artikelnr 5 only in C
        "year":      [2024, 2024, 2024],
        "week":      [2, 3, 4],
        "doelstelling": [100, 200, 300],
    })


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_result_is_dataframe(df_a, df_b, df_c):
    result = join_data(df_a, df_b, df_c)
    assert isinstance(result, pd.DataFrame)


def test_artikelnr_in_result(df_a, df_b, df_c):
    result = join_data(df_a, df_b, df_c)
    assert "artikelnr" in result.columns


def test_selected_a_columns_present(df_a, df_b, df_c):
    result = join_data(df_a, df_b, df_c)
    for col in ["f1", "f2", "f3"]:
        assert col in result.columns, f"Column {col} missing from result"


def test_extra_a_column_not_present(df_a, df_b, df_c):
    """extra_col from A should be dropped (only f1,f2,f3 selected)."""
    result = join_data(df_a, df_b, df_c)
    assert "extra_col" not in result.columns


def test_b_columns_present(df_a, df_b, df_c):
    result = join_data(df_a, df_b, df_c)
    assert "omschrijving" in result.columns


def test_c_columns_present(df_a, df_b, df_c):
    result = join_data(df_a, df_b, df_c)
    assert "doelstelling" in result.columns


def test_year_week_columns_extracted(df_a, df_b, df_c):
    result = join_data(df_a, df_b, df_c)
    assert "year" in result.columns
    assert "week" in result.columns


def test_year_week_values_correct(df_a, df_b, df_c):
    """artikelnr=1: startdatum 2024-01-08 is ISO week 2 of 2024."""
    result = join_data(df_a, df_b, df_c)
    row = result[result["artikelnr"] == 1].iloc[0]
    assert int(row["year"]) == 2024
    assert int(row["week"]) == 2


def test_end_year_week_columns_extracted(df_a, df_b, df_c):
    result = join_data(df_a, df_b, df_c)
    assert "end_year" in result.columns
    assert "end_week" in result.columns


def test_outer_join_keeps_all_artikelnrs(df_a, df_b, df_c):
    """Outer join: all artikelnrs from A, B, and C should appear."""
    result = join_data(df_a, df_b, df_c)
    result_artikelnrs = set(result["artikelnr"].dropna().astype(int))
    assert {1, 2, 3, 4, 5}.issubset(result_artikelnrs)


def test_no_duplicate_rows_for_matching_key(df_a, df_b, df_c):
    """artikelnr=1 with matching year+week should appear exactly once."""
    result = join_data(df_a, df_b, df_c)
    match = result[(result["artikelnr"] == 1) & (result["week"] == 2)]
    assert len(match) == 1

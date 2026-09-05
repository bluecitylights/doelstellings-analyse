import pandas as pd


def join_data(df_a: pd.DataFrame, df_b: pd.DataFrame, df_c: pd.DataFrame) -> pd.DataFrame:
    """
    Join three DataFrames:
      - A + B on artikelnr  (A: f1, f2, f3 only; B: all columns)
      - Extract ISO year + week from B's start/end date columns
      - Join result + C on artikelnr + year + week  (C: all columns)
    """
    # ── Step 1: Join A + B on artikelnr ──────────────────────────────────────
    # From A: only f1, f2, f3 (plus artikelnr for the join key)
    df_a_sel = df_a[["Artikelnummer", "f1", "f2", "f3"]]

    # From B: all columns
    df_ab = df_a_sel.merge(df_b, left_on="Artikelnummer", right_on="Artikelnr.", how="outer")

    # ── Step 2: Extract ISO year + week from B's date columns ────────────────
    # Adjust 'startdatum' / 'einddatum' to your actual column names in parquet B
    df_ab["Startdatum"] = pd.to_datetime(df_ab["Startdatum"], format="%d-%m-%Y", errors="coerce")
    df_ab["Einddatum"]  = pd.to_datetime(df_ab["Einddatum"], format="%d-%m-%Y", errors="coerce")

    df_ab["start_year"] = df_ab["Startdatum"].dt.isocalendar().year.astype("Int64")
    df_ab["start_week"] = df_ab["Startdatum"].dt.isocalendar().week.astype("Int64")
    df_ab["end_year"]   = df_ab["Einddatum"].dt.isocalendar().year.astype("Int64")
    df_ab["end_week"]   = df_ab["Einddatum"].dt.isocalendar().week.astype("Int64")

    # ── Step 3: Join with C on artikelnr + year + week ───────────────────────
    # Uses the start date's year/week as the join key — swap to end_ if needed
    df_for_join = df_ab.rename(columns={"start_year": "year", "start_week": "week"})

    df_c["JAAR"] = pd.to_numeric(df_c["JAAR"], errors="coerce").astype("Int64")
    df_c["WK"] = pd.to_numeric(df_c["WK"], errors="coerce").astype("Int64")
    
    df_result = df_for_join.merge(
        df_c,
        left_on=["Artikelnr.", "year", "week"],
        right_on=["IG", "JAAR", "WK"],
        how="outer",
        suffixes=("_ab", "_c"),  # avoids column name collisions between B and C
    )
    df_result = df_for_join

    return df_result

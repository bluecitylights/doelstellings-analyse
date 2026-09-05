import pandas as pd

# ── D020 column names ─────────────────────────────────────────────────────────
D020_ARTIKELNR   = "Artikelnummer"
D020_SELECT_COLS = ["f1", "f2", "f3"]  # extra kolommen die mee worden genomen uit D020

# ── TP041 column names ────────────────────────────────────────────────────────
TP041_ARTIKELNR  = "Artikelnr."
TP041_STARTDATUM = "Startdatum"
TP041_EINDDATUM  = "Einddatum"

# ── TO012 column names ────────────────────────────────────────────────────────
TO012_ARTIKELNR = "IG"
TO012_JAAR      = "JAAR"
TO012_WEEK      = "WK"


def join_data(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    df_c: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join three DataFrames:
      - D020 + TP041 on artikelnr  (D020: selected fields only; TP041: all columns)
      - Extract ISO year + week from TP041's start/end date columns
      - Join result + TO012 on artikelnr + year + week  (TO012: all columns)
    """
    # ── Step 1: Join D020 + TP041 on artikelnr ────────────────────────────────
    df_a_sel = df_a[[D020_ARTIKELNR, *D020_SELECT_COLS]]

    df_ab = df_a_sel.merge(
        df_b,
        left_on=D020_ARTIKELNR,
        right_on=TP041_ARTIKELNR,
        how="outer",
    )

    # ── Step 2: Extract ISO year + week from TP041's date columns ─────────────
    df_ab[TP041_STARTDATUM] = pd.to_datetime(df_ab[TP041_STARTDATUM], format="%d-%m-%Y", errors="coerce")
    df_ab[TP041_EINDDATUM]  = pd.to_datetime(df_ab[TP041_EINDDATUM],  format="%d-%m-%Y", errors="coerce")

    df_ab["start_year"] = df_ab[TP041_STARTDATUM].dt.isocalendar().year.astype("Int64")
    df_ab["start_week"] = df_ab[TP041_STARTDATUM].dt.isocalendar().week.astype("Int64")
    df_ab["end_year"]   = df_ab[TP041_EINDDATUM].dt.isocalendar().year.astype("Int64")
    df_ab["end_week"]   = df_ab[TP041_EINDDATUM].dt.isocalendar().week.astype("Int64")

    # ── Step 3: Join with TO012 on artikelnr + year + week ────────────────────
    df_c[TO012_JAAR] = pd.to_numeric(df_c[TO012_JAAR], errors="coerce").astype("Int64")
    df_c[TO012_WEEK] = pd.to_numeric(df_c[TO012_WEEK], errors="coerce").astype("Int64")

    df_result = df_ab.merge(
        df_c,
        left_on=[TP041_ARTIKELNR, "start_year", "start_week"],
        right_on=[TO012_ARTIKELNR, TO012_JAAR, TO012_WEEK],
        how="outer",
        suffixes=("_ab", "_c"),
    )

    return df_result

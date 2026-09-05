import os
import pandas as pd
from join_parquet import join_data

# ── File paths — adjust to your actual xlsx filenames ─────────────────────────
# Tuple: (xlsx_path, parquet_path, sheet_name)
# xlsx files are read from the project root; parquet cache goes into data/
os.makedirs("data", exist_ok=True)

FILES = {
    "a": ("data_a.xlsx", "data/data_a.parquet", "Tabblad1"),
    "b": ("data_b.xlsx", "data/data_b.parquet", "Tabblad1"),
    "c": ("data_c.xlsx", "data/data_c.parquet", "Tabblad1"),
}


def xlsx_to_parquet(xlsx_path: str, parquet_path: str, sheet_name: str = "Tabblad1") -> None:
    """Convert xlsx to parquet if parquet doesn't exist or xlsx is newer."""
    xlsx_mtime = os.path.getmtime(xlsx_path)
    if os.path.exists(parquet_path):
        if xlsx_mtime <= os.path.getmtime(parquet_path):
            print(f"[cache] {parquet_path} up to date, skipping")
            return
    print(f"[convert] {xlsx_path} (sheet: {sheet_name}) -> {parquet_path}")
    pd.read_excel(xlsx_path, sheet_name=sheet_name, engine="openpyxl").to_parquet(parquet_path, index=False)


def main():
    # ── 1. Convert xlsx -> parquet (skips if already up to date) ─────────────
    for key, (xlsx, parquet, sheet) in FILES.items():
        xlsx_to_parquet(xlsx, parquet, sheet)

    # ── 2. Load parquet files ─────────────────────────────────────────────────
    df_a = pd.read_parquet(FILES["a"][1])
    df_b = pd.read_parquet(FILES["b"][1])
    df_c = pd.read_parquet(FILES["c"][1])

    # ── 3. Join ───────────────────────────────────────────────────────────────
    result = join_data(df_a, df_b, df_c)

    print(f"Result shape: {result.shape}")
    print(result.head())


if __name__ == "__main__":
    main()

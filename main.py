from pathlib import Path

import pandas as pd

from join_parquet import join_data

# ── File paths — adjust to your actual xlsx filenames ─────────────────────────
# Tuple: (xlsx_path, parquet_path, sheet_name)
EXCEL_DIR = Path(r"<path>")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FILES: dict[str, tuple[Path, Path, str]] = {
    "d020":  (EXCEL_DIR / "D020.xlsx",  DATA_DIR / "D020.parquet",  "D020"),
    "to012": (EXCEL_DIR / "TO012.xlsx", DATA_DIR / "TO012.parquet", "Tabel DimensieKPI_data"),
    "tp041": (EXCEL_DIR / "TP041.xlsx", DATA_DIR / "TP041.parquet", "TP041"),
}


def xlsx_to_parquet(xlsx_path: Path, parquet_path: Path, sheet_name: str = "Tabblad1") -> None:
    """Convert xlsx to parquet if parquet doesn't exist or xlsx is newer."""
    xlsx_mtime = xlsx_path.stat().st_mtime
    if parquet_path.exists():
        if xlsx_mtime <= parquet_path.stat().st_mtime:
            print(f"[cache] {parquet_path} up to date, skipping")
            return
    print(f"[convert] {xlsx_path} (sheet: {sheet_name}) -> {parquet_path}")
    pd.read_excel(xlsx_path, sheet_name=sheet_name, engine="openpyxl", dtype=str).to_parquet(parquet_path, index=False)


def main() -> None:
    print("Analyseer")
    
    # ── 1. Convert xlsx -> parquet (skips if already up to date) ─────────────
    for _key, (xlsx, parquet, sheet) in FILES.items():
        xlsx_to_parquet(xlsx, parquet, sheet)

    # ── 2. Load parquet files ─────────────────────────────────────────────────
    df_a = pd.read_parquet(FILES["d020"][1])
    print(f"Result shape: {df_a.shape}")
    print(df_a.head())
    df_b = pd.read_parquet(FILES["tp041"][1])
    print(f"Result shape: {df_b.shape}")
    print(df_b.head())
    df_c = pd.read_parquet(FILES["to012"][1])
    print(f"Result shape: {df_c.shape}")
    print(df_c.head())

    # ── 3. Join ───────────────────────────────────────────────────────────────
    result = join_data(df_a, df_b, df_c)

    print(f"Result shape: {result.shape}")
    print(result.head())

    result.to_excel("data/resultaat.xlsx", index=False)


if __name__ == "__main__":
    main()
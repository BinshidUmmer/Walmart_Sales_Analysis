# src/etl/load.py
from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def write_parquet(df: pd.DataFrame, filename: str):
    out = PROCESSED_DIR / filename
    # pandas uses pyarrow or fastparquet backend; pyarrow recommended
    df.to_parquet(out, index=False)
    return out

if __name__ == "__main__":
    # example quick test
    import sys
    from extract import load_csv
    from transform import transform
    df = load_csv("walmart_customer_purchases.csv")
    cleaned, report = transform(df)
    path = write_parquet(cleaned, "walmart_customer_purchases_clean.parquet")
    print("Wrote:", path)


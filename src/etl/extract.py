# src/etl/extract.py
from pathlib import Path
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

def load_csv(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Raw file not found: {path}")
    # use low_memory=False to avoid mixed type warnings with large CSVs
    df = pd.read_csv(path, low_memory=False)
    return df

# quick command-line test
if __name__ == "__main__":
    df = load_csv("walmart_customer_purchases.csv")
    print("Loaded rows:", len(df))
    print("Columns:", df.columns.tolist())
    print(df.head(3).to_dict(orient="records"))

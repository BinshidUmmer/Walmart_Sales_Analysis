from pathlib import Path
import pandas as pd
import sqlite3
import uuid

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "walmart_sales.db"
SCHEMA_PATH = Path(__file__).resolve().parents[2]/ "src" / "sql" / "views.sql"  # 👈 path to your SQL file


def write_parquet(df: pd.DataFrame, filename: str):
    """Write cleaned dataframe to Parquet."""
    out = PROCESSED_DIR / filename
    df.to_parquet(out, index=False)
    return out


def load_to_sqlite(df: pd.DataFrame):
    """Load cleaned dataframe into SQLite with normalized schema."""
    conn = sqlite3.connect(DB_PATH)

    # --- Load schema from external .sql file ---
    if SCHEMA_PATH.exists():
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
    else:
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    # --- Generate product IDs for each (category, product_name) ---
    product_dim = (
        df[["category", "product_name"]]
        .drop_duplicates()
        .assign(product_id=[str(uuid.uuid4()) for _ in range(len(df[["category", "product_name"]].drop_duplicates()))])
    )

    # --- Generate transaction IDs ---
    df = df.copy()
    df["transaction_id"] = [str(uuid.uuid4()) for _ in range(len(df))]

    # --- Merge to attach product_id ---
    df = df.merge(product_dim, on=["category", "product_name"], how="left")

    # --- Write dimension tables ---
    customer_dim = df[["customer_id", "age", "gender", "city"]].drop_duplicates()
    product_dim.to_sql("dim_product", conn, if_exists="replace", index=False)
    customer_dim.to_sql("dim_customer", conn, if_exists="replace", index=False)

    # --- Write fact table ---
    fact_cols = [
        "transaction_id", "customer_id", "product_id", "purchase_date",
        "purchase_amount", "discount_applied", "payment_method", "rating", "repeat_customer"
    ]
    df[fact_cols].to_sql("fact_sales", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    print(f"✅ Data successfully loaded into SQLite at {DB_PATH}")


if __name__ == "__main__":
    from extract import load_csv
    from transform import transform

    df = load_csv("walmart_customer_purchases.csv")
    cleaned, report = transform(df)

    parquet_path = write_parquet(cleaned, "walmart_customer_purchases_clean.parquet")
    print(f"Wrote Parquet: {parquet_path}")

    load_to_sqlite(cleaned)
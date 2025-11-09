# src/etl/run.py
from extract import load_csv
from transform import transform
from load import write_parquet
import json

def run_pipeline(raw_filename: str, out_filename: str):
    df = load_csv(raw_filename)
    cleaned, report = transform(df)
    out_path = write_parquet(cleaned, out_filename)
    # save small report
    with open("data/processed/etl_report.json", "w") as fh:
        json.dump(report, fh, indent=2)
    print("Done. Out:", out_path)
    print("Report:", report)

if __name__ == "__main__":
    run_pipeline("walmart_customer_purchases.csv", "walmart_customer_purchases_clean.parquet")

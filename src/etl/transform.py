# src/etl/transform.py
import re
import pandas as pd
from dateutil import parser
from typing import Tuple

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

def is_valid_email(e):
    if pd.isna(e):
        return False
    return bool(EMAIL_RE.match(str(e).strip()))

def parse_date_safe(val):
    if pd.isna(val):
        return pd.NaT
    try:
        return parser.parse(str(val), dayfirst=False)
    except Exception:
        return pd.NaT

def transform(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Return transformed dataframe and a small report dict."""
    report = {}
    initial = len(df)
    report['initial_rows'] = initial

    # Standardize column names (lowercase)
    df = df.rename(columns=str.strip).rename(columns=str.lower)

    # Example expected columns: customer_id, transaction_id, purchase_date, purchase_amount, email, product_id, rating
    # 1. Drop exact duplicate rows
    df = df.drop_duplicates()
    report['after_drop_duplicates'] = len(df)

    # 2. Parse numeric columns
    if 'purchase_amount' in df.columns:
        df['purchase_amount'] = pd.to_numeric(df['purchase_amount'], errors='coerce')

    # 3. Ensure positive amounts: remove or flag negatives
    if 'purchase_amount' in df.columns:
        before = len(df)
        df = df[df['purchase_amount'].notna() & (df['purchase_amount'] >= 0)]
        report['removed_negative_amounts'] = before - len(df)

    # 4. Parse dates
    if 'purchase_date' in df.columns:
        df['purchase_date_parsed'] = df['purchase_date'].apply(parse_date_safe)
        df['purchase_date_parsed'] = pd.to_datetime(df['purchase_date_parsed'])
        # optionally drop rows without a parsable date
        before = len(df)
        df = df[df['purchase_date_parsed'].notna()]
        report['removed_unparsable_dates'] = before - len(df)
        # replace original column if you want:
        df['purchase_date'] = df['purchase_date_parsed']
        df = df.drop(columns=['purchase_date_parsed'])

    # 5. Email validation
    if 'email' in df.columns:
        df['email_valid'] = df['email'].apply(is_valid_email)
        report['invalid_emails'] = int((~df['email_valid']).sum())
        # Optional: remove invalid email rows (or keep with flag)
        df = df[df['email_valid']]

    # 6. Dedupe by business key (e.g., transaction_id), keep latest if duplicate
    if 'transaction_id' in df.columns:
        before = len(df)
        # if purchase_date exists, keep the latest date
        if 'purchase_date' in df.columns:
            df = df.sort_values('purchase_date').drop_duplicates(subset=['transaction_id'], keep='last')
        else:
            df = df.drop_duplicates(subset=['transaction_id'])
        report['deduped_transactions'] = before - len(df)

    # 7. Compute repeat_customer flag based on customer transaction counts
    if 'customer_id' in df.columns:
        counts = df.groupby('customer_id').size()
        df['repeat_customer'] = df['customer_id'].map(lambda cid: 'yes' if counts.get(cid, 0) > 1 else 'no')

    # 8. Clean rating (if present) to integer 1-5, else NaN
    if 'rating' in df.columns:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').astype('Int64')
        df.loc[(df['rating'] < 1) | (df['rating'] > 5), 'rating'] = pd.NA

    # final row count
    report['final_rows'] = len(df)
    return df.reset_index(drop=True), report

# quick test
if __name__ == "__main__":
    import sys
    from extract import load_csv
    df = load_csv("walmart_customer_purchases.csv")
    cleaned, rep = transform(df)
    print(rep)
    print(cleaned.head())

CREATE TABLE IF NOT EXISTS dim_customer (
  customer_id TEXT PRIMARY KEY,
  age INTEGER,
  gender TEXT,
  city TEXT
);

CREATE TABLE IF NOT EXISTS dim_product (
  product_id TEXT PRIMARY KEY,
  category TEXT,
  product_name TEXT
);

CREATE TABLE IF NOT EXISTS fact_sales (
  transaction_id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  purchase_date TEXT,          
  purchase_amount NUMERIC,
  discount_applied TEXT,
  payment_method TEXT,
  rating INTEGER,
  repeat_customer TEXT, 
  FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
  FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
);

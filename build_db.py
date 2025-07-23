import pandas as pd
import sqlite3

# Load the CSVs
ad_sales = pd.read_csv("Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped).csv")
total_sales = pd.read_csv("Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped).csv")
eligibility = pd.read_csv("Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped).csv")

# Connect to SQLite
db_name = "ecommerce_data.db"
conn = sqlite3.connect(db_name)

# Write tables
ad_sales.to_sql("ad_sales_metrics", conn, if_exists="replace", index=False)
total_sales.to_sql("total_sales_metrics", conn, if_exists="replace", index=False)
eligibility.to_sql("eligibility_table", conn, if_exists="replace", index=False)

print(f"✅ Database '{db_name}' built successfully with 3 tables:")
print(" - ad_sales_metrics")
print(" - total_sales_metrics")
print(" - eligibility_table")

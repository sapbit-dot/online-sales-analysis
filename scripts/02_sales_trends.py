import pandas as pd
import os

# Load cleaned dataset
df: pd.DataFrame = pd.read_csv("../data/full_olist_data_clean.csv")
print("Dataset loaded:", df.shape)

# 1. Monthly Sales Trends
df["purchase_year_month"] = pd.to_datetime(df["order_purchase_timestamp"]).dt.to_period("M").astype(str)

monthly_sales = (
    df.groupby("purchase_year_month")["price"]
    .sum()
    .reset_index()
    .rename(columns={"price": "monthly_revenue"})
)

print("Monthly sales trend (first rows):")
print(monthly_sales.head())

# 2. Monthly Order Count
monthly_orders = (
    df.groupby("purchase_year_month")["order_id"]
    .nunique()
    .reset_index()
    .rename(columns={"order_id": "orders_count"})
)

print("Monthly order count:")
print(monthly_orders.head())

# 3. Revenue per Product Category
category_revenue = (
    df.groupby("product_category_name")["price"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={"price": "total_revenue"})
)

print("Top categories by revenue:")
print(category_revenue.head())

# 4. Customer Order Analysis (replacing top products)
order_stats = (
    df.groupby("order_id")
    .agg(
        order_value=("price", "sum"),
        num_items=("order_item_id", "count"),
        num_categories=("product_category_name", pd.Series.nunique)
    )
    .reset_index()
)

print("Order stats (first rows):")
print(order_stats.head())

# 5. Sellers Performance
top_sellers = (
    df.groupby("seller_id")["price"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={"price": "seller_revenue"})
)

print("Top sellers:")
print(top_sellers.head())

# 6. Combine results and save outputs
output_dir = "../data/analysis_results/"
os.makedirs(output_dir, exist_ok=True)

monthly_sales.to_csv(output_dir + "monthly_sales.csv", index=False)
monthly_orders.to_csv(output_dir + "monthly_orders.csv", index=False)
category_revenue.to_csv(output_dir + "category_revenue.csv", index=False)
order_stats.to_csv(output_dir + "order_stats.csv", index=False)  # <-- new table
top_sellers.to_csv(output_dir + "top_sellers.csv", index=False)

print("Analysis files saved in:", output_dir)

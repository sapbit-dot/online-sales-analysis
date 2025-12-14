import os
import pandas as pd

# Detect project folder correctly
project_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(project_dir, "../data")
cleaned_dir = os.path.join(data_dir, "cleaned")

os.makedirs(cleaned_dir, exist_ok=True)

# File path for raw dataset (where download script placed it)
raw_file = os.path.join(data_dir, "raw", "full_olist_data.csv")

print("Loading:", raw_file)
df = pd.read_csv(raw_file)

print("Initial shape:", df.shape)

# Remove duplicates
df = df.drop_duplicates()
print("After removing duplicates:", df.shape)

# Convert purchase_date
if "order_purchase_timestamp" in df.columns:
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["purchase_year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)

# Handle missing values
df = df.dropna(subset=["order_id", "customer_id", "product_id", "price"])

text_cols = df.select_dtypes(include="object").columns
df[text_cols] = df[text_cols].fillna("Unknown")

num_cols = df.select_dtypes(include=["int64", "float64"]).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())

# Save cleaned dataset
output_path = os.path.join(cleaned_dir, "full_olist_data.csv")
print("Saving cleaned dataset to:", output_path)

df.to_csv(output_path, index=False)

print("Cleaning complete. Final shape:", df.shape)

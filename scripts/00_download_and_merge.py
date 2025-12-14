import os
import pandas as pd
import kagglehub

# Paths
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(project_dir, "data")
raw_dir = os.path.join(data_dir, "raw")

os.makedirs(raw_dir, exist_ok=True)

print("Project directory:", project_dir)
print("Raw directory:", raw_dir)

# Download dataset
print("Downloading dataset from Kaggle...")
path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

print("Dataset downloaded to:", path)

# Copy downloaded files into data/raw if needed
# KaggleHub puts files in a versioned directory, so we copy them manually
for file in os.listdir(path):
    src = os.path.join(path, file)
    dst = os.path.join(raw_dir, file)
    if os.path.isfile(src):
        print("Copying:", file)
        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
            fdst.write(fsrc.read())

# Load source files
orders = pd.read_csv(os.path.join(raw_dir, "olist_orders_dataset.csv"))
items = pd.read_csv(os.path.join(raw_dir, "olist_order_items_dataset.csv"))
products = pd.read_csv(os.path.join(raw_dir, "olist_products_dataset.csv"))
payments = pd.read_csv(os.path.join(raw_dir, "olist_order_payments_dataset.csv"))
reviews = pd.read_csv(os.path.join(raw_dir, "olist_order_reviews_dataset.csv"))
customers = pd.read_csv(os.path.join(raw_dir, "olist_customers_dataset.csv"))
sellers = pd.read_csv(os.path.join(raw_dir, "olist_sellers_dataset.csv"))

# Merge
df = orders.merge(items, on="order_id", how="left")
df = df.merge(products, on="product_id", how="left")
df = df.merge(payments, on="order_id", how="left")
df = df.merge(reviews, on="order_id", how="left")
df = df.merge(customers, on="customer_id", how="left")
df = df.merge(sellers, on="seller_id", how="left")

# Save merged file
output_path = os.path.join(raw_dir, "full_olist_data.csv")
df.to_csv(output_path, index=False)

print("\nMerged dataset saved to:", output_path)
print("Final shape:", df.shape)

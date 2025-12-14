import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Load cleaned dataset
df = pd.read_csv("../data/cleaned/full_olist_data.csv")
df['order_approved_at'] = pd.to_datetime(df['order_approved_at'], errors='coerce')
df = df.dropna(subset=['order_approved_at'])

# Create Year-Month column
df['purchase_year_month'] = df['order_approved_at'].dt.to_period('M').astype(str)

# -------------------------------
# Top 5 categories by revenue
category_revenue = (
    df.groupby('product_category_name')['price']
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)
category_translation = {
    "beleza_saude": "Beauty & Health",
    "relogios_presentes": "Watches & Gifts",
    "cama_mesa_banho": "Home & Bath",
    "esporte_lazer": "Sports & Leisure",
    "informatica_acessorios": "Computers & Accessories"
}
category_revenue['label'] = category_revenue['product_category_name'].map(category_translation)

# Top 5 sellers by revenue and items sold
seller_revenue = (
    df.groupby('seller_id')
    .agg({'price':'sum', 'order_item_id':'count'})
    .rename(columns={'order_item_id':'total_items_sold'})
    .sort_values('price', ascending=False)
    .head(5)
    .reset_index()
)

# -------------------------------
# Create 2x2 dashboard
fig, axes = plt.subplots(2,2, figsize=(16,12))
plt.subplots_adjust(hspace=0.4, wspace=0.3)

# 1. Top Left – Revenue over time (Line plot) – עד חודש 2018-08
monthly_revenue = (
    df.groupby('purchase_year_month')['price']
    .sum()
    .reset_index()
)
# Keep only months <= Aug 2018
monthly_revenue = monthly_revenue[monthly_revenue['purchase_year_month'] <= '2018-08']

axes[0,0].plot(monthly_revenue['purchase_year_month'], monthly_revenue['price'], marker='o', color='blue')
axes[0,0].set_title("Monthly Revenue")
axes[0,0].set_xlabel("Year-Month")
axes[0,0].set_ylabel("Revenue")
axes[0,0].tick_params(axis='x', rotation=90)
axes[0,0].ticklabel_format(style='plain', axis='y')

# 2. Top Right – Top Categories (Bar plot)
sns.barplot(data=category_revenue, x="label", y="price", palette="viridis", ax=axes[0,1])
axes[0,1].set_title("Top 5 Categories by Revenue")
axes[0,1].set_xlabel("Category")
axes[0,1].set_ylabel("Revenue")
axes[0,1].tick_params(axis='x', rotation=45)
axes[0,1].ticklabel_format(style='plain', axis='y')

# 3. Bottom Left – Orders Scatter Plot
order_stats = pd.read_csv("../data/analysis_results/order_stats.csv")

# Remove possible duplicate orders
order_stats = order_stats.drop_duplicates(subset=['order_id'])

scatter = axes[1,0].scatter(
    order_stats["num_items"],
    order_stats["order_value"],
    c=order_stats["num_categories"],
    cmap="viridis",
    alpha=0.35,
)
axes[1,0].set_title("Orders Scatter Plot\nItems vs Order Value (color = categories)")
axes[1,0].set_xlabel("Number of Items in Order")
axes[1,0].set_ylabel("Order Value (BRL)")
axes[1,0].ticklabel_format(style='plain', axis='y')

cbar = fig.colorbar(scatter, ax=axes[1,0])
cbar.set_label("Number of Categories")

# 4. Bottom Right – Top Sellers Bubble Plot
top_seller_ids = seller_revenue['seller_id'].tolist()
seller_category_revenue = (
    df[df['seller_id'].isin(top_seller_ids)]
    .groupby(['seller_id', 'product_category_name'])
    .agg({'price':'sum','order_item_id':'sum'})
    .reset_index()
)

# Category with max revenue per seller
seller_top_category = seller_category_revenue.loc[
    seller_category_revenue.groupby('seller_id')['price'].idxmax()
][['seller_id','product_category_name']]

# Translate categories
category_translation.update({
    "pcs": "Electronics/PCs",
    "moveis_escritorio": "Office Furniture"
})
seller_top_category['category_eng'] = seller_top_category['product_category_name'].map(category_translation)
seller_top_category['category_eng'] = seller_top_category['category_eng'].fillna(seller_top_category['product_category_name'])

# Merge with top sellers
top_sellers_plot = seller_revenue.merge(seller_top_category, on='seller_id', how='left')

# Shorten seller names
top_sellers_plot['seller_short'] = top_sellers_plot['seller_id'].apply(lambda x: x[:6]+"..." if len(x)>6 else x)

# Bubble plot
colors = sns.color_palette("tab10", n_colors=len(top_sellers_plot))
max_bubble_size = 2000
size_scale = max_bubble_size / top_sellers_plot['total_items_sold'].max()

for i, row in top_sellers_plot.iterrows():
    axes[1,1].scatter(
        x=row['seller_short'],
        y=row['price'],
        s=row['total_items_sold'] * size_scale,
        color=colors[i],
        alpha=0.7
    )
    axes[1,1].text(
        row['seller_short'],
        row['price'] + (row['total_items_sold'] * size_scale * 0.005),
        row['category_eng'],
        ha='center',
        va='bottom',
        fontsize=8,
        weight='bold'
    )

axes[1,1].set_title("Top Sellers Bubble Plot (size = items sold & top category)")
axes[1,1].set_xlabel("Seller ID")
axes[1,1].set_ylabel("Revenue")
axes[1,1].tick_params(axis='x', rotation=45)
axes[1,1].ticklabel_format(style='plain', axis='y')
if axes[1,1].get_legend() is not None:
    axes[1,1].legend_.remove()

# Supertitle
fig.suptitle("E-Commerce Sales Dashboard", fontsize=18)

# Save dashboard
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("../reports/dashboard_2x2_final.png")
plt.show()

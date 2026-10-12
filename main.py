import pandas as pd
import os
from pathlib import Path

# --- CONFIG ---
INPUT_FILE = "data/restaurant-orders.csv"
OUTPUT_DIR = "data/clean"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_etl():
    print("=== HORECA ETL START ===")

    # 1. EXTRACT
    df = pd.read_csv(INPUT_FILE)
    print(f"[Extract] Raw rows: {len(df)} | Cols: {list(df.columns)}")

    df.rename(columns={
        'Order ID': 'order_id',
        'Customer Name': 'customer_name',
        'Food Item': 'food_item',
        'Category': 'category',
        'Quantity': 'quantity',
        'Price': 'price',
        'Payment Method': 'payment_method',
        'Order Time': 'order_time'
    }, inplace=True)

    # 2. TRANSFORM
    initial_len = len(df)

    # 2.1 Дедупликация
    df = df.drop_duplicates(subset=['order_id', 'food_item', 'order_time'])
    print(f"[Dedup] Removed {initial_len - len(df)} duplicates ({(initial_len - len(df))/initial_len*100:.1f}%)")

    # 2.2 Обработка пропусков
    df['customer_name'] = df['customer_name'].fillna('Walk-in Customer')
    df['category'] = df['category'].fillna('Unknown')
    df['quantity'] = df['quantity'].fillna(1)
    df['payment_method'] = df['payment_method'].fillna('Cash')

    df['price'] = df.groupby('food_item')['price'].transform(lambda x: x.fillna(x.median()))
    df['price'] = df['price'].fillna(df['price'].median())

    df = df.dropna(subset=['order_time', 'food_item'])

    # 2.3 Типы данных
    df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['order_time'])
    df['quantity'] = df['quantity'].astype(int)
    df['price'] = df['price'].astype(float)
    df['order_id'] = df['order_id'].astype(str)

    # 2.4 Бизнес-метрики
    df['total_amount'] = df['quantity'] * df['price']
    df['order_hour'] = df['order_time'].dt.hour
    df['order_date'] = df['order_time'].dt.date
    df['weekday'] = df['order_time'].dt.day_name()
    df['weekday_num'] = df['order_time'].dt.weekday
    df['is_weekend'] = df['weekday_num'] >= 5
    df['month'] = df['order_time'].dt.to_period('M').astype(str)

    # 2.5 Флаг аномалий
    df['is_large_order'] = df['quantity'] > 10

    # 3. BUILD STAR SCHEMA из одного файла
    # dim_menu
    dim_menu = df[['food_item', 'category', 'price']].sort_values('food_item').drop_duplicates(subset=['food_item']).copy()
    dim_menu['item_id'] = range(1, len(dim_menu) + 1)
    # Т.к. cost нет в исходнике, эмулируем для портфолио 32%
    dim_menu['cost'] = (dim_menu['price'] * 0.32).round(2)
    dim_menu['margin_pct'] = ((dim_menu['price'] - dim_menu['cost']) / dim_menu['price'] * 100).round(2)
    dim_menu = dim_menu[['item_id', 'food_item', 'category', 'price', 'cost', 'margin_pct']]

    # dim_customer
    dim_customer = df[['customer_name']].drop_duplicates().copy()
    dim_customer['customer_id'] = range(1, len(dim_customer) + 1)
    dim_customer = dim_customer[['customer_id', 'customer_name']]

    # fact_orders
    fact_orders = df.merge(dim_menu[['item_id', 'food_item']], on='food_item', how='left')
    fact_orders = fact_orders.merge(dim_customer, on='customer_name', how='left')

    fact_orders = fact_orders[[
        'order_id', 'item_id', 'customer_id', 'quantity',
        'price', 'total_amount', 'payment_method',
        'order_time', 'order_date', 'order_hour', 'weekday', 'is_weekend', 'month', 'is_large_order'
    ]]

    # 4. LOAD TO CSV
    fact_orders.to_csv(f"{OUTPUT_DIR}/fact_orders.csv", index=False)
    dim_menu.to_csv(f"{OUTPUT_DIR}/dim_menu.csv", index=False)
    dim_customer.to_csv(f"{OUTPUT_DIR}/dim_customer.csv", index=False)

    # Также сохраняем один полный clean файл для Tableau Public
    df.to_csv(f"{OUTPUT_DIR}/clean_restaurant_orders.csv", index=False)

    print(f"\n=== ETL DONE ===")
    print(f"fact_orders: {len(fact_orders)} rows -> {OUTPUT_DIR}/fact_orders.csv")
    print(f"dim_menu: {len(dim_menu)} items -> {OUTPUT_DIR}/dim_menu.csv")
    print(f"dim_customer: {len(dim_customer)} customers -> {OUTPUT_DIR}/dim_customer.csv")
    print(f"Revenue total: {fact_orders['total_amount'].sum():,.2f}")
    print(f"Date range: {fact_orders['order_time'].min()} to {fact_orders['order_time'].max()}")
    print("\nTop 5 dishes:")
    print(fact_orders.merge(dim_menu, on='item_id').groupby('food_item')['total_amount'].sum().sort_values(ascending=False).head())

if __name__ == "__main__":
    run_etl()
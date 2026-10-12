import pandas as pd
import os

# Extract - твой единственный файл
orders = pd.read_csv('data/restaurant-orders.csv')
print(f"Raw: {len(orders)} rows")

# Стандартизируем названия колонок под код
orders.columns = [c.strip().lower().replace(' ', '_') for c in orders.columns]
# теперь: order_id, customer_name, food_item, category, quantity, price, payment_method, order_time

# Transform
# 1. Dedup - реальная проблема в общепите
orders = orders.drop_duplicates(subset=['order_id', 'food_item'])

# 2. Null handling
orders['quantity'] = orders['quantity'].fillna(1)
orders['price'] = orders['price'].fillna(orders['price'].median())
orders = orders.dropna(subset=['order_time', 'food_item'])

# 3. Очистка типов
orders['order_time'] = pd.to_datetime(orders['order_time'], errors='coerce')
orders = orders.dropna(subset=['order_time'])
orders['quantity'] = orders['quantity'].astype(int)

# 4. Бизнес-логика - то, за что платят в NurTelecom
orders['total_amount'] = orders['quantity'] * orders['price']
orders['order_hour'] = orders['order_time'].dt.hour
orders['weekday'] = orders['order_time'].dt.day_name()
orders['is_weekend'] = orders['order_time'].dt.weekday >= 5

# 5. Создаем справочники из одного файла - это покажет уровень
dim_menu = orders[['food_item', 'category', 'price']].drop_duplicates(subset=['food_item']).copy()
dim_menu['item_id'] = range(1, len(dim_menu)+1)
# эмулируем себестоимость 30% для расчета food cost, напиши об этом в README честно
dim_menu['cost'] = dim_menu['price'] * 0.32
dim_menu['food_cost_pct'] = dim_menu['cost'] / dim_menu['price'] * 100

dim_customer = orders[['customer_name']].drop_duplicates().copy()
dim_customer['customer_id'] = range(1, len(dim_customer)+1)

# 6. Факт-таблица
fact_orders = orders.merge(dim_menu[['item_id', 'food_item']], on='food_item', how='left')
fact_orders = fact_orders.merge(dim_customer, on='customer_name', how='left')
fact_orders = fact_orders[['order_id', 'item_id', 'customer_id', 'quantity', 'price', 'total_amount', 'payment_method', 'order_time', 'order_hour', 'weekday']]

# Save for Postgres
os.makedirs('data/clean', exist_ok=True)
fact_orders.to_csv('data/clean/fact_orders.csv', index=False)
dim_menu.to_csv('data/clean/dim_menu.csv', index=False)
dim_customer.to_csv('data/clean/dim_customer.csv', index=False)

print(f"Clean fact: {len(fact_orders)}")
print(f"Menu items: {len(dim_menu)}")
print(f"Customers: {len(dim_customer)}")
print(fact_orders['total_amount'].describe())
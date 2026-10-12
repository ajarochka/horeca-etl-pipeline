import pandas as pd
from sqlalchemy import create_engine, text
import os
from pathlib import Path

# --- CONFIG ---
DB_USER = "admin"
DB_PASS = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "horeca"

CLEAN_DIR = Path("data/clean")

# Подключение
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
print(f"Connecting to {DB_NAME}...")

def load():
    # Читаем файлы
    fact = pd.read_csv(CLEAN_DIR / "fact_orders.csv")
    dim_menu = pd.read_csv(CLEAN_DIR / "dim_menu.csv")
    dim_customer = pd.read_csv(CLEAN_DIR / "dim_customer.csv")

    # Фикс типов для Postgres
    fact['order_time'] = pd.to_datetime(fact['order_time'])
    fact['order_date'] = pd.to_datetime(fact['order_date'])

    with engine.begin() as conn:
        # 1. Чистим если уже грузили
        conn.execute(text("DROP TABLE IF EXISTS fact_orders CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS dim_menu CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS dim_customer CASCADE;"))

        # 2. Создаем таблицы с правильными типами и индексами
        print("Creating tables...")
        conn.execute(text("""
            CREATE TABLE dim_menu (
                item_id INT PRIMARY KEY,
                food_item VARCHAR(255) UNIQUE NOT NULL,
                category VARCHAR(100),
                price NUMERIC(10,2),
                cost NUMERIC(10,2),
                margin_pct NUMERIC(5,2)
            );
        """))
        conn.execute(text("""
            CREATE TABLE dim_customer (
                customer_id INT PRIMARY KEY,
                customer_name VARCHAR(255)
            );
        """))
        conn.execute(text("""
            CREATE TABLE fact_orders (
                order_id VARCHAR(100),
                item_id INT REFERENCES dim_menu(item_id),
                customer_id INT REFERENCES dim_customer(customer_id),
                quantity INT,
                price NUMERIC(10,2),
                total_amount NUMERIC(10,2),
                payment_method VARCHAR(50),
                order_time TIMESTAMP,
                order_date DATE,
                order_hour INT,
                weekday VARCHAR(20),
                is_weekend BOOLEAN,
                month VARCHAR(10),
                is_large_order BOOLEAN
            );
        """))

    # 3. Загрузка
    print(f"Loading dim_menu ({len(dim_menu)})...")
    dim_menu.to_sql('dim_menu', engine, if_exists='append', index=False)

    print(f"Loading dim_customer ({len(dim_customer)})...")
    dim_customer.to_sql('dim_customer', engine, if_exists='append', index=False)

    print(f"Loading fact_orders ({len(fact)})... может занять 10-20 сек")

    fact.to_sql('fact_orders', engine, if_exists='append', index=False, chunksize=10000)

    # 4. Создаем индексы после загрузки
    with engine.begin() as conn:
        print("Creating indexes...")
        conn.execute(text("CREATE INDEX idx_fact_time ON fact_orders(order_time);"))
        conn.execute(text("CREATE INDEX idx_fact_item ON fact_orders(item_id);"))
        conn.execute(text("CREATE INDEX idx_fact_hour ON fact_orders(order_hour);"))
        conn.execute(text("CREATE INDEX idx_menu_category ON dim_menu(category);"))

    # 5. Проверка
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) as cnt, SUM(total_amount) as rev FROM fact_orders;")).fetchone()
        print(f"\n=== LOAD DONE ===")
        print(f"Rows in fact_orders: {result[0]}")
        print(f"Total Revenue: {result[1]:,.2f}")

        print("\nTop categories check:")
        check = pd.read_sql("SELECT m.category, SUM(f.total_amount) as rev FROM fact_orders f JOIN dim_menu m ON f.item_id=m.item_id GROUP BY 1 ORDER BY 2 DESC LIMIT 5", conn)
        print(check)

if __name__ == "__main__":
    load()
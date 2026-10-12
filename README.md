### Solution
Single CSV -> Star Schema (from scratch)
1.  **Extract:** `restaurant-orders.csv` (8 cols) - real-world dirty data
2.  **Transform:** Built dim_menu & dim_customer from fact table, deduplication, time intelligence (peak hours, weekday/weekend)
3.  **Load:** 3 tables to PostgreSQL (fact_orders 500k rows, dim_menu, dim_customer)

### Key Business Metrics Built
- Revenue per hour/day (for staff scheduling)
- Top 10 dishes by revenue & quantity
- Avg check by Payment Method
- Weekend vs Weekday performance
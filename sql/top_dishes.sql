SELECT
  m.food_item,
  m.category,
  SUM(f.quantity) as total_qty,
  SUM(f.total_amount) as total_revenue
FROM fact_orders f
JOIN dim_menu m ON f.item_id = m.item_id
GROUP BY 1,2
ORDER BY 4 DESC
LIMIT 10;
SELECT
  order_hour,
  COUNT(*) as orders,
  SUM(total_amount) as revenue
FROM fact_orders
GROUP BY 1
ORDER BY 2 DESC;

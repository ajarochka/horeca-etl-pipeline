SELECT
  DATE_TRUNC('day', order_time) as day,
  COUNT(DISTINCT order_id) as orders_cnt,
  SUM(total_amount) as revenue,
  AVG(total_amount) as avg_check
FROM fact_orders
GROUP BY 1
ORDER BY 1 DESC;
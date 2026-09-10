-- Core analytical queries
SELECT SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi;

SELECT COUNT(DISTINCT order_id) AS orders FROM orders;
SELECT COUNT(DISTINCT customer_id) AS customers FROM orders;

SELECT p.category, SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category ORDER BY revenue DESC;

SELECT customer_id, COUNT(DISTINCT order_id) AS frequency
FROM orders GROUP BY customer_id;

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id = 1001;

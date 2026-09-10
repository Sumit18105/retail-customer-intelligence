from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path(__file__).resolve().parent / 'database' / 'retail.db'

def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.execute('PRAGMA foreign_keys = ON')
    return con

def query(sql, params=()):
    with get_connection() as con:
        return pd.read_sql_query(sql, con, params=params)

def kpis(start=None, end=None):
    where = 'WHERE DATE(o.order_date) BETWEEN DATE(?) AND DATE(?)' if start and end else ''
    params = (start, end) if start and end else ()
    return query(f'''SELECT COALESCE(SUM(oi.quantity*oi.unit_price),0) revenue,
      COUNT(DISTINCT o.order_id) orders, COUNT(DISTINCT o.customer_id) customers,
      CASE WHEN COUNT(DISTINCT o.order_id)>0 THEN SUM(oi.quantity*oi.unit_price)*1.0/COUNT(DISTINCT o.order_id) ELSE 0 END aov
      FROM orders o JOIN order_items oi ON o.order_id=oi.order_id {where}''', params).iloc[0].to_dict()

def repeat_rate(start=None,end=None):
    where = 'WHERE DATE(order_date) BETWEEN DATE(?) AND DATE(?)' if start and end else ''
    params=(start,end) if start and end else ()
    q=f'''WITH f AS (SELECT customer_id, COUNT(DISTINCT order_id) n FROM orders {where} GROUP BY customer_id)
          SELECT COALESCE(SUM(CASE WHEN n>1 THEN 1 ELSE 0 END)*100.0/NULLIF(COUNT(*),0),0) repeat_rate FROM f'''
    return float(query(q,params).iloc[0,0])

def monthly_revenue(start=None,end=None):
    where = 'WHERE DATE(o.order_date) BETWEEN DATE(?) AND DATE(?)' if start and end else ''
    params=(start,end) if start and end else ()
    return query(f'''SELECT strftime('%Y-%m',o.order_date) month, SUM(oi.quantity*oi.unit_price) revenue
                     FROM orders o JOIN order_items oi ON o.order_id=oi.order_id {where}
                     GROUP BY month ORDER BY month''',params)

def category_revenue(start=None,end=None):
    where = 'WHERE DATE(o.order_date) BETWEEN DATE(?) AND DATE(?)' if start and end else ''
    params=(start,end) if start and end else ()
    return query(f'''SELECT p.category, SUM(oi.quantity*oi.unit_price) revenue
                     FROM order_items oi JOIN products p ON oi.product_id=p.product_id
                     JOIN orders o ON o.order_id=oi.order_id {where}
                     GROUP BY p.category ORDER BY revenue DESC''',params)

def customer_rfm(start=None,end=None):
    where = 'WHERE DATE(o.order_date) BETWEEN DATE(?) AND DATE(?)' if start and end else ''
    params=(start,end) if start and end else ()
    q=f'''WITH base AS (
      SELECT o.customer_id, MAX(DATE(o.order_date)) last_order,
             COUNT(DISTINCT o.order_id) frequency,
             SUM(oi.quantity*oi.unit_price) monetary
      FROM orders o JOIN order_items oi ON o.order_id=oi.order_id {where}
      GROUP BY o.customer_id),
    scored AS (
      SELECT *,
        CAST(julianday((SELECT MAX(DATE(order_date)) FROM orders)) - julianday(last_order) AS INTEGER) recency,
        NTILE(5) OVER (ORDER BY (julianday((SELECT MAX(DATE(order_date)) FROM orders))-julianday(last_order)) DESC) r_score,
        NTILE(5) OVER (ORDER BY frequency) f_score,
        NTILE(5) OVER (ORDER BY monetary) m_score
      FROM base)
    SELECT customer_id, recency, frequency, ROUND(monetary,2) monetary, r_score, f_score, m_score,
      CASE
        WHEN r_score>=4 AND f_score>=4 AND m_score>=4 THEN 'Champions'
        WHEN f_score>=4 AND r_score>=3 THEN 'Loyal Customers'
        WHEN r_score>=4 AND f_score<=2 THEN 'New Customers'
        WHEN r_score>=3 AND f_score>=2 THEN 'Potential Loyalists'
        WHEN r_score<=2 AND (m_score>=4 OR f_score>=4) THEN 'At Risk'
        ELSE 'Lost Customers' END segment
    FROM scored ORDER BY monetary DESC'''
    return query(q,params)

def segment_summary(rfm):
    return rfm.groupby('segment',as_index=False).agg(customers=('customer_id','count'),revenue=('monetary','sum')).sort_values('revenue',ascending=False)

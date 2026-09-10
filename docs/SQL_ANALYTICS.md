# SQL & Analytics Specification

Core metrics: revenue = SUM(quantity × unit_price); orders = COUNT(DISTINCT order_id); customers = COUNT(DISTINCT customer_id); AOV = revenue/orders; repeat rate = customers with >1 order / total customers.

RFM: recency, frequency, monetary. Scores use quintiles and map to Champions, Loyal Customers, New Customers, Potential Loyalists, At Risk and Lost Customers.

Validation: reconcile revenue to a direct SQL total, customer counts to distinct IDs, segment counts to total segmented customers, and manually inspect sample customers.

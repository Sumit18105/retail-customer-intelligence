# Database Schema

```text
customers (1) ──< orders (1) ──< order_items >── (1) products
```

- `customers(customer_id PK, customer_name, email, city, signup_date)`
- `products(product_id PK, product_name, category, unit_price)`
- `orders(order_id PK, customer_id FK, order_date, order_status)`
- `order_items(order_item_id PK, order_id FK, product_id FK, quantity, unit_price)`

Indexes: `orders(customer_id)`, `orders(order_date)`, `order_items(order_id)`, `order_items(product_id)`.

Integrity: primary keys unique/non-null; foreign keys valid; quantity positive for completed purchases; price non-negative; dates parseable.

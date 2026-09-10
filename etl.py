from pathlib import Path
import sqlite3
import pandas as pd

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / 'data'
DB_PATH = BASE / 'database' / 'retail.db'

REQUIRED = ['order_id','product_id','product_name','quantity','order_date','unit_price','customer_id','city','category']

def clean_transactions(path: str | Path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    before = len(df)
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    numeric_cols = ['quantity','unit_price','customer_id']
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    invalid = (
        df['order_id'].isna() | df['product_id'].isna() | df['customer_id'].isna() |
        df['order_date'].isna() | df['quantity'].isna() | df['unit_price'].isna() |
        (df['quantity'] <= 0) | (df['unit_price'] < 0)
    )
    invalid_count = int(invalid.sum())
    df = df.loc[~invalid].copy()
    df['customer_id'] = df['customer_id'].astype(int)
    df['quantity'] = df['quantity'].astype(int)
    df['revenue'] = df['quantity'] * df['unit_price']
    quality = {
        'rows_processed': before,
        'duplicates_found': duplicate_count,
        'invalid_records': invalid_count,
        'valid_records': len(df),
        'missing_values_remaining': int(df[REQUIRED].isna().sum().sum()),
    }
    return df, quality

def build_database(df: pd.DataFrame, db_path: str | Path = DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.execute('PRAGMA foreign_keys = ON')
    con.executescript('''
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_name TEXT,
        email TEXT,
        city TEXT,
        signup_date DATE
    );
    CREATE TABLE products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_price REAL NOT NULL
    );
    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date DATETIME NOT NULL,
        order_status TEXT NOT NULL DEFAULT 'completed',
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    );
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(order_id),
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    );
    ''')
    customers = df[['customer_id','city']].drop_duplicates('customer_id').copy()
    customers['customer_name'] = customers['customer_id'].map(lambda x: f'Customer {x}')
    customers['email'] = customers['customer_id'].map(lambda x: f'customer{x}@example.com')
    customers['signup_date'] = pd.to_datetime(df.groupby('customer_id')['order_date'].min().reindex(customers['customer_id']).values).date
    products = df[['product_id','product_name','category','unit_price']].drop_duplicates('product_id').copy()
    orders = df[['order_id','customer_id','order_date']].drop_duplicates('order_id').copy()
    orders['order_status'] = 'completed'
    items = df[['order_id','product_id','quantity','unit_price']].copy()
    customers.to_sql('customers', con, if_exists='append', index=False)
    products.to_sql('products', con, if_exists='append', index=False)
    orders.to_sql('orders', con, if_exists='append', index=False)
    items.to_sql('order_items', con, if_exists='append', index=False)
    con.executescript('''
      CREATE INDEX idx_orders_customer_id ON orders(customer_id);
      CREATE INDEX idx_orders_order_date ON orders(order_date);
      CREATE INDEX idx_order_items_order_id ON order_items(order_id);
      CREATE INDEX idx_order_items_product_id ON order_items(product_id);
    ''')
    con.commit(); con.close()

if __name__ == '__main__':
    source = DATA_DIR / 'demo_retail_data.csv'
    df, quality = clean_transactions(source)
    build_database(df)
    print(quality)

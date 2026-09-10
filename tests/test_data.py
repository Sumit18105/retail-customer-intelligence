import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analytics import get_connection, kpis, customer_rfm

def test_database_tables():
    with get_connection() as con:
        tables={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {'customers','products','orders','order_items'} <= tables

def test_kpis_positive():
    kp=kpis(); assert kp['revenue']>0 and kp['orders']>0 and kp['customers']>0

def test_rfm_reconciles():
    r=customer_rfm(); assert len(r)>0; assert r['customer_id'].nunique()==len(r)
    assert set(r['segment']).issubset({'Champions','Loyal Customers','New Customers','Potential Loyalists','At Risk','Lost Customers'})

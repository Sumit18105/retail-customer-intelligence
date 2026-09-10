from pathlib import Path
import numpy as np, pandas as pd
rng=np.random.default_rng(42)
out=Path(__file__).resolve().parents[1]/'data/demo_retail_data.csv'
n_customers,n_products,n_orders=1500,120,12000
cities=['Delhi','Mumbai','Bengaluru','Pune','Hyderabad','Chennai','Kolkata','Jaipur']
cats=['Home Decor','Gifts','Stationery','Kitchen','Accessories','Seasonal']
products=pd.DataFrame({'product_id':[f'P{i:04d}' for i in range(1,n_products+1)],'product_name':[f'Product {i:04d}' for i in range(1,n_products+1)],'category':rng.choice(cats,n_products),'unit_price':np.round(rng.lognormal(2.7,.7,n_products),2)})
customers=pd.DataFrame({'customer_id':np.arange(10001,10001+n_customers),'city':rng.choice(cities,n_customers,p=[.2,.18,.16,.12,.11,.09,.08,.06])})
orders=pd.DataFrame({'order_id':[f'O{i:07d}' for i in range(1,n_orders+1)],'customer_id':rng.choice(customers.customer_id,n_orders),'order_date':pd.Timestamp('2025-01-01')+pd.to_timedelta(rng.integers(0,365,n_orders),unit='D')})
orders['order_date']=orders.order_date.dt.strftime('%Y-%m-%d')
items=[]
for _,o in orders.iterrows():
    for p in rng.choice(products.product_id,size=int(rng.integers(1,4)),replace=False):
        q=int(rng.integers(1,6)); price=float(products.loc[products.product_id.eq(p),'unit_price'].iloc[0]); items.append([o.order_id,p,f'Product {p[1:]}',q,o.order_date,price,o.customer_id,customers.loc[customers.customer_id.eq(o.customer_id),'city'].iloc[0],products.loc[products.product_id.eq(p),'category'].iloc[0]])
df=pd.DataFrame(items,columns=['order_id','product_id','product_name','quantity','order_date','unit_price','customer_id','city','category'])
out.parent.mkdir(exist_ok=True); df.to_csv(out,index=False); print(out,df.shape)

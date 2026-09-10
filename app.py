from pathlib import Path
import sqlite3, time
import pandas as pd
import plotly.express as px
import streamlit as st
from analytics import kpis, repeat_rate, monthly_revenue, category_revenue, customer_rfm, segment_summary, get_connection

st.set_page_config(page_title='Retail Customer Intelligence', page_icon='📊', layout='wide')
DB_PATH = Path(__file__).resolve().parent / 'database' / 'retail.db'

st.markdown('''<style>
.block-container{padding-top:1.5rem;max-width:1400px}.metric-card{border:1px solid #e5e7eb;border-radius:14px;padding:14px;background:#fff}
.insight{padding:16px;border-radius:12px;background:#f7f7f8;border-left:4px solid #111827}
</style>''', unsafe_allow_html=True)

if not DB_PATH.exists():
    st.error('Database not found. Run `python etl.py` first.')
    st.stop()

rfm_all = customer_rfm()
with get_connection() as con:
    bounds = pd.read_sql_query('SELECT MIN(DATE(order_date)) min_date, MAX(DATE(order_date)) max_date FROM orders', con).iloc[0]
    categories = pd.read_sql_query('SELECT DISTINCT category FROM products ORDER BY category', con)['category'].tolist()
    cities = pd.read_sql_query('SELECT DISTINCT city FROM customers ORDER BY city', con)['city'].tolist()

st.sidebar.title('Retail Intelligence')
page = st.sidebar.radio('Navigate', ['Overview','Customer Intelligence','SQL Performance'])
st.sidebar.caption('Filters apply to the analytical views where supported.')
dates = st.sidebar.date_input('Date range', (pd.to_datetime(bounds.min_date).date(), pd.to_datetime(bounds.max_date).date()))
selected_segment = st.sidebar.multiselect('Customer segment', sorted(rfm_all.segment.unique()))
selected_category = st.sidebar.multiselect('Category', categories)
selected_city = st.sidebar.multiselect('City / region', cities)
start, end = dates if isinstance(dates, tuple) and len(dates)==2 else (None,None)

if page == 'Overview':
    st.title('Retail Customer Intelligence & Campaign Analytics')
    st.caption('Turn transaction history into customer value, retention priorities and campaign actions.')
    kp = kpis(start,end); rr = repeat_rate(start,end)
    cols = st.columns(5)
    vals=[(f"£{kp['revenue']:,.0f}",'Revenue'),(f"{int(kp['customers']):,}",'Customers'),(f"{int(kp['orders']):,}",'Orders'),(f"£{kp['aov']:,.2f}",'AOV'),(f"{rr:.1f}%",'Repeat rate')]
    for c,(v,l) in zip(cols,vals): c.metric(l,v)
    m=monthly_revenue(start,end); c=category_revenue(start,end)
    a,b=st.columns(2)
    with a: st.plotly_chart(px.line(m,x='month',y='revenue',markers=True,title='How is revenue changing over time?'),width='stretch')
    with b: st.plotly_chart(px.bar(c.head(10),x='category',y='revenue',title='Which categories generate the most revenue?'),width='stretch')
    top=rfm_all.head(10).copy(); top['customer_id']=top.customer_id.astype(str)
    st.plotly_chart(px.bar(top.sort_values('monetary'),x='monetary',y='customer_id',orientation='h',title='Who are the highest-value customers?'),width='stretch')
    st.markdown('<div class="insight"><b>Business lens:</b> Use the Customer Intelligence view to move from performance reporting to specific retention and engagement actions.</div>',unsafe_allow_html=True)

elif page == 'Customer Intelligence':
    st.title('Customer Intelligence')
    rfm=rfm_all.copy()
    if selected_segment: rfm=rfm[rfm.segment.isin(selected_segment)]
    if selected_city:
        with get_connection() as con:
            city_ids=pd.read_sql_query('SELECT customer_id FROM customers WHERE city IN (%s)'%(','.join('?'*len(selected_city))),con,params=selected_city)['customer_id']
        rfm=rfm[rfm.customer_id.isin(city_ids)]
    s=segment_summary(rfm)
    a,b=st.columns(2)
    with a: st.plotly_chart(px.bar(s,x='segment',y='customers',title='How many customers are in each segment?'),width='stretch')
    with b: st.plotly_chart(px.bar(s,x='segment',y='revenue',title='Which segments contribute the most revenue?'),width='stretch')
    if len(rfm):
        rfm['recommended_action']=rfm.segment.map({'Champions':'VIP loyalty rewards','Loyal Customers':'Cross-sell and loyalty campaigns','New Customers':'Onboarding / second-purchase campaign','Potential Loyalists':'Personalized repeat-purchase offer','At Risk':'Win-back campaign','Lost Customers':'Reactivation campaign'})
        st.dataframe(rfm[['customer_id','recency','frequency','monetary','segment','recommended_action']].rename(columns={'customer_id':'Customer ID','recency':'Recency (days)','frequency':'Frequency','monetary':'Monetary','segment':'Segment','recommended_action':'Recommended Action'}),width='stretch',hide_index=True)
        share = len(rfm[rfm.segment=='Champions'])/len(rfm)*100
        champ_rev = rfm.loc[rfm.segment=='Champions','monetary'].sum()/rfm.monetary.sum()*100 if rfm.monetary.sum() else 0
        st.markdown(f'<div class="insight"><b>Insight:</b> Champions are {share:.1f}% of the filtered customers and contribute {champ_rev:.1f}% of their revenue. These recommendations are analytical hypotheses, not guaranteed campaign outcomes.</div>',unsafe_allow_html=True)
    else: st.info('No customers match the selected filters.')

else:
    st.title('SQL Query Performance')
    st.write('Representative indexed lookup: `SELECT * FROM orders WHERE customer_id = ?`')
    customer_id=int(rfm_all.iloc[0].customer_id)

    def performance_demo(customer_id, repeats=25):
        # Use an isolated in-memory copy so the production-style database indexes
        # do not contaminate the "before index" experiment.
        with get_connection() as source:
            source_orders = pd.read_sql_query(
                'SELECT order_id, customer_id, order_date, order_status FROM orders',
                source,
            )

        con=sqlite3.connect(':memory:')
        source_orders.to_sql('orders', con, index=False, if_exists='replace')
        lookup='SELECT * FROM orders WHERE customer_id = ?'
        params=(customer_id,)

        plan_before=con.execute('EXPLAIN QUERY PLAN '+lookup, params).fetchall()
        con.execute(lookup, params).fetchall()  # warm-up
        before_samples=[]
        for _ in range(repeats):
            t0=time.perf_counter()
            con.execute(lookup, params).fetchall()
            before_samples.append((time.perf_counter()-t0)*1000)

        con.execute('CREATE INDEX idx_demo_customer_id ON orders(customer_id)')
        con.commit()
        plan_after=con.execute('EXPLAIN QUERY PLAN '+lookup, params).fetchall()
        con.execute(lookup, params).fetchall()  # warm-up
        after_samples=[]
        for _ in range(repeats):
            t0=time.perf_counter()
            con.execute(lookup, params).fetchall()
            after_samples.append((time.perf_counter()-t0)*1000)
        con.close()

        return (
            float(pd.Series(before_samples).median()),
            float(pd.Series(after_samples).median()),
            plan_before,
            plan_after,
        )

    before, after, plan_before, plan_after=performance_demo(customer_id)
    c1,c2=st.columns(2)
    c1.metric('Before index',f'{before:.3f} ms')
    c2.metric('After index',f'{after:.3f} ms')
    st.caption('Timing shown is the median of 25 local executions after a warm-up run. Exact wall-clock values depend on the machine and dataset size.')
    st.subheader('Execution plans')
    st.code('Before:\n'+str(plan_before)+'\n\nAfter:\n'+str(plan_after),language='text')
    st.info('Before indexing, SQLite scans the orders table. After indexing, the plan should use idx_demo_customer_id for the customer_id lookup. On a small demo dataset, wall-clock differences can be negligible; EXPLAIN QUERY PLAN is the stronger demonstration of the access-strategy change. Indexes also add storage and write-maintenance cost.')

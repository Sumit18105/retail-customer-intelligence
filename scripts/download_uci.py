"""Download UCI Online Retail when network access is available.
The app ships with a deterministic demo CSV so it works immediately; this script lets you replace it with the public UCI source.
"""
from urllib.request import urlretrieve
from pathlib import Path
import zipfile
BASE=Path(__file__).resolve().parents[1]
url='https://archive.ics.uci.edu/static/public/352/online+retail.zip'
out=BASE/'data'/'online_retail.zip'
urlretrieve(url,out)
with zipfile.ZipFile(out) as z:
    names=z.namelist(); xlsx=next(n for n in names if n.lower().endswith('.xlsx')); z.extract(xlsx, BASE/'data')
print('Downloaded:', xlsx)
print('Run your adapted ingestion against the workbook, or replace demo_retail_data.csv after transforming the source schema.')

import sqlite3
import pandas as pd
import os
from logger import init, step, done, finish

init("export_for_cloud.py")

# Create output directory
os.makedirs("data/cloud", exist_ok=True)

conn = sqlite3.connect("patents.db")

step("yearly_patent_counts")
pd.read_sql("SELECT * FROM yearly_patent_counts", conn).to_csv("data/cloud/yearly.csv", index=False)
done()

step("company_patent_counts")
pd.read_sql("SELECT * FROM company_patent_counts", conn).to_csv("data/cloud/companies.csv", index=False)
done()

step("inventor_patent_counts")
pd.read_sql("SELECT * FROM inventor_patent_counts", conn).to_csv("data/cloud/inventors.csv", index=False)
done()

step("countries")
pd.read_sql("""
    SELECT l.country AS country_code,
           COUNT(DISTINCT pi.patent_id) AS patent_count
    FROM inventors i
    JOIN patent_inventor pi ON i.inventor_id = pi.inventor_id
    JOIN locations l        ON i.country     = l.location_id
    WHERE l.country IS NOT NULL AND l.country != ''
    GROUP BY l.country
    ORDER BY patent_count DESC
    LIMIT 15;
""", conn).to_csv("data/cloud/countries.csv", index=False)
done()

conn.close()
finish()
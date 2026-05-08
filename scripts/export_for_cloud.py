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
pd.read_sql("""
    SELECT * FROM inventor_patent_counts
    ORDER BY patent_count DESC
    LIMIT 500
""", conn).to_csv("data/cloud/inventors.csv", index=False)
done()

step("countries")
pd.read_sql("""
    SELECT country AS country_code,
           COUNT(*) AS patent_count
    FROM inventors
    WHERE country IS NOT NULL AND country != ''
    GROUP BY country
    ORDER BY patent_count DESC
    LIMIT 15;
""", conn).to_csv("data/cloud/countries.csv", index=False)
done()

conn.close()
finish()
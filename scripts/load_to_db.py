# scripts/load_to_db.py
import pandas as pd
import sqlite3
import os

DB_PATH = "patents.db"

# Remove old DB (because of re-running the code)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(" Removed old database")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1 Create schema
print("Creating tables...")
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS patents (
        patent_id   TEXT PRIMARY KEY,
        title       TEXT,
        abstract    TEXT,
        filing_date TEXT,
        year        INTEGER,
        type        TEXT
    );

    CREATE TABLE IF NOT EXISTS inventors (
        inventor_id TEXT PRIMARY KEY,
        name        TEXT,
        country     TEXT
    );

    CREATE TABLE IF NOT EXISTS companies (
        company_id  TEXT PRIMARY KEY,
        name        TEXT
    );

    CREATE TABLE IF NOT EXISTS patent_inventor (
        patent_id   TEXT,
        inventor_id TEXT,
        FOREIGN KEY (patent_id)   REFERENCES patents(patent_id),
        FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id)
    );

    CREATE TABLE IF NOT EXISTS patent_company (
        patent_id  TEXT,
        company_id TEXT,
        FOREIGN KEY (patent_id)  REFERENCES patents(patent_id),
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
    );
    CREATE TABLE IF NOT EXISTS locations (
        location_id TEXT PRIMARY KEY,
        city        TEXT,
        state       TEXT,
        country     TEXT
    );
""")
conn.commit()
print(" Schema created")

# 2. Load CSVs into DB 
def load_table(csv_path, table_name, chunksize=100_000):
    """Load a CSV into SQLite in chunks to handle large files."""
    print(f"Loading {table_name}...")
    total = 0
    for chunk in pd.read_csv(csv_path, chunksize=chunksize, low_memory=False):
        chunk.to_sql(table_name, conn, if_exists="append", index=False)
        total += len(chunk)
        print(f"  {total:,} rows loaded...", end="\r")
    print(f"   {table_name}: {total:,} rows loaded    ")

load_table("data/clean/clean_patents.csv",   "patents")
load_table("data/clean/clean_inventors.csv", "inventors")
load_table("data/clean/clean_companies.csv", "companies")
load_table("data/clean/patent_inventor.csv", "patent_inventor")
load_table("data/clean/patent_company.csv",  "patent_company")
load_table("data/clean/clean_locations.csv", "locations")

# 3 Adding indexes for faster queries 
print("Adding indexes...")
cursor.executescript("""
    CREATE INDEX IF NOT EXISTS idx_patents_year       ON patents(year);
    CREATE INDEX IF NOT EXISTS idx_patents_type       ON patents(type);
    CREATE INDEX IF NOT EXISTS idx_pat_inv_patent     ON patent_inventor(patent_id);
    CREATE INDEX IF NOT EXISTS idx_pat_inv_inventor   ON patent_inventor(inventor_id);
    CREATE INDEX IF NOT EXISTS idx_pat_co_patent      ON patent_company(patent_id);
    CREATE INDEX IF NOT EXISTS idx_pat_co_company     ON patent_company(company_id);
    CREATE INDEX IF NOT EXISTS idx_locations_country ON locations(country);
    CREATE INDEX IF NOT EXISTS idx_locations_id      ON locations(location_id);
""")
conn.commit()
print("Indexes created")

#4 Verify row counts
print("\n Verification ")
tables = ["patents", "inventors", "companies", "patent_inventor", "patent_company", "locations"]
for table in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<20} {count:>12,} rows")

conn.close()
print("\nDatabase ready: patents.db")

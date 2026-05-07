# scripts/add_indexes.py
import sqlite3
import time
from logger import init, step, done, finish

init("add_indexes.py")

conn = sqlite3.connect("patents.db")
conn.execute("PRAGMA journal_mode=OFF;")
conn.execute("PRAGMA synchronous=OFF;")
conn.execute("PRAGMA cache_size=-64000;")

print("Adding indexes to patents.db...")
print("(This runs once and may take 2-5 minutes on 9M rows — but only needed once)\n")

indexes = [
    ("idx_patents_year",        "CREATE INDEX IF NOT EXISTS idx_patents_year        ON patents(year);"),
    ("idx_pat_co_company_id",   "CREATE INDEX IF NOT EXISTS idx_pat_co_company_id   ON patent_company(company_id);"),
    ("idx_pat_co_patent_id",    "CREATE INDEX IF NOT EXISTS idx_pat_co_patent_id    ON patent_company(patent_id);"),
    ("idx_pat_inv_inventor_id", "CREATE INDEX IF NOT EXISTS idx_pat_inv_inventor_id ON patent_inventor(inventor_id);"),
    ("idx_pat_inv_patent_id",   "CREATE INDEX IF NOT EXISTS idx_pat_inv_patent_id   ON patent_inventor(patent_id);"),
]

for name, sql in indexes:
    step(name)
    print(f"  Creating {name}...", end=" ", flush=True)
    conn.execute(sql)
    conn.commit()
    done(name)
    print("done")

conn.close()
print("\nAll indexes created. Now run analytics.py")

finish()
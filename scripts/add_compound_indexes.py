# scripts/add_compound_indexes.py
import sqlite3
import time
from logger import init, step, done, finish

init("add_compound_indexes.py")

conn = sqlite3.connect("patents.db")
conn.execute("PRAGMA journal_mode=OFF;")
conn.execute("PRAGMA synchronous=OFF;")
conn.execute("PRAGMA cache_size=-128000;")

print("Adding compound indexes...")

indexes = [
    # Compound index — covers both patent_id and year in one lookup
    ("idx_patents_id_year",
     "CREATE INDEX IF NOT EXISTS idx_patents_id_year ON patents(patent_id, year);"),

    # Covering index for patent_company — avoids table lookup entirely
    ("idx_pc_covering",
     "CREATE INDEX IF NOT EXISTS idx_pc_covering ON patent_company(patent_id, company_id);"),

    # Covering index for patent_inventor
    ("idx_pi_covering",
     "CREATE INDEX IF NOT EXISTS idx_pi_covering ON patent_inventor(patent_id, inventor_id);"),
]

for name, sql in indexes:
    step(name)
    
    print(f"  Creating {name}...", end=" ", flush=True)
    t = time.time()
    conn.execute(sql)
    conn.commit()
    done(name)
    print(f"done ({time.time()-t:.1f}s)")

conn.close()
print("\nNow run build_summary_tables.py again")

finish()
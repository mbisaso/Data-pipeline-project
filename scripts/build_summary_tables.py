# scripts/build_summary_tables.py
import sqlite3
import time
from logger import init, step, done, finish

init("build_summary_tables.py")

conn = sqlite3.connect("patents.db")
conn.execute("PRAGMA journal_mode=OFF;")
conn.execute("PRAGMA synchronous=OFF;")
conn.execute("PRAGMA cache_size=-128000;")
conn.execute("PRAGMA temp_store=MEMORY;")
conn.execute("PRAGMA mmap_size=268435456;")

print("Building summary tables...\n")

steps = [
    (
        "yearly_patent_counts",
        """
        DROP TABLE IF EXISTS yearly_patent_counts;
        CREATE TABLE yearly_patent_counts AS
        SELECT year, COUNT(*) AS total_patents
        FROM patents
        WHERE year >= 1976 AND year IS NOT NULL
        GROUP BY year
        ORDER BY year;
        """
    ),
    (
        "tmp_patent_ids",
        """
        DROP TABLE IF EXISTS tmp_patent_ids;
        CREATE TABLE tmp_patent_ids AS
        SELECT patent_id FROM patents
        WHERE year >= 1976 AND year IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_tmp_pid ON tmp_patent_ids(patent_id);
        """
    ),
    (
        "company_patent_counts",
        """
        DROP TABLE IF EXISTS company_patent_counts;
        CREATE TABLE company_patent_counts AS
        SELECT pc.company_id, c.name, COUNT(*) AS patent_count
        FROM patent_company pc
        JOIN tmp_patent_ids t ON t.patent_id  = pc.patent_id
        JOIN companies c      ON c.company_id = pc.company_id
        GROUP BY pc.company_id
        ORDER BY patent_count DESC;
        """
    ),
    (
        "inventor_patent_counts",
        """
        DROP TABLE IF EXISTS inventor_patent_counts;
        CREATE TABLE inventor_patent_counts AS
        SELECT pi.inventor_id, i.name, COUNT(*) AS patent_count
        FROM patent_inventor pi
        JOIN tmp_patent_ids t ON t.patent_id   = pi.patent_id
        JOIN inventors i      ON i.inventor_id = pi.inventor_id
        GROUP BY pi.inventor_id
        ORDER BY patent_count DESC;
        """
    ),
    (
        "tmp_top3_companies",
        """
        DROP TABLE IF EXISTS tmp_top3_companies;
        CREATE TABLE tmp_top3_companies AS
        SELECT company_id FROM company_patent_counts LIMIT 3;
        """
    ),
    (
        "company_yearly_counts",
        """
        DROP TABLE IF EXISTS company_yearly_counts;
        CREATE TABLE company_yearly_counts AS
        SELECT p.year, pc.company_id, COUNT(*) AS patent_count
        FROM patent_company pc
        JOIN tmp_patent_ids t     ON t.patent_id  = pc.patent_id
        JOIN patents p            ON p.patent_id  = pc.patent_id
        JOIN tmp_top3_companies c ON c.company_id = pc.company_id
        GROUP BY p.year, pc.company_id
        ORDER BY p.year;
        """
    ),
    (
        "cleanup temp tables",
        """
        DROP TABLE IF EXISTS tmp_patent_ids;
        DROP TABLE IF EXISTS tmp_top3_companies;
        """
    ),
]

for name, sql in steps:
    step(name)
    print(f"  Building {name}...", end=" ", flush=True)
    t = time.time()
    for stmt in sql.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            conn.execute(stmt)
    conn.commit()
    done(name)
    print(f"done ({time.time()-t:.1f}s)")

conn.close()
print("\nAll summary tables built.")
print("Next: run analytics.py")

finish()
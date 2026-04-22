# scripts/run_queries.py
import sqlite3
import pandas as pd
import os
import json
os.makedirs("reports", exist_ok=True)

conn = sqlite3.connect("patents.db")
print("Connected to patents.db\n")

#Q1:Top Inventors
print("Running Q1: Top Inventors...")
q1 = """
    SELECT 
        i.name,
        COUNT(pi.patent_id) AS patent_count
    FROM inventors i
    JOIN patent_inventor pi ON i.inventor_id = pi.inventor_id
    GROUP BY i.inventor_id, i.name
    ORDER BY patent_count DESC
    LIMIT 10;
"""
top_inventors = pd.read_sql(q1, conn)
print(top_inventors.to_string(index=False))

#Q2:Top Companies 
print("\nRunning Q2: Top Companies...")
q2 = """
    SELECT 
        c.name,
        COUNT(pc.patent_id) AS patent_count
    FROM companies c
    JOIN patent_company pc ON c.company_id = pc.company_id
    GROUP BY c.company_id, c.name
    ORDER BY patent_count DESC
    LIMIT 10;
"""
top_companies = pd.read_sql(q2, conn)
print(top_companies.to_string(index=False))

 
# Q3:Top Countries — real country names via locations table
print("\nRunning Q3: Top Countries...")
q3 = """
    SELECT 
        l.country,
        COUNT(DISTINCT pi.patent_id) AS patent_count
    FROM inventors i
    JOIN patent_inventor pi ON i.inventor_id = pi.inventor_id
    JOIN locations l        ON i.country     = l.location_id
    WHERE l.country IS NOT NULL
      AND l.country != ''
    GROUP BY l.country
    ORDER BY patent_count DESC
    LIMIT 10;
"""
countries = pd.read_sql(q3, conn)
print(countries.to_string(index=False))
 

#Q4:Trends Over Time
print("\nRunning Q4: Patents Per Year...")
q4 = """
    SELECT 
        year,
        COUNT(*) AS total_patents
    FROM patents
    WHERE year IS NOT NULL
    GROUP BY year
    ORDER BY year;
"""
trends = pd.read_sql(q4, conn)
print(trends.to_string(index=False))

#Q5:JOIN Query
print("\nRunning Q5: Patents with Inventors and Companies...")
q5 = """
    SELECT 
        p.patent_id,
        p.title,
        p.year,
        p.type,
        i.name  AS inventor_name,
        c.name  AS company_name
    FROM patents p
    JOIN patent_inventor pi ON p.patent_id = pi.patent_id
    JOIN inventors i        ON pi.inventor_id = i.inventor_id
    JOIN patent_company pc  ON p.patent_id = pc.patent_id
    JOIN companies c        ON pc.company_id = c.company_id
    LIMIT 20;
"""
joined = pd.read_sql(q5, conn)
print(joined.to_string(index=False))

#Q6:CTE Query
print("\nRunning Q6: CTE — Inventor productivity by type...")
q6 = """
    WITH inventor_counts AS (
        SELECT 
            i.inventor_id,
            i.name,
            COUNT(pi.patent_id) AS total_patents
        FROM inventors i
        JOIN patent_inventor pi ON i.inventor_id = pi.inventor_id
        GROUP BY i.inventor_id, i.name
    ),
    top_inventors_cte AS (
        SELECT *
        FROM inventor_counts
        WHERE total_patents >= 10
    )
    SELECT 
        t.name,
        t.total_patents,
        p.type,
        COUNT(p.patent_id) AS patents_by_type
    FROM top_inventors_cte t
    JOIN patent_inventor pi ON t.inventor_id = pi.inventor_id
    JOIN patents p          ON pi.patent_id = p.patent_id
    GROUP BY t.inventor_id, t.name, p.type
    ORDER BY t.total_patents DESC, patents_by_type DESC
    LIMIT 20;
"""
cte_result = pd.read_sql(q6, conn)
print(cte_result.to_string(index=False))

#Q7:Ranking Query
print("\nRunning Q7: Ranking Inventors with Window Function...")
q7 = """
    SELECT 
        name,
        total_patents,
        RANK()       OVER (ORDER BY total_patents DESC) AS rank,
        DENSE_RANK() OVER (ORDER BY total_patents DESC) AS dense_rank,
        NTILE(4)     OVER (ORDER BY total_patents DESC) AS quartile
    FROM (
        SELECT 
            i.name,
            COUNT(pi.patent_id) AS total_patents
        FROM inventors i
        JOIN patent_inventor pi ON i.inventor_id = pi.inventor_id
        GROUP BY i.inventor_id, i.name
    ) sub
    ORDER BY rank
    LIMIT 20;
"""
ranked = pd.read_sql(q7, conn)
print(ranked.to_string(index=False))



#Save results
print("\nSaving query results...")
top_inventors.to_csv("reports/top_inventors.csv",   index=False)
top_companies.to_csv("reports/top_companies.csv",   index=False)
countries.to_csv("reports/country_trends.csv",      index=False)
trends.to_csv("reports/yearly_trends.csv",          index=False)
joined.to_csv("reports/joined_sample.csv",          index=False)
cte_result.to_csv("reports/cte_result.csv",         index=False)
ranked.to_csv("reports/ranked_inventors.csv",       index=False)

#JSON Report
print("\nGenerating JSON report...")
 
total_patents_count = int(
    pd.read_sql("SELECT COUNT(*) AS total FROM patents", conn).iloc[0]['total']
)
 
total_country_patents = countries['patent_count'].sum()
 
report = {
    "total_patents": total_patents_count,
 
    # Q1 result — column is patent_count
    "top_inventors": [
        {
            "rank":    i + 1,
            "name":    row['name'],
            "patents": int(row['patent_count'])
        }
        for i, row in top_inventors.iterrows()
    ],
 
    # Q2 result 
    "top_companies": [
        {
            "rank":    i + 1,
            "name":    row['name'],
            "patents": int(row['patent_count'])
        }
        for i, row in top_companies.iterrows()
    ],
 
    # Q3 result 
    "top_countries": [
    {
        "country":      row['country'],
        "patent_count": int(row['patent_count']),
        "share":        round(int(row['patent_count']) / total_country_patents, 4)
    }
    for _, row in countries.iterrows()
       
    ],
 
    # Q4 result
    "yearly_trends": [
        {
            "year":          int(row['year']),
            "total_patents": int(row['total_patents'])
        }
        for _, row in trends.iterrows()
    ],
 
    # Q7 result 
    "ranked_inventors": [
        {
            "rank":          int(row['rank']),
            "name":          row['name'],
            "total_patents": int(row['total_patents']),
            "quartile":      int(row['quartile'])
        }
        for _, row in ranked.iterrows()
    ]
}
 
with open("reports/report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("  reports/report.json saved")
 
#JSON Preview
print("\n JSON Preview")
preview = {
    "total_patents":    report["total_patents"],
    "top_inventors":    report["top_inventors"][:3],
    "top_companies":    report["top_companies"][:3],
    "top_countries":    report["top_countries"][:3],
    "yearly_trends":    report["yearly_trends"][-3:],
    "ranked_inventors": report["ranked_inventors"][:3]
}
print(json.dumps(preview, indent=2))

print("  All reports + Json report saved to reports/")

conn.close()
print("\nAll 7 queries complete!")
# scripts/visualize.py
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
from logger import init, step, done, finish, error

os.makedirs("reports/charts", exist_ok=True)

init("visualize.py")

step("Connecting to patents.db")
conn = sqlite3.connect("patents.db")
print("Connected to patents.db\n")
done("Connected")

sns.set_theme(style="whitegrid")
COLORS = sns.color_palette("Blues_r", 10)

# ══════════════════════════════════════════════════════════════
# CHART 1: Patents Per Year (Line Chart)
# ══════════════════════════════════════════════════════════════
step("Chart 1: Patents Per Year")
trends = pd.read_sql("""
    SELECT year, COUNT(*) AS total_patents
    FROM patents
    WHERE year IS NOT NULL AND year >= 1976
    GROUP BY year
    ORDER BY year;
""", conn)

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(trends['year'], trends['total_patents'],
        color='steelblue', linewidth=2.5, marker='o', markersize=3)
ax.fill_between(trends['year'], trends['total_patents'],
                alpha=0.15, color='steelblue')
ax.set_title("Global Patent Grants Per Year (1976–Present)",
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Number of Patents", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("reports/charts/01_patents_per_year.png", dpi=150)
plt.close()
done("Chart 1: Patents Per Year")
print("   01_patents_per_year.png")


# ══════════════════════════════════════════════════════════════
# CHART 2: Top 10 Inventors (Horizontal Bar Chart)
# ══════════════════════════════════════════════════════════════
step("Chart 2: Top 10 Inventors")
top_inv = pd.read_sql("""
    SELECT i.name, COUNT(pi.patent_id) AS patent_count
    FROM inventors i
    JOIN patent_inventor pi ON i.inventor_id = pi.inventor_id
    GROUP BY i.inventor_id, i.name
    ORDER BY patent_count DESC
    LIMIT 10;
""", conn).sort_values('patent_count')

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(top_inv['name'], top_inv['patent_count'],
               color=COLORS, edgecolor='white')
for bar in bars:
    width = bar.get_width()
    ax.text(width + 5, bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}", va='center', fontsize=10)
ax.set_title("Top 10 Most Prolific Inventors (All Time)",
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel("Number of Patents", fontsize=12)
ax.set_ylabel("")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig("reports/charts/02_top_inventors.png", dpi=150)
plt.close()
done("Chart 2: Top 10 Inventors")
print("  02_top_inventors.png")


# ══════════════════════════════════════════════════════════════
# CHART 3: Top 10 Companies (Horizontal Bar Chart)
# ══════════════════════════════════════════════════════════════
step("Chart 3: Top 10 Companies")
top_co = pd.read_sql("""
    SELECT c.name, COUNT(pc.patent_id) AS patent_count
    FROM companies c
    JOIN patent_company pc ON c.company_id = pc.company_id
    GROUP BY c.company_id, c.name
    ORDER BY patent_count DESC
    LIMIT 10;
""", conn).sort_values('patent_count')

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(top_co['name'], top_co['patent_count'],
               color=sns.color_palette("Greens_r", 10), edgecolor='white')
for bar in bars:
    width = bar.get_width()
    ax.text(width + 20, bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}", va='center', fontsize=10)
ax.set_title("Top 10 Companies by Patent Count (All Time)",
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel("Number of Patents", fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig("reports/charts/03_top_companies.png", dpi=150)
plt.close()
done("Chart 3: Top 10 Companies")
print("  03_top_companies.png")


# ══════════════════════════════════════════════════════════════
# CHART 4: Pie Chart of Patent Types — FIXED (legend instead of overlapping labels)
# ══════════════════════════════════════════════════════════════
step("Chart 4: Patent Types")
types = pd.read_sql("""
    SELECT type, COUNT(*) AS total
    FROM patents
    WHERE type IS NOT NULL
    GROUP BY type
    ORDER BY total DESC;
""", conn)

fig, ax = plt.subplots(figsize=(10, 8))
colors = sns.color_palette("Set2", len(types))
wedges, texts, autotexts = ax.pie(
    types['total'],
    labels=None,                        # no inline labels — use legend instead
    autopct='%1.1f%%',
    colors=colors,
    startangle=140,
    pctdistance=0.75,                   # push % labels inside slices
    wedgeprops=dict(edgecolor='white', linewidth=2)
)
for autotext in autotexts:
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

# Legend with type name + count + percentage
total_patents = types['total'].sum()
legend_labels = [
    f"{row['type'].title()}  —  {int(row['total']):,} ({row['total']/total_patents*100:.1f}%)"
    for _, row in types.iterrows()
]
ax.legend(
    wedges, legend_labels,
    title="Patent Type",
    title_fontsize=12,
    fontsize=11,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.12),
    ncol=2,
    frameon=True
)
ax.set_title("Patent Grants by Type", fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig("reports/charts/04_patent_types.png", dpi=150, bbox_inches='tight')
plt.close()
done("Chart 4: Patent Types")
print("  04_patent_types.png")


# ══════════════════════════════════════════════════════════════
# CHART 5: Patents Per Decade (Bar Chart)
# ══════════════════════════════════════════════════════════════
step("Chart 5: Patents Per Decade")
decades = pd.read_sql("""
    SELECT
        (year / 10) * 10  AS decade,
        COUNT(*)          AS total_patents
    FROM patents
    WHERE year IS NOT NULL AND year >= 1976
    GROUP BY decade
    ORDER BY decade;
""", conn)
decades['decade_label'] = decades['decade'].astype(str) + "s"

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(decades['decade_label'], decades['total_patents'],
              color=sns.color_palette("Purples_r", len(decades)),
              edgecolor='white', width=0.6)
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 1000,
            f"{int(height):,}", ha='center', fontsize=10)
ax.set_title("Total Patent Grants by Decade", fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel("Decade", fontsize=12)
ax.set_ylabel("Number of Patents", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig("reports/charts/05_patents_per_decade.png", dpi=150)
plt.close()
done("Chart 5: Patents Per Decade")
print("  05_patents_per_decade.png")


# ══════════════════════════════════════════════════════════════
# CHART 6: Top 10 Inventors — Recent (2015–Present)
# ══════════════════════════════════════════════════════════════
step("Chart 6: Top Inventors (2015–Present)")
recent_inv = pd.read_sql("""
    SELECT i.name, COUNT(pi.patent_id) AS patent_count
    FROM inventors i
    JOIN patent_inventor pi ON i.inventor_id = pi.inventor_id
    JOIN patents p          ON pi.patent_id = p.patent_id
    WHERE p.year >= 2015
    GROUP BY i.inventor_id, i.name
    ORDER BY patent_count DESC
    LIMIT 10;
""", conn).sort_values('patent_count')

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(recent_inv['name'], recent_inv['patent_count'],
               color=sns.color_palette("Oranges_r", 10), edgecolor='white')
for bar in bars:
    width = bar.get_width()
    ax.text(width + 1, bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}", va='center', fontsize=10)
ax.set_title("Top 10 Inventors (2015–Present)", fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel("Number of Patents", fontsize=12)
plt.tight_layout()
plt.savefig("reports/charts/06_top_inventors_recent.png", dpi=150)
plt.close()
done("Chart 6: Top Inventors (2015–Present)")
print("   06_top_inventors_recent.png")


# ══════════════════════════════════════════════════════════════
# CHART 7: Top 10 Companies — Recent (2015–Present)
# ══════════════════════════════════════════════════════════════
step("Chart 7: Top Companies (2015–Present)")
recent_co = pd.read_sql("""
    SELECT c.name, COUNT(pc.patent_id) AS patent_count
    FROM companies c
    JOIN patent_company pc ON c.company_id = pc.company_id
    JOIN patents p         ON pc.patent_id = p.patent_id
    WHERE p.year >= 2015
    GROUP BY c.company_id, c.name
    ORDER BY patent_count DESC
    LIMIT 10;
""", conn).sort_values('patent_count')

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(recent_co['name'], recent_co['patent_count'],
               color=sns.color_palette("RdPu_r", 10), edgecolor='white')
for bar in bars:
    width = bar.get_width()
    ax.text(width + 20, bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}", va='center', fontsize=10)
ax.set_title("Top 10 Companies by Patents (2015–Present)",
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel("Number of Patents", fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig("reports/charts/07_top_companies_recent.png", dpi=150)
plt.close()
done("Chart 7: Top Companies (2015–Present)")
print("   07_top_companies_recent.png")


# ══════════════════════════════════════════════════════════════
# CHART 8: Top 15 Countries by Patent Count
# ══════════════════════════════════════════════════════════════
step("Chart 8: Top 15 Countries")
COUNTRY_NAMES = {
    'US':'United States','JP':'Japan','DE':'Germany',
    'CN':'China','KR':'South Korea','TW':'Taiwan',
    'GB':'United Kingdom','CA':'Canada','FR':'France',
    'CH':'Switzerland','SE':'Sweden','NL':'Netherlands',
    'IL':'Israel','AU':'Australia','IT':'Italy',
    'FI':'Finland','DK':'Denmark','IN':'India',
    'BE':'Belgium','AT':'Austria','SG':'Singapore',
    'NO':'Norway','RU':'Russia','ES':'Spain','BR':'Brazil',
}

countries = pd.read_sql("""
    SELECT
        l.country                        AS country_code,
        COUNT(DISTINCT pi.patent_id)     AS patent_count
    FROM inventors i
    JOIN patent_inventor pi ON i.inventor_id = pi.inventor_id
    JOIN locations l        ON i.country     = l.location_id
    WHERE l.country IS NOT NULL AND l.country != ''
    GROUP BY l.country
    ORDER BY patent_count DESC
    LIMIT 15;
""", conn)

countries['country_name'] = (
    countries['country_code'].map(COUNTRY_NAMES).fillna(countries['country_code'])
)
total = countries['patent_count'].sum()
countries['share_pct'] = (countries['patent_count'] / total * 100).round(1)
countries = countries.sort_values('patent_count', ascending=True)

fig, ax = plt.subplots(figsize=(13, 9))
bars = ax.barh(
    countries['country_name'], countries['patent_count'],
    color=sns.color_palette("Blues_r", len(countries)), edgecolor='white'
)
for bar, (_, row) in zip(bars, countries.iterrows()):
    width = bar.get_width()
    ax.text(width + 5000, bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}  ({row['share_pct']}%)", va='center', fontsize=10)
ax.set_title(
    "Top 15 Countries by Patent Count (All Time)\nBased on inventor location data",
    fontsize=16, fontweight='bold', pad=15
)
ax.set_xlabel("Number of Patents", fontsize=12)
ax.set_ylabel("")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_xlim(right=countries['patent_count'].max() * 1.25)
plt.tight_layout()
plt.savefig("reports/charts/08_top_countries.png", dpi=150)
plt.close()
done("Chart 8: Top 15 Countries")
print("  08_top_countries.png")


conn.close()
print("\n All 8 charts saved to reports/charts/")
print("\n── Charts Summary ───────────────────────────────────")
print("  01_patents_per_year.png      → Innovation trend over time")
print("  02_top_inventors.png         → All-time top inventors")
print("  03_top_companies.png         → All-time top companies")
print("  04_patent_types.png          → Breakdown by patent type")
print("  05_patents_per_decade.png    → Growth by decade")
print("  06_top_inventors_recent.png  → Top inventors since 2015")
print("  07_top_companies_recent.png  → Top companies since 2015")
print("  08_top_countries.png         → Top 15 countries by patents")

finish() 
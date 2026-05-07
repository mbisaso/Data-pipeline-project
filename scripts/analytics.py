# scripts/analytics.py
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import os
from logger import init, step, done, finish, error

os.makedirs("reports/charts", exist_ok=True)

init("analytics.py")

YEAR_FROM     = 1976
COMPLETE_YEAR = 2023

step("Connecting to patents.db")
conn = sqlite3.connect("patents.db")
conn.execute("PRAGMA journal_mode = OFF;")
conn.execute("PRAGMA synchronous  = OFF;")
conn.execute("PRAGMA cache_size   = -64000;")
conn.execute("PRAGMA temp_store   = MEMORY;")
conn.execute("PRAGMA mmap_size    = 268435456;")
print("Connected to patents.db\n")

count = conn.execute("SELECT COUNT(*) FROM patents").fetchone()[0]
if count == 0:
    error("patents table is empty. Run load_to_db.py first.")
    conn.close()
    exit()
done("Connected")
print(f"patents table has {count:,} rows — proceeding...\n")

sns.set_theme(style="whitegrid")

# ──────────────────────────────────────────────────────────────
#  LOAD BASE DATA from pre-aggregated summary tables
# ──────────────────────────────────────────────────────────────
step("Loading from pre-aggregated summary tables")
trends = pd.read_sql("SELECT * FROM yearly_patent_counts ORDER BY year;", conn)
top_co = pd.read_sql("SELECT * FROM company_patent_counts LIMIT 10;", conn)
top_inv = pd.read_sql("SELECT * FROM inventor_patent_counts LIMIT 10;", conn)
co_yearly = pd.read_sql("""
    SELECT cyc.year, cyc.company_id, cyc.patent_count, c.name
    FROM company_yearly_counts cyc
    JOIN companies c ON c.company_id = cyc.company_id
    ORDER BY cyc.year;
""", conn)
done("Summary tables loaded")
print(" All data loaded from summary tables\n")

# ── Use only complete years throughout ────────────────────────
trends_complete = trends[trends['year'] <= COMPLETE_YEAR].copy()
trends_complete['yoy_growth_pct'] = trends_complete['total_patents'].pct_change() * 100

# ══════════════════════════════════════════════════════════════
#  SECTION 1 — DESCRIPTIVE ANALYTICS
# ══════════════════════════════════════════════════════════════
step("Descriptive analytics")
print("=" * 55)
print("  DESCRIPTIVE ANALYTICS")
print("=" * 55)

print("\n[1] Patent Counts Per Year — Summary Statistics:")
print(trends_complete['total_patents'].describe().apply(lambda x: f"{x:,.2f}"))

print("\n[2] Top 10 Companies — Summary Statistics:")
print(top_co['patent_count'].describe().apply(lambda x: f"{x:,.2f}"))

print("\n[3] Top 10 Inventors — Summary Statistics:")
print(top_inv['patent_count'].describe().apply(lambda x: f"{x:,.2f}"))

skew = stats.skew(trends_complete['total_patents'])
kurt = stats.kurtosis(trends_complete['total_patents'])
print(f"\n[4] Yearly Patent Distribution:")
print(f"    Skewness : {skew:.4f}  {'(right-skewed)' if skew > 0 else '(left-skewed)'}")
print(f"    Kurtosis : {kurt:.4f}  {'(heavy tails)' if kurt > 0 else '(light tails)'}")

avg_growth = trends_complete['yoy_growth_pct'].mean()
print(f"\n[5] Avg Year-over-Year Patent Growth ({YEAR_FROM}–{COMPLETE_YEAR}): {avg_growth:.2f}%")
done("Descriptive analytics")


# ── CHART 9: YoY Growth Rate ──────────────────────────────────
step("Chart 9: YoY Growth Rate")
yoy = trends_complete.dropna(subset=['yoy_growth_pct']).copy()

fig, ax = plt.subplots(figsize=(14, 6))
positive = yoy[yoy['yoy_growth_pct'] >= 0]
negative = yoy[yoy['yoy_growth_pct'] <  0]
ax.bar(positive['year'], positive['yoy_growth_pct'],
       color='#2196F3', edgecolor='white', width=0.8,
       label='Growth year (positive %)')
ax.bar(negative['year'], negative['yoy_growth_pct'],
       color='#EF5350', edgecolor='white', width=0.8,
       label='Decline year (negative %)')
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
max_row = yoy.loc[yoy['yoy_growth_pct'].idxmax()]
min_row = yoy.loc[yoy['yoy_growth_pct'].idxmin()]
ax.annotate(f"Peak: +{max_row['yoy_growth_pct']:.1f}%",
            xy=(max_row['year'], max_row['yoy_growth_pct']),
            xytext=(max_row['year'] + 1, max_row['yoy_growth_pct'] + 1),
            fontsize=9, color='#1565C0', fontweight='bold')
ax.annotate(f"Largest drop: {min_row['yoy_growth_pct']:.1f}%",
            xy=(min_row['year'], min_row['yoy_growth_pct']),
            xytext=(min_row['year'] + 1, min_row['yoy_growth_pct'] - 2),
            fontsize=9, color='#B71C1C', fontweight='bold')
ax.set_title(
    f"Year-over-Year Patent Growth Rate (%) — {YEAR_FROM}–{COMPLETE_YEAR}\n"
    "Only complete years shown — partial years excluded",
    fontsize=14, fontweight='bold', pad=15
)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Growth Rate (%)", fontsize=12)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.legend(fontsize=11, loc='upper right')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("reports/charts/09_yoy_growth.png", dpi=150)
plt.close()
done("Chart 9: YoY Growth Rate")
print("   09_yoy_growth.png")


# ══════════════════════════════════════════════════════════════
#  SECTION 2 — PREDICTIVE ANALYTICS
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("  PREDICTIVE ANALYTICS")
print("=" * 55)

X = trends_complete[['year']].values
y = trends_complete['total_patents'].values

# ── CHART 10: Linear Regression Forecast ─────────────────────
step("Chart 10: Linear Regression Forecast")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
lin_model = LinearRegression()
lin_model.fit(X_train, y_train)

y_pred_test = lin_model.predict(X_test)
r2   = r2_score(y_test, y_pred_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))

print(f"\n[Linear Regression Model Performance]")
print(f"    R² Score : {r2:.4f}  (1.0 = perfect fit)")
print(f"    RMSE     : {rmse:,.0f} patents")

future_years = np.arange(2024, 2031).reshape(-1, 1)
future_preds = lin_model.predict(future_years)

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(trends_complete['year'], trends_complete['total_patents'],
        color='steelblue', linewidth=2.5, marker='o', markersize=4,
        label=f'Actual data ({YEAR_FROM}–{COMPLETE_YEAR})')
ax.plot(future_years, future_preds,
        color='darkorange', linewidth=2.5, linestyle='--',
        marker='s', markersize=6,
        label='Linear forecast (2024–2030)')
ax.axvline(x=COMPLETE_YEAR, color='gray', linestyle=':',
           linewidth=1.5, label='Forecast boundary')
for yr, val in zip(future_years.flatten(), future_preds):
    ax.annotate(f"{int(val):,}", (yr, val),
                textcoords="offset points", xytext=(0, 10),
                ha='center', fontsize=9, color='darkorange')
ax.fill_between(trends_complete['year'],
                trends_complete['total_patents'],
                alpha=0.1, color='steelblue')
ax.set_title(
    f"Patent Count Forecast — Linear Regression\n"
    f"R² = {r2:.4f}  |  RMSE = {rmse:,.0f} patents  |  "
    f"Trained on {YEAR_FROM}–{COMPLETE_YEAR}",
    fontsize=13, fontweight='bold', pad=15
)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Number of Patents", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.legend(fontsize=11)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("reports/charts/10_forecast_linear.png", dpi=150)
plt.close()
done("Chart 10: Linear Regression Forecast")
print(" 10_forecast_linear.png")


# ── CHART 11: Polynomial Regression ──────────────────────────
step("Chart 11: Polynomial Regression Forecast")
poly_model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
poly_model.fit(X, y)

all_years  = np.arange(YEAR_FROM, 2031).reshape(-1, 1)
poly_preds = poly_model.predict(all_years)
poly_preds = np.clip(poly_preds, 0, None)
r2_poly    = r2_score(y, poly_model.predict(X))

print(f"\n[Polynomial Regression Model Performance]")
print(f"    R² Score (degree=2) : {r2_poly:.4f}")

fig, ax = plt.subplots(figsize=(14, 6))
ax.scatter(trends_complete['year'], trends_complete['total_patents'],
           color='steelblue', s=40, alpha=0.8, zorder=3,
           label=f'Actual data ({YEAR_FROM}–{COMPLETE_YEAR})')
ax.plot(all_years, poly_preds, color='crimson', linewidth=2.5,
        label=f'Polynomial fit (degree=2, R²={r2_poly:.4f})')
ax.axvline(x=COMPLETE_YEAR, color='gray', linestyle=':',
           linewidth=1.5, label='Forecast boundary')
for yr in [2025, 2027, 2030]:
    idx = list(all_years.flatten()).index(yr)
    val = poly_preds[idx]
    ax.annotate(f"{int(val):,}", (yr, val),
                textcoords="offset points", xytext=(0, 12),
                ha='center', fontsize=9, color='crimson', fontweight='bold')
ax.set_title(
    f"Patent Count — Polynomial Regression Forecast (degree=2)\n"
    f"R² = {r2_poly:.4f}  |  Trained on {YEAR_FROM}–{COMPLETE_YEAR}  |  "
    f"Projected to 2030",
    fontsize=13, fontweight='bold', pad=15
)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Number of Patents", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.legend(fontsize=11)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("reports/charts/11_forecast_polynomial.png", dpi=150)
plt.close()
done("Chart 11: Polynomial Regression Forecast")
print("   11_forecast_polynomial.png")

conn.close()
print("\n Analytics complete — charts 09–11 saved to reports/charts/")
print("\n── Model Summary ─────────────────────────────────────")
print(f"   Linear Regression     → R²={r2:.4f}, RMSE={rmse:,.0f}")
print(f"   Polynomial (degree=2) → R²={r2_poly:.4f}")

finish()
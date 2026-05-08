# dashboard.py
import streamlit as st
import pandas as pd
import json
import os

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Global Patent Intelligence",
    page_icon="🔬",
    layout="wide"
)

# ── CSV data directory ─────────────────────────────────────────
DATA_DIR = "data/cloud"

# ── Load from CSVs ────────────────────────────────────────────
@st.cache_data
def load_top_inventors():
    df = pd.read_csv(f"{DATA_DIR}/inventors.csv")
    return df[['name','patent_count']].sort_values('patent_count', ascending=False).head(10)

@st.cache_data
def load_top_companies():
    df = pd.read_csv(f"{DATA_DIR}/companies.csv")
    return df[['name','patent_count']].sort_values('patent_count', ascending=False).head(10)

@st.cache_data
def load_trends():
    df = pd.read_csv(f"{DATA_DIR}/yearly.csv")
    return df[['year','total_patents']].sort_values('year')

@st.cache_data
def load_summary():
    yearly    = pd.read_csv(f"{DATA_DIR}/yearly.csv")
    inventors = pd.read_csv(f"{DATA_DIR}/inventors.csv")
    companies = pd.read_csv(f"{DATA_DIR}/companies.csv")
    total     = int(yearly['total_patents'].sum())
    total_inv = 4_257_666
    total_co  = 511_466
    return total, total_inv, total_co

@st.cache_data
def load_countries():
    COUNTRY_NAMES = {
        'US':'United States','JP':'Japan','DE':'Germany',
        'CN':'China','KR':'South Korea','TW':'Taiwan',
        'GB':'United Kingdom','CA':'Canada','FR':'France',
        'CH':'Switzerland','SE':'Sweden','NL':'Netherlands',
        'IL':'Israel','AU':'Australia','IT':'Italy',
        'FI':'Finland','IN':'India','BE':'Belgium',
        'SG':'Singapore','NO':'Norway','RU':'Russia',
        'ES':'Spain','BR':'Brazil','AT':'Austria','DK':'Denmark',
    }
    df = pd.read_csv(f"{DATA_DIR}/countries.csv")
    df['country'] = df['country_code'].map(COUNTRY_NAMES).fillna(df['country_code'])
    return df

# ── Helper to show saved chart images ─────────────────────────
def show_chart(filename, caption=""):
    path = f"reports/charts/{filename}"
    if os.path.exists(path):
        st.image(path, caption=caption, use_container_width=True)
    else:
        st.warning(f"Chart not found: {filename}. Run visualize.py first.")

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
st.sidebar.title("Patent Intelligence")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate to", [
    "Overview",
    "Top Inventors",
    "Top Companies",
    "Countries",
    "Trends Over Time",
    "Predictive Analytics",
    "Search Patents",
])
st.sidebar.markdown("---")
st.sidebar.caption("Data: USPTO PatentsView")
st.sidebar.caption("Coverage: 1976 – present")

# ══════════════════════════════════════════════════════════════
#  PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("Global Patent Intelligence Dashboard")
    st.markdown("Analyzing **9+ million U.S. patents** from 1976 to present.")
    st.markdown("---")

    total, total_inv, total_co = load_summary()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Patents",   f"{total:,}")
    col2.metric("Total Inventors", f"{total_inv:,}")
    col3.metric("Total Companies", f"{total_co:,}")

    st.markdown("---")

    json_path = "reports/report.json"
    if os.path.exists(json_path):
        with open(json_path) as f:
            report = json.load(f)
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Top 5 Inventors")
            inv_df = pd.DataFrame(report['top_inventors'][:5])
            st.dataframe(inv_df[['rank','name','patents']], hide_index=True, use_container_width=True)
        with col_b:
            st.subheader("Top 5 Companies")
            co_df = pd.DataFrame(report['top_companies'][:5])
            st.dataframe(co_df[['rank','name','patents']], hide_index=True, use_container_width=True)
    else:
        st.info("Run run_queries.py to generate report.json")

    st.markdown("---")
    st.subheader("Patent Grants Over Time")
    show_chart("01_patents_per_year.png")

# ══════════════════════════════════════════════════════════════
#  PAGE 2 — TOP INVENTORS
# ══════════════════════════════════════════════════════════════
elif page == "Top Inventors":
    st.title("Top Inventors")
    st.markdown("---")
    tab1, tab2 = st.tabs(["All Time", "Since 2015"])
    with tab1:
        st.subheader("All-Time Top 10 Inventors")
        show_chart("02_top_inventors.png")
        df = load_top_inventors()
        df.index = range(1, len(df) + 1)
        df.index.name = "Rank"
        st.dataframe(df, use_container_width=True)
    with tab2:
        st.subheader("Top 10 Inventors (2015–Present)")
        show_chart("06_top_inventors_recent.png")

# ══════════════════════════════════════════════════════════════
#  PAGE 3 — TOP COMPANIES
# ══════════════════════════════════════════════════════════════
elif page == "Top Companies":
    st.title("Top Companies")
    st.markdown("---")
    tab1, tab2 = st.tabs(["All Time", "Since 2015"])
    with tab1:
        st.subheader("All-Time Top 10 Companies")
        show_chart("03_top_companies.png")
        df = load_top_companies()
        df.index = range(1, len(df) + 1)
        df.index.name = "Rank"
        st.dataframe(df, use_container_width=True)
    with tab2:
        st.subheader("Top 10 Companies (2015–Present)")
        show_chart("07_top_companies_recent.png")

# ══════════════════════════════════════════════════════════════
#  PAGE 4 — COUNTRIES
# ══════════════════════════════════════════════════════════════
elif page == "Countries":
    st.title("Countries by Patent Count")
    st.markdown("---")
    show_chart("08_top_countries.png")
    st.subheader("Data Table")
    df = load_countries()
    total = df['patent_count'].sum()
    df['share %'] = (df['patent_count'] / total * 100).round(2)
    df.index = range(1, len(df) + 1)
    df.index.name = "Rank"
    st.dataframe(df[['country','patent_count','share %']], use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  PAGE 5 — TRENDS OVER TIME
# ══════════════════════════════════════════════════════════════
elif page == "Trends Over Time":
    st.title("Patent Trends Over Time")
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["Yearly Trend", "By Decade", "Patent Types"])
    with tab1:
        show_chart("01_patents_per_year.png")
        st.subheader("Raw Data")
        st.dataframe(load_trends(), use_container_width=True, hide_index=True)
    with tab2:
        show_chart("05_patents_per_decade.png")
    with tab3:
        show_chart("04_patent_types.png")

# ══════════════════════════════════════════════════════════════
#  PAGE 6 — PREDICTIVE ANALYTICS
# ══════════════════════════════════════════════════════════════
elif page == "Predictive Analytics":
    st.title("Predictive Analytics")
    st.markdown("Patent count forecasts using machine learning models.")
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs([
        "YoY Growth Rate",
        "Linear Regression Forecast",
        "Polynomial Regression Forecast",
    ])
    with tab1:
        st.subheader("Year-over-Year Growth Rate (%)")
        st.caption("Blue = growth year   |   Red = decline year")
        show_chart("09_yoy_growth.png")
    with tab2:
        st.subheader("Linear Regression Forecast (2025–2030)")
        st.caption("Assumes patent growth continues at the same average rate.")
        show_chart("10_forecast_linear.png")
    with tab3:
        st.subheader("Polynomial Regression Forecast (2025–2030)")
        st.caption("Captures the curve in patent growth, degree=2.")
        show_chart("11_forecast_polynomial.png")

# ══════════════════════════════════════════════════════════════
#  PAGE 7 — SEARCH PATENTS
# ══════════════════════════════════════════════════════════════
elif page == "Search Patents":
    st.title("Search Patents")
    st.markdown("---")
    st.info(
        " Live search is unavailable in the cloud deployment. "
        "Clone the repo and run locally with `patents.db` to enable this feature."
    )
# scripts/build_relationships.py
import pandas as pd
import zipfile
import os

os.makedirs("data/clean", exist_ok=True)

#1 Read raw files
print("Reading inventor file...")
with zipfile.ZipFile("data/raw/g_inventor_disambiguated.tsv.zip", 'r') as z:
    with z.open(z.namelist()[0]) as f:
        inventors_raw = pd.read_csv(f, sep='\t', low_memory=False)

print("Reading assignee file...")
with zipfile.ZipFile("data/raw/g_assignee_disambiguated.tsv.zip", 'r') as z:
    with z.open(z.namelist()[0]) as f:
        assignees_raw = pd.read_csv(f, sep='\t', low_memory=False)

print("Reading patent file...")
with zipfile.ZipFile("data/raw/g_patent.tsv.zip", 'r') as z:
    with z.open(z.namelist()[0]) as f:
        patents_raw = pd.read_csv(f, sep='\t', low_memory=False)

print(f"  Loaded {len(patents_raw):,} patents")
print(f"  Loaded {len(inventors_raw):,} inventor records")
print(f"  Loaded {len(assignees_raw):,} assignee records")

#2 Clean patents 
print("\nCleaning patents...")
patents = patents_raw[['patent_id', 'patent_title', 'patent_date', 'patent_type']].copy()
patents.rename(columns={
    'patent_title': 'title',
    'patent_date':  'filing_date',
    'patent_type':  'type'
}, inplace=True)
patents['abstract'] = None   # placeholder so DB schema stays consisten
patents.drop_duplicates(subset='patent_id', inplace=True)
patents.dropna(subset=['patent_id', 'title'], inplace=True)
patents['filing_date'] = pd.to_datetime(patents['filing_date'], errors='coerce')
patents['year'] = patents['filing_date'].dt.year
patents.to_csv("data/clean/clean_patents.csv", index=False)
print(f"clean_patents.csv   - {len(patents):,} rows")

#3 Clean inventors
print("Cleaning inventors...")
inventors = inventors_raw[['inventor_id', 'disambig_inventor_name_first',
                            'disambig_inventor_name_last', 'location_id']].copy()
inventors['name'] = (inventors['disambig_inventor_name_first'].fillna('') + ' ' +
                     inventors['disambig_inventor_name_last'].fillna('')).str.strip()
inventors.rename(columns={'location_id': 'country'}, inplace=True)
inventors = inventors[['inventor_id', 'name', 'country']]
inventors.drop_duplicates(subset='inventor_id', inplace=True)
inventors.dropna(subset=['inventor_id'], inplace=True)
inventors.to_csv("data/clean/clean_inventors.csv", index=False)
print(f"clean_inventors.csv - {len(inventors):,} rows")

#4 Clean companies
print("Cleaning companies...")
companies = assignees_raw[['assignee_id', 'disambig_assignee_organization']].copy()
companies.rename(columns={
    'assignee_id':                    'company_id',
    'disambig_assignee_organization': 'name'
}, inplace=True)
companies.drop_duplicates(subset='company_id', inplace=True)
companies.dropna(subset=['company_id', 'name'], inplace=True)
companies.to_csv("data/clean/clean_companies.csv", index=False)
print(f"clean_companies.csv - {len(companies):,} rows")

# 5 Build patent_inventor relationship 
print("Building patent_inventor table...")
pat_inv = inventors_raw[['patent_id', 'inventor_id']].copy()
pat_inv.drop_duplicates(inplace=True)
pat_inv.dropna(inplace=True)
pat_inv.to_csv("data/clean/patent_inventor.csv", index=False)
print(f"patent_inventor.csv - {len(pat_inv):,} rows")

# 6 Build patent_company relationship 
print("Building patent_company table...")
pat_co = assignees_raw[['patent_id', 'assignee_id']].copy()
pat_co.rename(columns={'assignee_id': 'company_id'}, inplace=True)
pat_co.drop_duplicates(inplace=True)
pat_co.dropna(inplace=True)
pat_co.to_csv("data/clean/patent_company.csv", index=False)
print(f"patent_company.csv  - {len(pat_co):,} rows")

#7 Load and clean location mapping
print("Reading location file...")
with zipfile.ZipFile("data/raw/g_location_disambiguated.tsv.zip", 'r') as z:
    with z.open(z.namelist()[0]) as f:
        locations_raw = pd.read_csv(f, sep='\t', low_memory=False,
                                    usecols=['location_id', 'disambig_city',
                                             'disambig_state', 'disambig_country'])

locations_raw.rename(columns={
    'disambig_city':    'city',
    'disambig_state':   'state',
    'disambig_country': 'country'
}, inplace=True)
locations_raw.drop_duplicates(subset='location_id', inplace=True)
locations_raw.dropna(subset=['location_id'], inplace=True)
locations_raw.to_csv("data/clean/clean_locations.csv", index=False)
print(f" clean_locations.csv - {len(locations_raw):,} rows")

print("\nAll clean files ready in data/clean/")

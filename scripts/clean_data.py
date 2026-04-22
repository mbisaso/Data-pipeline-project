import pandas as pd
import zipfile
import os

# Build absolute path relative to THIS script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "raw")

print(os.path.exists(os.path.join(DATA_DIR, "g_inventor_disambiguated.tsv.zip")))

def extract_and_read(zip_path, filename, cols=None):
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(filename) as f:
            return pd.read_csv(f, sep='\t', low_memory=False, usecols=cols)

# Only load the columns  needed

patents_df   = extract_and_read(os.path.join(DATA_DIR, "g_patent.tsv.zip"), "g_patent.tsv",cols=['patent_id', 'patent_title', 'patent_date', 'patent_type'])
inventors_df = extract_and_read(os.path.join(DATA_DIR, "g_inventor_disambiguated.tsv.zip"), "g_inventor_disambiguated.tsv", cols=['patent_id', 'inventor_id', 'disambig_inventor_name_first',
          'disambig_inventor_name_last', 'location_id'])
assignees_df = extract_and_read(os.path.join(DATA_DIR, "g_assignee_disambiguated.tsv.zip"), "g_assignee_disambiguated.tsv", cols=['patent_id', 'assignee_id', 'disambig_assignee_organization'])

print(patents_df.head())
print(patents_df.columns.tolist())
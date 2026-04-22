-- sql/schema.sql

CREATE TABLE IF NOT EXISTS patents (
    patent_id   TEXT PRIMARY KEY,
    title       TEXT,
    abstract    TEXT,        -- NULL in this dataset (not provided in bulk file)
    filing_date TEXT,
    year        INTEGER,
    type        TEXT         -- e.g. utility, design, plant
);

CREATE TABLE IF NOT EXISTS inventors (
    inventor_id TEXT PRIMARY KEY,
    name        TEXT,
    country     TEXT         -- location_id from source (UUID reference)
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

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_patents_year     ON patents(year);
CREATE INDEX IF NOT EXISTS idx_patents_type     ON patents(type);
CREATE INDEX IF NOT EXISTS idx_pat_inv_patent   ON patent_inventor(patent_id);
CREATE INDEX IF NOT EXISTS idx_pat_inv_inventor ON patent_inventor(inventor_id);
CREATE INDEX IF NOT EXISTS idx_pat_co_patent    ON patent_company(patent_id);
CREATE INDEX IF NOT EXISTS idx_pat_co_company   ON patent_company(company_id);
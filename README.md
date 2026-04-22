A data engineering pipeline that collects, cleans, stores, and analyzes real-world U.S. patent data from the 
USPTO PatentsView dataset.

Project Overview
Patents are official records of inventions. This pipeline processes over 9 million U.S. patents granted from 1976 to present and answers important questions such as:
Which companies own the most patents?
Which countries produce the most patents?
How has patent activity changed over time?

Database Schema 
The pipeline builds a relational SQLite database (patents.db) with 6 tables:
patents
inventors
companies
locations
patent_inventor
patent_company

SQL Queries Implemented
Top inventors    Who has the most patents all time?
Top companies    Which companies own the most patents?
Top countries    Which countries produce the most patents?
Trends over time  How many patents are granted each year?
Join Query       Patents combined with inventors and companies
CTE Query        Inventor productivity broken down by patent type
Ranking Query    Inventors ranked using SQL window functions

Visualizations generated
patents_per_year.png     Patent grant trend from 1976 to present
top_inventors.png        All-time top 10  inventors
top_companies.png        All-time top 10 companies by patent count
patent_types.png          Breakdown of patents by type (pie chart)
patents_per_decade.png     Total patent grants grouped by decade
top_inventors_recent.png    Top inventors since 2015
top_companies_recent.png    Top companies since 2015 

How to Reproduce This project
Requirements: 3GB Free disk space for raw data files, Internet connection for initial data download
1.clone the repository
2.install dependencies  pip install -r requirements.txt
3.Download raw data
4.clean data and build tables
5.Load into database
6.Run queries and generate reports
7.Generate visualizations

Data source
source USPTO PatentsView
URL https://data.uspto.gov/bulkdata/datasets/pvgpatdis

Files Downloaded
g_patent.tsv.zip
g_inventor_disambiguated.tsv.zip
g_assignee_disambiguated.tsv.zip
g_location_disambiguated.tsv.zip
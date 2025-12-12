# Load libraries
import requests
import json
import pandas as pd
import os
from datetime import datetime

# Ensure data folder exists
os.makedirs('data', exist_ok=True)

# File paths
MASTER_FILE = 'data/labor_data_master.csv'  # The master CSV
RAW_FILE = 'data/labor_data.csv'            # Optional raw CSV to include

# BLS API key
API_KEY = 'fe5517b08aec4f7da63b911b04a549aa'

# Series IDs to pull
series_ids = {
    'Total Nonfarm Employment': 'CES0000000001',
    'Unemployment Rate (SA)': 'LNS14000000',
    'Civilian Labor Force': 'LNS11000000',
    'Average Hourly Earnings Private': 'CES0500000003',
    'CPI-U': 'CUUR0000SA0'
}

# FUNCTIONS
def fetch_bls_data(series_ids, start_year=2010):
    """Fetch BLS data for all series"""
    end_year = datetime.now().year
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": list(series_ids.values()),
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationKey": API_KEY
    })
    response = requests.post(
        'https://api.bls.gov/publicAPI/v2/timeseries/data/', 
        data=data, 
        headers=headers
    )
    json_data = json.loads(response.text)
    
    all_data = []
    for series in json_data['Results']['series']:
        series_name = [k for k,v in series_ids.items() if v == series['seriesID']][0]
        for item in series['data']:
            year = int(item['year'])
            period = item['period']
            if 'M01' <= period <= 'M12':  # Monthly data only
                month = int(period[1:])
                date = pd.Timestamp(year=year, month=month, day=1)
                value = float(item['value'].replace(',', ''))
                all_data.append({'Date': date, 'Series': series_name, 'Value': value})
    
    df = pd.DataFrame(all_data)
    df = df.sort_values(['Series', 'Date']).reset_index(drop=True)
    return df

# LOAD MASTER FILE
if os.path.exists(MASTER_FILE):
    master_df = pd.read_csv(MASTER_FILE, parse_dates=['Date'])
else:
    master_df = pd.DataFrame(columns=['Date', 'Series', 'Value'])

# OPTIONAL: Merge raw CSV if it exists
if os.path.exists(RAW_FILE):
    raw_df = pd.read_csv(RAW_FILE, parse_dates=['Date'])
    master_df = pd.concat([master_df, raw_df]).drop_duplicates(subset=['Date', 'Series']).reset_index(drop=True)

# FETCH NEW DATA
# FETCH NEW DATA
if not master_df.empty:
    last_year_in_master = master_df['Date'].dt.year.max()
    start_year = last_year_in_master
else:
    start_year = 2000

new_data = fetch_bls_data(series_ids, start_year=start_year)

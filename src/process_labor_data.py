# Load libraries
import requests
import json
import pandas as pd
import os
from datetime import datetime

# SETUP
os.makedirs('data', exist_ok=True)
MASTER_FILE = 'data/labor_data_master.csv'
RAW_FILE = 'data/labor_data.csv' 
API_KEY = 'fe5517b08aec4f7da63b911b04a549aa'

series_ids = {
    'Total Nonfarm Employment': 'CES0000000001',
    'Unemployment Rate (SA)': 'LNS14000000',
    'Civilian Labor Force': 'LNS11000000',
    'Average Hourly Earnings Private': 'CES0500000003',
    'CPI-U': 'CUUR0000SA0'
}

# FUNCTIONS
def fetch_bls_data(series_ids, start_year=2000):
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
            if 'M01' <= period <= 'M12':
                month = int(period[1:])
                date = pd.Timestamp(year=year, month=month, day=1)
                value = float(item['value'].replace(',', ''))
                all_data.append({'Date': date, 'Series': series_name, 'Value': value})

    df = pd.DataFrame(all_data)
    df = df.sort_values(['Series', 'Date']).reset_index(drop=True)
    return df

# LOAD EXISTING MASTER
if os.path.exists(MASTER_FILE):
    master_df = pd.read_csv(MASTER_FILE, parse_dates=['Date'])
else:
    master_df = pd.DataFrame(columns=['Date', 'Series', 'Value'])

# Merge raw CSV if exists
if os.path.exists(RAW_FILE):
    raw_df = pd.read_csv(RAW_FILE, parse_dates=['Date'])
    master_df = pd.concat([master_df, raw_df]).drop_duplicates(subset=['Date', 'Series']).reset_index(drop=True)

# FETCH NEW DATA
new_data = fetch_bls_data(series_ids, start_year=2000)

# COMBINE DATA
combined_df = pd.concat(
    [master_df.dropna(axis=1, how='all'), new_data.dropna(axis=1, how='all')]
).drop_duplicates(subset=['Date', 'Series']).reset_index(drop=True)

# ENSURE VALUE IS NUMERIC
combined_df['Value'] = pd.to_numeric(combined_df['Value'], errors='coerce')

# CLEAN / TRANSFORM DATA
# 1. Round Average Hourly Earnings Private to 2 decimals
mask_earnings = combined_df['Series'] == 'Average Hourly Earnings Private'
combined_df.loc[mask_earnings, 'Value'] = combined_df.loc[mask_earnings, 'Value'].round(2)

# 2. Multiply Civilian Labor Force & Total Nonfarm Employment by 1,000
for s in ['Civilian Labor Force', 'Total Nonfarm Employment']:
    mask = combined_df['Series'] == s
    combined_df.loc[mask, 'Value'] = combined_df.loc[mask, 'Value'] * 1000

# 3. Unemployment Rate: 1 decimal, rename series
mask_unemp = combined_df['Series'] == 'Unemployment Rate (SA)'
combined_df.loc[mask_unemp, 'Value'] = combined_df.loc[mask_unemp, 'Value'].round(1)
combined_df.loc[mask_unemp, 'Series'] = 'Unemployment Rate (Seasonally Adjusted)'

# 4. CPI-U: rename series
mask_cpi = combined_df['Series'] == 'CPI-U'
combined_df.loc[mask_cpi, 'Series'] = 'Consumer Price Index - All Urban Consumers'

# SAVE MASTER FILE
combined_df.to_csv(MASTER_FILE, index=False)
print(f"Master file updated: {MASTER_FILE} ({len(combined_df)} rows)")

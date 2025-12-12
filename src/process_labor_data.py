# load libraries
import requests
import json
import pandas as pd
import os
from datetime import datetime

# SETUP
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # go up from src/
DATA_DIR = os.path.join(ROOT_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
MASTER_FILE = os.path.join(DATA_DIR, 'labor_data_master.csv')

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
    """Fetch BLS data for all series, handling 20-year API limit dynamically."""
    end_year = datetime.now().year
    max_years = 20
    all_data = []

    # Split the request into 20-year chunks
    for chunk_start in range(start_year, end_year + 1, max_years):
        chunk_end = min(chunk_start + max_years - 1, end_year)
        headers = {'Content-type': 'application/json'}
        data = json.dumps({
            "seriesid": list(series_ids.values()),
            "startyear": str(chunk_start),
            "endyear": str(chunk_end),
            "registrationKey": API_KEY
        })
        response = requests.post(
            'https://api.bls.gov/publicAPI/v2/timeseries/data/',
            data=data,
            headers=headers
        )
        json_data = json.loads(response.text)

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

# FETCH DATA (last 20 years dynamically)
combined_df = fetch_bls_data(series_ids, start_year=datetime.now().year - 20 + 1)

# CLEAN / TRANSFORM DATA

# Round Average Hourly Earnings Private to 2 decimals
mask_earnings = combined_df['Series'] == 'Average Hourly Earnings Private'
combined_df.loc[mask_earnings, 'Value'] = combined_df.loc[mask_earnings, 'Value'].round(2)

# Multiply Civilian Labor Force & Total Nonfarm Employment by 1,000
for s in ['Civilian Labor Force', 'Total Nonfarm Employment']:
    mask = combined_df['Series'] == s
    combined_df.loc[mask, 'Value'] = combined_df.loc[mask, 'Value'] * 1000

# Unemployment Rate: 1 decimal, rename series
mask_unemp = combined_df['Series'] == 'Unemployment Rate (SA)'
combined_df.loc[mask_unemp, 'Value'] = combined_df.loc[mask_unemp, 'Value'].round(1)
combined_df.loc[mask_unemp, 'Series'] = 'Unemployment Rate (Seasonally Adjusted)'

# CPI-U: rename series
mask_cpi = combined_df['Series'] == 'CPI-U'
combined_df.loc[mask_cpi, 'Series'] = 'Consumer Price Index - All Urban Consumers'

# SAVE MASTER FILE (overwrite)
combined_df.to_csv(MASTER_FILE, index=False)
print(f"Master file created and cleaned: {MASTER_FILE} ({len(combined_df)} rows)")

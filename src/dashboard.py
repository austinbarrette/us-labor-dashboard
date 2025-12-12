import streamlit as st
import pandas as pd

st.title("US Labor Market Dashboard")

# URL to your master dataset (raw GitHub file)
CSV_URL = "https://raw.githubusercontent.com/austinbarrette/us-labor-dashboard/main/data/labor_data_master.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL, parse_dates=['Date'])
    return df

df = load_data()

st.subheader("Preview of Data")
st.dataframe(df.head())

# Select a metric (Series)
series_list = sorted(df['Series'].unique())
selected_series = st.selectbox("Choose a labor metric:", series_list)

filtered = df[df['Series'] == selected_series]

st.line_chart(filtered.set_index("Date")["Value"])

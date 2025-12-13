import streamlit as st
import pandas as pd
import altair as alt

# CREATE DASHBOARD TITLE
st.title("US Labor Market Dashboard")

# URL to your master dataset
CSV_URL = "https://raw.githubusercontent.com/austinbarrette/us-labor-dashboard/main/data/labor_data_master.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL, parse_dates=['Date'])
    return df

df = load_data()

# SERIES SELECTION (SIDE-BY-SIDE)
st.markdown("### Choose U.S. Labor Metrics to Visualize:")

# Create two columns for filtering
col1, col2 = st.columns(2)

with col1:
    primary_series = st.radio("Primary Metric", sorted(df['Series'].unique()), key="primary")
with col2:
    compare_options = ["None"] + [s for s in sorted(df['Series'].unique()) if s != primary_series]
    compare_series = st.radio("Compare Metric (optional)", compare_options, key="compare")

# FILTER DATA FILTERS (to prevent errors from occuring with choosing same dataset when comparing)
plot_df = df[df['Series'] == primary_series][["Date", "Value"]].rename(columns={"Value": primary_series})
plot_df = plot_df.set_index("Date")

if compare_series != "None":
    compare_df = df[df['Series'] == compare_series][["Date", "Value"]].rename(columns={"Value": compare_series})
    compare_df = compare_df.set_index("Date")
    plot_df = plot_df.join(compare_df, how="outer")

# AXIS FORMATTING LOGIC (MILLIONS)
million_series = [
    "Total Nonfarm Employment",
    "Civilian Labor Force"
]

plot_df_chart = plot_df.copy()

if primary_series in million_series:
    plot_df_chart[primary_series] = plot_df_chart[primary_series] / 1_000_000

if compare_series in million_series:
    plot_df_chart[compare_series] = plot_df_chart[compare_series] / 1_000_000

# LINE CHART TITLE WITH HTML
# Set consistent font size for all lines
font_size = "24px"

if compare_series == "None":
    title_html = f"<div style='font-size:{font_size}; font-weight:bold;'>{primary_series} over Time</div>"
else:
    title_html = (
        f"<div style='font-size:{font_size}; font-weight:bold;'>{primary_series}</div>"
        f"<div style='font-size:{font_size}; font-weight:bold;'>vs. {compare_series} over Time</div>"
    )

st.markdown(title_html, unsafe_allow_html=True)

# Plot lines with optional secondary axis
if compare_series == "None":
    lines = alt.Chart(plot_df_chart).mark_line(color="#1f77b4").encode(
        x='Date:T',
        y=alt.Y(
            f'{primary_series}:Q',
            title=None,
            axis=alt.Axis(format="~s") if primary_series in million_series else alt.Axis()
        ),
        tooltip=['Date:T', f'{primary_series}:Q']
    )
else:
    base = alt.Chart(plot_df_chart).encode(x='Date:T')

    line1 = base.mark_line(color="#1f77b4").encode(
        y=alt.Y(
            f'{primary_series}:Q',
            title=primary_series,
            axis=alt.Axis(format="~s") if primary_series in million_series else alt.Axis()
        ),
        tooltip=['Date:T', f'{primary_series}:Q']
    )

    line2 = base.mark_line(color="#ff7f0e").encode(
        y=alt.Y(
            f'{compare_series}:Q',
            title=compare_series,
            axis=alt.Axis(format="~s") if compare_series in million_series else alt.Axis()
        ),
        tooltip=['Date:T', f'{compare_series}:Q']
    )

    lines = alt.layer(line1, line2).resolve_scale(y='independent')

st.altair_chart(lines, use_container_width=True)

# DYNAMIC DATA TABLE
table_df = plot_df.reset_index()
# Sort newest to oldest as default
table_df = table_df.sort_values("Date", ascending=False)

# Show all data, no title, dynamic column names
st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    height=400  # set height for scrollable table
)

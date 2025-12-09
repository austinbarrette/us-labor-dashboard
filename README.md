# U.S. Labor Statistics Dashboard

## Overview
The U.S. Labor Statistics Dashboard is a Streamlit-based application that collects, processes, and visualizes major indicators of the U.S. labor market using data from the Bureau of Labor Statistics (BLS) Public Data API. The dashboard automatically updates following each new release through a GitHub Actions workflow that appends monthly records, creating an automated and reproducible analytical platform.

## Key Features
- Visualizes trends in total nonfarm employment, unemployment rate (seasonally adjusted), civilian labor force, average hourly earnings of private employees, and the Consumer Price Index (CPI-U).
- Interactive line charts and summary metrics to track historical and current labor market trends.
- Automated data collection and updating via GitHub Actions to ensure the dashboard always reflects the latest BLS data.

## Data Sources
Data is retrieved from the [Bureau of Labor Statistics (BLS) Public Data API](https://www.bls.gov/developers/home.htm) in JSON format. The dashboard focuses on core labor market indicators to provide insight into employment, wages, and inflation.

## Technology Stack
- **Python** – data retrieval, cleaning, and processing
- **Pandas & NumPy** – data wrangling and time series construction
- **Streamlit** – interactive dashboard development and deployment
- **GitHub Actions** – automated monthly data collection and dashboard updates
- **Altair / Plotly** – data visualization (line charts, summary metrics)

## Project Structure

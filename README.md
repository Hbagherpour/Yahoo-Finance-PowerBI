# Yahoo Finance Data Pull for Power BI
This repository contains a Python script to fetch global index data from Yahoo Finance and save it as a CSV file for use in Power BI dashboards.

## Usage
1. Install required packages: `pip install yfinance pandas`
2. Run the script: `python global_indices_data_pull.py`
3. Import the generated CSV into Power BI.

## Notes
- The script fetches data from 2024-01-01 to the current date.
- Output is saved to `X:\your working directory\Yahoo-Finance-PowerBI-project\global_indices_historical.csv`.
import yfinance as yf
import pandas as pd
import logging
import os
from datetime import datetime, date
import math

# Set up logging
logging.basicConfig(
    filename='global_indices_data_pull.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define the indices and their Yahoo Finance ticker symbols along with currencies
indices = {
    'S&P 500': {'ticker': '^GSPC', 'currency': 'USD'},
    'FTSE 100': {'ticker': '^FTSE', 'currency': 'GBP'},
    'DAX': {'ticker': '^GDAXI', 'currency': 'EUR'},
    'CAC 40': {'ticker': '^FCHI', 'currency': 'EUR'},
    'Nikkei 225': {'ticker': '^N225', 'currency': 'JPY'},
    'Hang Seng': {'ticker': '^HSI', 'currency': 'HKD'},
    'Nasdaq 100': {'ticker': '^NDX', 'currency': 'USD'},
    'STOXX 50': {'ticker': '^STOXX50E', 'currency': 'EUR'},
    'S&P/ASX 20': {'ticker': '^AXJO', 'currency': 'AUD'},  # Note: Using S&P/ASX 200 as proxy
    'CSI 300': {'ticker': '000300.SS', 'currency': 'CNY'},
    'NSE NIFTY 50': {'ticker': '^NSEI', 'currency': 'INR'},
    'Índice Bovespa': {'ticker': '^BVSP', 'currency': 'BRL'},
    'Tadawul All Shares Index': {'ticker': '^TASI.SR', 'currency': 'SAR'}
}

def fetch_index_data(ticker, start_date, end_date):
    """Fetch historical data for a given index ticker."""
    try:
        # Ensure dates are in the correct format (date only, no time)
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        
        # Download historical data
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if df.empty:
            logging.warning(f"No data retrieved for {ticker} between {start_date} and {end_date}")
            return None
        return df
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {str(e)}")
        return None

def main():
    # Define output directory
    output_dir = r'X:\your working directory\Yahoo-Finance-PowerBI-project\global_indices_historical.csv'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")
    
    # Print current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"CSV files will be saved to: {output_dir}")
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"CSV files will be saved to: {output_dir}")
    
    # Define file paths upfront
    historical_file = os.path.join(output_dir, 'global_indices_historical.csv')
    
    # Define fixed start date and dynamic end date (today)
    start_date = datetime(2024, 1, 1)
    end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)  # Use today's date, strip time
    
    # Initialize list to store all rows
    all_data = []
    
    # Fetch data for each index and collect rows
    for index_name, info in indices.items():
        ticker = info['ticker']
        currency = info['currency']
        logging.info(f"Fetching data for {index_name} ({ticker})")
        
        # Fetch historical data
        df = fetch_index_data(ticker, start_date, end_date)
        if df is not None:
            # Add each row with Index name and currency units
            for date, row in df.iterrows():
                # Check for NaN and convert to scalar values
                open_value = float(row['Open']) if not math.isnan(row['Open']) else 0.0
                high_value = float(row['High']) if not math.isnan(row['High']) else 0.0
                low_value = float(row['Low']) if not math.isnan(row['Low']) else 0.0
                close_value = float(row['Close']) if not math.isnan(row['Close']) else 0.0
                volume_value = int(row['Volume']) if not math.isnan(row['Volume']) else 0
                
                all_data.append({
                    'Date': date,
                    'Index': index_name,
                    'Open': f"{open_value:.2f} {currency}",
                    'High': f"{high_value:.2f} {currency}",
                    'Low': f"{low_value:.2f} {currency}",
                    'Close': f"{close_value:.2f} {currency}",
                    'Volume': volume_value
                })
        else:
            logging.warning(f"Skipping {index_name} due to missing historical data")
    
    # Create DataFrame from all data and sort by Date
    if all_data:
        combined_historical = pd.DataFrame(all_data)
        # Sort by Date to ensure chronological order
        combined_historical = combined_historical.sort_values('Date')
        
        # Debug: Print the first few rows to verify structure
        print("Debug: First 5 rows of combined_historical:")
        print(combined_historical.head().to_string())
        
        # Save historical data to CSV
        combined_historical.to_csv(historical_file, index=False)
        logging.info(f"Historical data saved to {historical_file}")
    else:
        logging.error("No historical data was fetched for any index")
    
    # Verify file creation
    if os.path.exists(historical_file):
        logging.info(f"File {historical_file} created successfully with size {os.path.getsize(historical_file)} bytes")
        print(f"File created: {historical_file}")
    else:
        logging.error(f"File {historical_file} was not created")
        print(f"Warning: File {historical_file} was not created")

if __name__ == "__main__":
    main()
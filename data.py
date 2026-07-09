import yfinance as yf
import pandas as pd
import logging
import os
from datetime import datetime
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

# Define FX rate tickers (currency to USD, inverse will be used for conversion)
fx_tickers = {
    'USD': None,  # USD to USD is 1.0
    'GBP': 'GBPUSD=X',
    'EUR': 'EURUSD=X',
    'JPY': 'JPYUSD=X',
    'HKD': 'HKDUSD=X',
    'AUD': 'AUDUSD=X',
    'CNY': 'CNYUSD=X',
    'INR': 'INRUSD=X',
    'BRL': 'BRLUSD=X',
    'SAR': 'SARUSD=X'
}

def fetch_index_data(ticker, start_date, end_date):
    """Fetch historical data for a given index ticker."""
    try:
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if df.empty:
            logging.warning(f"No data retrieved for {ticker} between {start_date} and {end_date}")
            return None
        return df
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {str(e)}")
        return None

def fetch_fx_data(ticker, start_date, end_date):
    """Fetch FX rate data for a given currency pair."""
    try:
        if ticker is None:
            # Return a DataFrame with constant 1.0 for USD
            dates = pd.date_range(start=start_date, end=end_date)
            return pd.DataFrame({'Close': [1.0] * len(dates)}, index=dates)
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if df.empty:
            logging.warning(f"No FX data retrieved for {ticker} between {start_date} and {end_date}")
            return None
        # Use the 'Close' price as the FX rate (USD per foreign currency)
        return df[['Close']]
    except Exception as e:
        logging.error(f"Error fetching FX data for {ticker}: {str(e)}")
        return None

def main():
    # Define output directory (corrected to be a directory, not a file path)
    output_dir = r'C:\Hossein\Python'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")
    
    # Define file path
    historical_file = os.path.join(output_dir, 'global_indices_historical.csv')
    
    # Print current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"CSV files will be saved to: {output_dir}")
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"CSV files will be saved to: {output_dir}")
    
    # Define fixed start date and dynamic end date (today)
    start_date = datetime(2024, 1, 1)
    end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)  # Use today's date, strip time
    
    # Fetch FX data for all currencies
    fx_data = {}
    for currency, fx_ticker in fx_tickers.items():
        fx_df = fetch_fx_data(fx_ticker, start_date, end_date)
        if fx_df is not None:
            fx_data[currency] = fx_df.rename(columns={'Close': f'FX_{currency}_to_USD'})

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
                # Extract scalar values from Series
                open_value = float(row['Open'].item()) if not math.isnan(row['Open'].item()) else 0.0
                high_value = float(row['High'].item()) if not math.isnan(row['High'].item()) else 0.0
                low_value = float(row['Low'].item()) if not math.isnan(row['Low'].item()) else 0.0
                close_value = float(row['Close'].item()) if not math.isnan(row['Close'].item()) else 0.0
                volume_value = int(row['Volume'].item()) if not math.isnan(row['Volume'].item()) else 0
                
                # Get FX rate for the currency (inverse for foreign currency to USD)
                fx_series = fx_data[currency].loc[date] if date in fx_data[currency].index else pd.Series([1.0], index=[f'FX_{currency}_to_USD'])
                fx_rate = fx_series[f'FX_{currency}_to_USD'].item()
                if fx_rate == 0:  # Check scalar value
                    fx_rate = 1.0  # Avoid division by zero
                usd_conversion_rate = 1.0 / fx_rate if currency != 'USD' else 1.0
                
                # Convert to USD
                open_usd = open_value * usd_conversion_rate
                high_usd = high_value * usd_conversion_rate
                low_usd = low_value * usd_conversion_rate
                close_usd = close_value * usd_conversion_rate
                
                all_data.append({
                    'Date': date,
                    'Index': index_name,
                    'Open': f"{open_value:.2f} {currency}",
                    'High': f"{high_value:.2f} {currency}",
                    'Low': f"{low_value:.2f} {currency}",
                    'Close': f"{close_value:.2f} {currency}",
                    'Volume': volume_value,
                    'Open_USD': f"{open_usd:.2f} USD",
                    'High_USD': f"{high_usd:.2f} USD",
                    'Low_USD': f"{low_usd:.2f} USD",
                    'Close_USD': f"{close_usd:.2f} USD"
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
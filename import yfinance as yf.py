import yfinance as yf
df = yf.download('^GSPC', start='2024-05-11', end='2025-05-11')
print(df)
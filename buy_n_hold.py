import ccxt
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Initialize Binance client
exchange = ccxt.binance()

# Define symbols and leverage
# symbols = ['BTC', 'ETH', 'SOL', 'NEAR', 'TIA', 'MANTA', 'SEI', 'TAO', 'IOTX', 'GMX']
symbols = ['BTC', 'ETC', 'ICX', 'LINK', 'NULS', 'ONT', 'TRX', 'LTC', 'NEO', 'VET']
leverage = 5  # Example leverage

# Define the time period
start_date = '2021-01-01T00:00:00Z'
end_date = '2021-05-31T23:59:59Z'

# Total portfolio value and allocation per symbol
total_portfolio_value = 500  # €500
allocation_per_symbol = total_portfolio_value * 0.10  # 10% of the portfolio

# Initialize total returns
total_return_without_leverage = 0
total_return_with_leverage = 0

# Initialize lists to store daily portfolio values
daily_values_without_leverage = []
daily_values_with_leverage = []

# Initialize a list to store timestamps
timestamps = []

# Function to fetch klines and perform analysis
def fetch_and_analyze(symbol):
    global total_return_without_leverage, total_return_with_leverage
    
    # Initialize an empty DataFrame to store all data
    all_data = pd.DataFrame()

    # Start date for fetching data
    current_date = exchange.parse8601(start_date)

    # Fetch data month by month
    while current_date < exchange.parse8601(end_date):
        # Fetch klines for a month
        ohlcv = exchange.fetch_ohlcv(symbol + '/USDT', timeframe='1d', since=current_date, limit=30)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Append to all_data
        all_data = pd.concat([all_data, df])

        # Convert current_date to datetime, add 30 days, and convert back to timestamp
        current_date = pd.to_datetime(current_date, unit='ms') + timedelta(days=30)
        current_date = int(current_date.timestamp() * 1000)  # Convert back to milliseconds

    # Store timestamps for plotting
    if not timestamps:
        timestamps.extend(all_data['timestamp'])

    # Calculate buy and hold return
    initial_price = all_data['close'].iloc[0]
    daily_returns = all_data['close'].pct_change().fillna(0)
    
    # Calculate daily portfolio values
    daily_value_without_leverage = allocation_per_symbol * (1 + daily_returns).cumprod()
    daily_value_with_leverage = allocation_per_symbol * (1 + daily_returns * leverage).cumprod()
    
    # Append daily values to the lists
    daily_values_without_leverage.append(daily_value_without_leverage)
    daily_values_with_leverage.append(daily_value_with_leverage)

# Run analysis for each symbol
for symbol in symbols:
    fetch_and_analyze(symbol)

# Sum daily values across all symbols
total_daily_values_without_leverage = sum(daily_values_without_leverage)
total_daily_values_with_leverage = sum(daily_values_with_leverage)

# Plot the results
plt.figure(figsize=(14, 7))
plt.plot(timestamps, total_daily_values_without_leverage, label='Without Leverage')
plt.plot(timestamps, total_daily_values_with_leverage, label='With Leverage')
plt.title('Portfolio Evolution')
plt.xlabel('Date')
plt.ylabel('Portfolio Value (€)')
plt.legend()
plt.grid(True)
plt.show()

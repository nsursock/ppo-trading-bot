import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import argparse

def plot_equity_curve_with_drawdown(df):
    # Calculate cumulative returns and drawdown
    df['Cumulative Return'] = (1 + df['return']).cumprod()
    df['Peak'] = df['Cumulative Return'].cummax()
    df['Drawdown'] = df['Cumulative Return'] - df['Peak']
    
    # Plot equity curve
    plt.figure(figsize=(14, 7))
    plt.plot(df['close_time'], df['Cumulative Return'], label='Equity Curve')
    plt.fill_between(df['close_time'], df['Cumulative Return'], df['Peak'], color='red', alpha=0.3, label='Drawdown')
    plt.title('Equity Curve with Drawdown')
    plt.xlabel('Close Time')
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.show()

def plot_daily_returns_heatmap(df):
    # Extract date and calculate daily returns
    df['Date'] = pd.to_datetime(df['close_time']).dt.date
    
    # Check if 'symbol' column exists in the original DataFrame
    if 'symbol' in df.columns:
        # Calculate daily returns with symbol
        daily_returns = df.groupby(['Date', 'symbol'])['return'].sum().reset_index()
        
        # Pivot data for heatmap
        returns_pivot = daily_returns.pivot(index='Date', columns='symbol', values='return')
        
        # Plot heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(returns_pivot, cmap='coolwarm', center=0)
        plt.title('Daily Returns Heatmap')
        plt.xlabel('Symbol')
        plt.ylabel('Date')
        plt.show()
    else:
        print("The 'symbol' column is missing from the data. Cannot plot heatmap.")

def plot_trade_outcomes_pie_chart(df):
    # Count trade outcomes
    outcome_counts = df['exit_reason'].value_counts()
    
    # Plot pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(outcome_counts, labels=outcome_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title('Trade Outcomes')
    plt.show()

def plot_drawdown_chart(df):
    df['Cumulative Return'] = (1 + df['return']).cumprod()
    df['Peak'] = df['Cumulative Return'].cummax()
    df['Drawdown'] = df['Cumulative Return'] - df['Peak']
    
    plt.figure(figsize=(14, 7))
    plt.plot(df['close_time'], df['Drawdown'], label='Drawdown', color='red')
    plt.fill_between(df['close_time'], df['Drawdown'], color='red', alpha=0.3)
    plt.title('Drawdown Over Time')
    plt.xlabel('Close Time')
    plt.ylabel('Drawdown')
    plt.legend()
    plt.show()

def plot_win_rate_by_asset(df):
    df['win'] = df['return'] > 0
    win_rate = df.groupby('symbol')['win'].mean()
    
    plt.figure(figsize=(10, 6))
    win_rate.plot(kind='bar', color='skyblue')
    plt.title('Win Rate by Asset')
    plt.xlabel('Asset')
    plt.ylabel('Win Rate')
    plt.xticks(rotation=45)
    plt.show()

def plot_pnl_distribution(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(df['return'], bins=50, kde=True, color='purple')
    plt.title('Profit and Loss Distribution')
    plt.xlabel('Return')
    plt.ylabel('Frequency')
    plt.show()

def compute_risk(df):
    # Calculate risk as the standard deviation of returns
    df['risk'] = df['return'].rolling(window=20).std()  # 20-period rolling standard deviation
    df['risk'].fillna(method='bfill', inplace=True)  # Backfill to handle NaN values at the start

def plot_risk_reward_distribution(df):
    # Compute risk if not already present
    if 'risk' not in df.columns:
        compute_risk(df)
    
    df['risk_reward_ratio'] = df['return'] / df['risk']
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='symbol', y='risk_reward_ratio', data=df)
    plt.title('Risk to Reward Distribution by Asset')
    plt.xlabel('Asset')
    plt.ylabel('Risk/Reward Ratio')
    plt.xticks(rotation=45)
    plt.show()

def plot_cumulative_pnl_by_asset(df):
    df['Cumulative PnL'] = df.groupby('symbol')['return'].cumsum()
    plt.figure(figsize=(12, 8))
    for symbol, group in df.groupby('symbol'):
        plt.plot(group['close_time'], group['Cumulative PnL'], label=symbol)
    plt.title('Cumulative PnL by Asset')
    plt.xlabel('Close Time')
    plt.ylabel('Cumulative PnL')
    plt.legend()
    plt.show()

def plot_trade_timing_heatmap(df):
    df['Hour'] = pd.to_datetime(df['close_time']).dt.hour
    timing_pivot = df.pivot_table(index='Hour', columns='symbol', values='return', aggfunc='sum')
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(timing_pivot, cmap='coolwarm', center=0)
    plt.title('Trade Timing Heatmap')
    plt.xlabel('Asset')
    plt.ylabel('Hour of Day')
    plt.show()

def visualize_graphs(history_file):
    # Load history from CSV
    df = pd.read_csv(history_file)
    
    # Visualize data
    plot_equity_curve_with_drawdown(df)
    plot_daily_returns_heatmap(df)
    plot_trade_outcomes_pie_chart(df)
    plot_drawdown_chart(df)
    plot_win_rate_by_asset(df)
    plot_pnl_distribution(df)
    plot_risk_reward_distribution(df)
    plot_cumulative_pnl_by_asset(df)
    plot_trade_timing_heatmap(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize trading bot performance.')
    parser.add_argument('-f', '--history_file', type=str, help='Path to the history CSV file')
    args = parser.parse_args()
    
    visualize_graphs(args.history_file)
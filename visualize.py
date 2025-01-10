import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import argparse



def plot_performance_metrics(df):
    # Create a figure with two subplots
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(14, 10))
    
    # Calculate cumulative returns
    df['Cumulative Returns'] = (1 + df['return']).cumprod()
    
    # Plot Equity Curve on the first subplot
    axes[0].plot(df['close_time'], df['Cumulative Returns'], label='Equity Curve')
    
    # Calculate drawdowns
    df['Drawdown'] = df['Cumulative Returns'] / df['Cumulative Returns'].cummax() - 1
    axes[0].fill_between(df['close_time'], df['Cumulative Returns'], where=(df['Drawdown'] < 0), color='red', alpha=0.3, label='Drawdown')
    
    axes[0].set_title('Equity Curve with Drawdowns')
    axes[0].set_xlabel('Close Time')
    axes[0].set_ylabel('Portfolio Value')
    axes[0].legend()
    
    # Calculate daily returns
    df['Daily Returns'] = df['return']
    
    # Plot Daily Returns on the second subplot
    sns.barplot(x='close_time', y='Daily Returns', data=df, ax=axes[1])
    axes[1].set_title('Daily Returns')
    axes[1].set_xlabel('Close Time')
    axes[1].set_ylabel('Returns')
    axes[1].tick_params(axis='x', rotation=45)
    
    # Adjust layout
    plt.tight_layout()
    plt.show()
    
def plot_risk_analysis(df):
    # Create a figure with three subplots
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 10))
    
    # Calculate cumulative returns and drawdowns
    df['Cumulative Returns'] = (1 + df['return']).cumprod()
    df['Drawdown'] = df['Cumulative Returns'] / df['Cumulative Returns'].cummax() - 1
    
    # Plot Drawdown Chart
    axes[0].plot(df['close_time'], df['Drawdown'], label='Drawdown', color='blue')
    axes[0].fill_between(df['close_time'], df['Drawdown'], color='red', alpha=0.3, where=(df['Drawdown'] < -0.1), label='Severe Drawdown')
    axes[0].set_title('Drawdown Chart')
    axes[0].set_xlabel('Close Time')
    axes[0].set_ylabel('Drawdown')
    axes[0].legend()
    
    # Calculate max drawdown for each trade
    df['Max Drawdown'] = df['Drawdown'].cummin()
    
    # Plot Max Drawdown vs. Time
    axes[1].scatter(df['close_time'], df['Max Drawdown'], label='Max Drawdown', color='purple')
    axes[1].set_title('Max Drawdown vs. Time')
    axes[1].set_xlabel('Close Time')
    axes[1].set_ylabel('Max Drawdown')
    axes[1].legend()
    
    # Pivot the data for heatmap
    leverage_pivot = df.pivot_table(index='close_time', columns='symbol', values='leverage', fill_value=0)
    
    # Plot Leverage Heatmap
    sns.heatmap(leverage_pivot, cmap='coolwarm', ax=axes[2], cbar_kws={'label': 'Leverage'})
    axes[2].set_title('Leverage Heatmap')
    axes[2].set_xlabel('Symbol')
    axes[2].set_ylabel('Close Time')
    axes[2].tick_params(axis='x', rotation=45)
    axes[2].tick_params(axis='y', rotation=0)
    
    # Adjust layout
    plt.tight_layout()
    plt.show()

def plot_trade_statistics(df):
    # Convert 'close_time' to datetime if not already
    df['close_time'] = pd.to_datetime(df['close_time'])
    
    # Calculate win rate by asset
    win_rate_by_asset = df.groupby('symbol')['return'].apply(lambda x: (x > 0).mean())
    
    # Calculate trade outcomes
    trade_outcomes = df['exit_reason'].value_counts()
    
    # Create a figure with four subplots
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 10))
    
    # Plot Win Rate by Asset
    sns.barplot(x=win_rate_by_asset.index, y=win_rate_by_asset.values, ax=axes[0, 0])
    axes[0, 0].set_title('Win Rate by Asset')
    axes[0, 0].set_xlabel('Asset')
    axes[0, 0].set_ylabel('Win Rate')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Plot Profit and Loss Distribution
    sns.histplot(df['return'], bins=50, kde=True, ax=axes[0, 1])
    axes[0, 1].set_title('Profit and Loss Distribution')
    axes[0, 1].set_xlabel('Return')
    axes[0, 1].set_ylabel('Frequency')
    
    # Plot Trade Outcomes
    axes[1, 0].pie(trade_outcomes, labels=trade_outcomes.index, autopct='%1.1f%%', startangle=140)
    axes[1, 0].set_title('Trade Outcomes')
    
    # Plot Duration vs. Profit Scatterplot
    df['duration'] = (pd.to_datetime(df['close_time']) - pd.to_datetime(df['open_time'])).dt.total_seconds()
    axes[1, 1].scatter(df['duration'], df['return'], alpha=0.5)
    axes[1, 1].set_title('Duration vs. Profit Scatterplot')
    axes[1, 1].set_xlabel('Duration (seconds)')
    axes[1, 1].set_ylabel('Profit')
    
    # Adjust layout
    plt.tight_layout()
    plt.show()

def plot_risk_reward_analysis(df):
    # Calculate risk/reward ratio
    df['risk_reward_ratio'] = df['return'] / df['borrowing_fee']  # Example calculation, adjust as needed
    
    # Create a figure with two subplots
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))
    
    # Plot Risk to Reward Distribution
    sns.boxplot(x='symbol', y='risk_reward_ratio', data=df, ax=axes[0])
    axes[0].set_title('Risk to Reward Distribution')
    axes[0].set_xlabel('Asset')
    axes[0].set_ylabel('Risk/Reward Ratio')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Calculate Sortino and Sharpe ratios over time
    df['sortino_ratio'] = df['return'].rolling(window=30).apply(lambda x: x.mean() / x[x < 0].std(), raw=False)
    df['sharpe_ratio'] = df['return'].rolling(window=30).mean() / df['return'].rolling(window=30).std()
    
    # Plot Sortino/Sharpe Ratio Comparison
    axes[1].plot(df['close_time'], df['sortino_ratio'], label='Sortino Ratio', color='blue')
    axes[1].plot(df['close_time'], df['sharpe_ratio'], label='Sharpe Ratio', color='green')
    axes[1].set_title('Sortino/Sharpe Ratio Comparison')
    axes[1].set_xlabel('Close Time')
    axes[1].set_ylabel('Ratio')
    axes[1].legend()
    axes[1].tick_params(axis='x', rotation=45)
    
    # Adjust layout
    plt.tight_layout()
    plt.show()

def plot_asset_level_performance(df):
    # Convert 'close_time' to datetime if not already
    df['close_time'] = pd.to_datetime(df['close_time'])
    
    # Calculate cumulative PnL by asset
    cumulative_pnl = df.groupby(['close_time', 'symbol'])['pnl'].sum().unstack().cumsum()
    
    # Create a figure with three subplots
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))
    
    # Plot Cumulative PnL by Asset using line plot
    cumulative_pnl.plot(ax=axes[0])
    axes[0].set_title('Cumulative PnL by Asset')
    axes[0].set_xlabel('Close Time')
    axes[0].set_ylabel('Cumulative PnL')
    axes[0].legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    # Prepare data for Heatmap of Returns by Asset and Time Period
    df['month'] = df['close_time'].dt.to_period('M')
    returns_pivot = df.pivot_table(index='symbol', columns='month', values='return', aggfunc='sum', fill_value=0)
    
    # Plot Heatmap of Returns by Asset and Time Period
    sns.heatmap(returns_pivot, cmap='coolwarm', ax=axes[1], cbar_kws={'label': 'Returns'})
    axes[1].set_title('Heatmap of Returns by Asset and Time Period')
    axes[1].set_xlabel('Month')
    axes[1].set_ylabel('Asset')
    axes[1].tick_params(axis='x', rotation=45)
    
    # Plot Leverage and Profit Correlation
    axes[2].scatter(df['leverage'], df['pnl'], alpha=0.5)
    axes[2].set_title('Leverage and Profit Correlation')
    axes[2].set_xlabel('Leverage')
    axes[2].set_ylabel('Profit/Loss')
    
    # Adjust layout
    plt.tight_layout()
    plt.show()

def plot_decision_metrics(df):
    # Create a figure with three subplots
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))
    
    # Action Breakdown
    action_counts = df['type'].value_counts()
    sns.barplot(x=action_counts.index, y=action_counts.values, ax=axes[0])
    axes[0].set_title('Action Breakdown')
    axes[0].set_xlabel('Action')
    axes[0].set_ylabel('Frequency')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Stop Loss and Take Profit Hits
    sl_tp_hits = df[['sl_price', 'tp_price']].melt(var_name='Type', value_name='Price')
    sns.histplot(sl_tp_hits, x='Price', hue='Type', multiple='stack', ax=axes[1])
    axes[1].set_title('Stop Loss and Take Profit Hits')
    axes[1].set_xlabel('Price Level')
    axes[1].set_ylabel('Frequency')
    
    # Conditions at Entry vs. Profit
    axes[2].scatter(df['leverage'], df['pnl'], alpha=0.5, label='Leverage vs. PnL')
    axes[2].scatter(df['collateral'], df['pnl'], alpha=0.5, label='Collateral vs. PnL', color='orange')
    axes[2].set_title('Conditions at Entry vs. Profit')
    axes[2].set_xlabel('Entry Condition')
    axes[2].set_ylabel('Profit/Loss')
    axes[2].legend()
    
    # Adjust layout
    plt.tight_layout()
    plt.show()

def plot_behavioral_patterns(df):
    # Convert 'open_time' and 'close_time' to datetime if not already
    df['open_time'] = pd.to_datetime(df['open_time'])
    df['close_time'] = pd.to_datetime(df['close_time'])
    
    # Extract hour from 'open_time' for trade timing analysis
    df['hour'] = df['open_time'].dt.hour
    
    # Create a pivot table for the heatmap
    timing_pivot = df.pivot_table(index='hour', columns='symbol', values='pnl', aggfunc='sum', fill_value=0)
    
    # Create a figure with two subplots
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
    
    # Plot Trade Timing Heatmap
    sns.heatmap(timing_pivot, cmap='coolwarm', ax=axes[0], cbar_kws={'label': 'Profit/Loss'})
    axes[0].set_title('Trade Timing Heatmap')
    axes[0].set_xlabel('Asset')
    axes[0].set_ylabel('Hour of Day')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Calculate trade duration in hours
    df['duration_hours'] = (df['close_time'] - df['open_time']).dt.total_seconds() / 3600
    
    # Plot Duration Analysis
    sns.histplot(df['duration_hours'], bins=50, ax=axes[1], kde=True)
    axes[1].set_title('Trade Duration Analysis')
    axes[1].set_xlabel('Duration (hours)')
    axes[1].set_ylabel('Frequency')
    
    # Highlight successful short-term vs. long-term trades
    short_term_threshold = 24  # Example threshold for short-term trades
    long_term_threshold = 168  # Example threshold for long-term trades (1 week)
    short_term_success = df[(df['duration_hours'] <= short_term_threshold) & (df['pnl'] > 0)]
    long_term_success = df[(df['duration_hours'] > long_term_threshold) & (df['pnl'] > 0)]
    
    axes[1].hist(short_term_success['duration_hours'], bins=50, alpha=0.5, label='Short-term Success', color='green')
    axes[1].hist(long_term_success['duration_hours'], bins=50, alpha=0.5, label='Long-term Success', color='blue')
    axes[1].legend()
    
    # Adjust layout
    plt.tight_layout()
    plt.show()

def visualize_graphs(history_file):
    # Load history from CSV
    df = pd.read_csv(history_file)
    
    plot_performance_metrics(df)
    
    plot_risk_analysis(df)
    
    plot_trade_statistics(df)
    
    plot_risk_reward_analysis(df)
    
    plot_asset_level_performance(df)
    
    plot_decision_metrics(df)
    
    plot_behavioral_patterns(df)
    
    # Optionally, you can add weekly/monthly returns using resampling
    # df['close_time'] = pd.to_datetime(df['close_time'])
    # weekly_returns = df.resample('W', on='close_time')['return'].sum()
    # monthly_returns = df.resample('M', on='close_time')['return'].sum()
    # Plot these similarly using sns.barplot or sns.heatmap

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize trading bot performance.')
    parser.add_argument('-f', '--history_file', type=str, help='Path to the history CSV file')
    args = parser.parse_args()
    
    visualize_graphs(args.history_file)
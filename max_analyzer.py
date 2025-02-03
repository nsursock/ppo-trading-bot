import argparse
import pandas as pd
import matplotlib.pyplot as plt

# cols: episode,open_time,close_time,symbol,type,entry_price,exit_price,position_size,leverage,collateral,sl_price,tp_price,liq_price,max_price,exit_reason,pnl,return,borrowing_fee,balance,risk_per_trade

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process a CSV file.')
    parser.add_argument('-c', '--csv_file', type=str, help='Path to the CSV file')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Read the CSV file
    df = pd.read_csv(args.csv_file)
    
    # Print the DataFrame to verify
    print(df)

    # Group by episode and calculate stats
    grouped = df.groupby('episode')

    # Prepare data for plotting
    episodes = []
    max_frequencies = []
    longest_liq_streaks = []
    avg_durations_max = []
    time_to_balances = []

    for episode, group in grouped:
        # Calculate the frequency of exit reason "max" as a percentage for each episode
        total_trades = len(group)
        max_frequency_percentage = (group['exit_reason'].value_counts().get('max', 0) / total_trades) * 100
        print(f"Episode {episode}: Frequency of exit reason 'max' as a percentage: {max_frequency_percentage:.2f}%")

        # Calculate the longest streak of exit reason "liq" for each episode
        longest_liq_streak = (group['exit_reason'] == 'liq').astype(int).groupby((group['exit_reason'] != 'liq').cumsum()).sum().max()
        print(f"Episode {episode}: Longest streak of exit reason 'liq': {longest_liq_streak}")

        # Calculate the average duration of trades that hit "max"
        group['open_time'] = pd.to_datetime(group['open_time'])
        group['close_time'] = pd.to_datetime(group['close_time'])
        group['trade_duration'] = (group['close_time'] - group['open_time']).dt.total_seconds() / 3600  # duration in hours

        max_trades = group[group['exit_reason'] == 'max']
        if not max_trades.empty:
            avg_duration_max = max_trades['trade_duration'].mean()
            print(f"Episode {episode}: Average duration of trades that hit 'max': {avg_duration_max:.2f} hours")
        else:
            print(f"Episode {episode}: No trades hit 'max'.")

        episodes.append(episode)
        max_frequencies.append(max_frequency_percentage)
        longest_liq_streaks.append(longest_liq_streak)
        avg_durations_max.append(avg_duration_max if not max_trades.empty else 0)

        # Calculate time to reach balance thresholds for each episode
        start_time = group['close_time'].min()
        balance_thresholds = [500, 2000, 10000, 50000, 200000, 1_000_000, 5_000_000, 10_000_000]
        time_to_balance = {threshold: None for threshold in balance_thresholds}

        for index, row in group.iterrows():
            current_balance = row['balance']
            current_time = row['close_time']

            for threshold in balance_thresholds:
                if time_to_balance[threshold] is None and current_balance >= threshold:
                    days_to_reach = (current_time - start_time).days
                    time_to_balance[threshold] = days_to_reach

        time_to_balances.append(time_to_balance)

    # Plotting
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Trading Bot Analysis')

    # Plot 1: Frequency of exit reason 'max'
    axs[0, 0].bar(episodes, max_frequencies, color='blue')
    axs[0, 0].set_title("Frequency of 'max' Exit Reason")
    axs[0, 0].set_xlabel('Episode')
    axs[0, 0].set_ylabel('Percentage')

    # Plot 2: Longest streak of 'liq'
    axs[0, 1].bar(episodes, longest_liq_streaks, color='red')
    axs[0, 1].set_title("Longest 'liq' Streak")
    axs[0, 1].set_xlabel('Episode')
    axs[0, 1].set_ylabel('Streak Length')

    # Plot 3: Average duration of 'max' trades
    axs[1, 0].bar(episodes, avg_durations_max, color='green')
    axs[1, 0].set_title("Average Duration of 'max' Trades")
    axs[1, 0].set_xlabel('Episode')
    axs[1, 0].set_ylabel('Duration (hours)')

    # Plot 4: Time to reach balance thresholds
    for threshold in balance_thresholds:
        days_to_reach = [time_to_balance[threshold] for time_to_balance in time_to_balances]
        axs[1, 1].plot(episodes, days_to_reach, label=f'Threshold {threshold}')
    axs[1, 1].set_title("Time to Reach Balance Thresholds")
    axs[1, 1].set_xlabel('Episode')
    axs[1, 1].set_ylabel('Days')
    axs[1, 1].legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    main()

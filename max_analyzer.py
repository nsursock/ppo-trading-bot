import argparse
import pandas as pd

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

    for episode, group in grouped:
        # Calculate the frequency of exit reason "max" as a percentage for each episode
        total_trades = len(group)
        max_frequency_percentage = (group['exit_reason'].value_counts().get('max', 0) / total_trades) * 100
        print(f"Episode {episode}: Frequency of exit reason 'max' as a percentage: {max_frequency_percentage:.2f}%")

        # Calculate the longest streak of exit reason "liq" for each episode
        longest_liq_streak = (group['exit_reason'] == 'liq').astype(int).groupby((group['exit_reason'] != 'liq').cumsum()).sum().max()
        print(f"Episode {episode}: Longest streak of exit reason 'liq': {longest_liq_streak}")

    # Group by episode and calculate time to reach balance thresholds
    grouped = df.groupby('episode')

    for episode, group in grouped:
        # Convert 'close_time' to datetime if not already
        group['close_time'] = pd.to_datetime(group['close_time'])

        # Get the start time of the episode
        start_time = group['close_time'].min()

        # Define balance thresholds
        balance_thresholds = [500, 2000, 10000, 50000, 200000, 1_000_000, 5_000_000, 10_000_000]

        # Initialize a dictionary to store the time to reach each balance threshold
        time_to_balance = {threshold: None for threshold in balance_thresholds}

        # Iterate over the group to find the time to reach each balance threshold
        for index, row in group.iterrows():
            current_balance = row['balance']
            current_time = row['close_time']

            for threshold in balance_thresholds:
                if time_to_balance[threshold] is None and current_balance >= threshold:
                    # Calculate the number of days from the start of the episode
                    days_to_reach = (current_time - start_time).days
                    time_to_balance[threshold] = days_to_reach

        # Print the time to reach each balance threshold for the episode
        print(f"Episode {episode}:")
        for threshold, days in time_to_balance.items():
            if days is not None:
                print(f"  Days to reach balance {threshold}: {days} days")
            else:
                print(f"  Balance {threshold} was not reached.")

if __name__ == "__main__":
    main()

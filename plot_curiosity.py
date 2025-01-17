import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize trading bot performance.')
    parser.add_argument('-f', '--history_file', type=str, help='Path to the history CSV file')
    args = parser.parse_args()
    
    # Load history from CSV
    df = pd.read_csv(args.history_file)
    
    # Assuming the CSV has columns 'episode', 'date', and 'pnl'
    df['date'] = pd.to_datetime(df['close_time'])
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    
    # Filter data to include only months up to June
    # df = df[df['month'] <= 6]
    
    # Calculate available capital at the end of each day
    df['capital'] = 1000 + df.groupby(['episode'])['pnl'].cumsum()
    
    # Calculate average capital per day per month
    avg_capital = df.groupby(['month', 'day'])['capital'].mean().unstack(fill_value=0)
    
    # Create a figure with two subplots
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
    
    # Normal scale plot
    axes[0].set_title('Average Available Capital at End of Each Day (Normal Scale)')
    axes[0].set_xlabel('Day')
    axes[0].set_ylabel('Month')
    im1 = axes[0].imshow(avg_capital, aspect='auto', cmap='viridis', origin='lower')
    fig.colorbar(im1, ax=axes[0], label='Average Capital')
    axes[0].set_xticks(ticks=np.arange(avg_capital.columns.size))
    axes[0].set_xticklabels(avg_capital.columns)
    axes[0].set_yticks(ticks=np.arange(avg_capital.index.size))
    axes[0].set_yticklabels(avg_capital.index)
    axes[0].invert_yaxis()
    
    # Log scale plot
    axes[1].set_title('Average Available Capital at End of Each Day (Log Scale)')
    axes[1].set_xlabel('Day')
    axes[1].set_ylabel('Month')
    log_avg_capital = np.log1p(avg_capital)  # Use log1p to handle zero values safely
    im2 = axes[1].imshow(log_avg_capital, aspect='auto', cmap='viridis', origin='lower')
    fig.colorbar(im2, ax=axes[1], label='Log of Average Capital')
    axes[1].set_xticks(ticks=np.arange(avg_capital.columns.size))
    axes[1].set_xticklabels(avg_capital.columns)
    axes[1].set_yticks(ticks=np.arange(avg_capital.index.size))
    axes[1].set_yticklabels(avg_capital.index)
    axes[1].invert_yaxis()
    
    plt.tight_layout()
    plt.show()
    
    # Create a second figure for the evolution of balance for each episode
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.set_title('Evolution of Balance for Each Episode (Log Scale)')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Log of Balance')

    # Plot balance evolution for each episode
    for episode, group in df.groupby('episode'):
        ax2.plot(group['date'], np.log1p(group['capital']), label=f'Episode {episode}')  # Use log1p to handle zero values safely

    ax2.legend(title='Episodes')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    

import json
import ccxt
from dotenv import load_dotenv
import os
from web3 import Web3
import requests
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
# load_dotenv('.env')

# Initialize ccxt Binance exchange
binance = ccxt.binance()

from interactions import fetch_open_trades, close_all_open_trades, setup_env
        
def main():
    # global web3, contract_address, wallet_address, private_key, contract
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Update stop-loss for profitable trades.')
    parser.add_argument('-e', '--env', type=str, help='Environment to use (sepolia or arbitrum).')

    # Parse the arguments
    args = parser.parse_args()
    
    # Load the appropriate environment file
    if args.env:
        env_file = f".env.{args.env}"
    else:
        env_file = ".env"
    setup_env(env_file)

    # open_trades = fetch_open_trades()
    # print(open_trades)

    # Use the parsed arguments
    close_all_open_trades()

if __name__ == "__main__":
    main()

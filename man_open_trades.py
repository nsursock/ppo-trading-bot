import argparse
import json
import os
from dotenv import load_dotenv
from web3 import Web3
import logging
import ccxt
import requests
import base64
import math

def send_post_request_to_blocktorch(transaction):
    url = "http://localhost:8000/api/internal/transaction/decode"  # Updated to local URL
    
    username = "nsursock"
    password = "aVeaatlc24*@"
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    payload = {
        "abis": {
            contract_address: {
                "contractAbi": contract_abi
            }
        },
        "transaction": transaction
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + encoded_credentials  # Base64 encoded credentials
    }

    # logging.info(f"Sending POST request to {url} with payload: {json.dumps(payload, indent=2)}")
    response = requests.post(url, json=payload, headers=headers)
    logging.info(f"POST request sent to {url}, status code: {response.status_code}")
    
    try:
        response_json = response.json()
        logging.debug(f"Response from blocktorch: {response_json}")
        return response_json
    except ValueError:
        logging.error(f"Failed to decode JSON response: {response.text}")
        return None
    
def decode_error(error, tx_data):
    if hasattr(error, 'data'):
        raw_data = error.data
        # Send the error data to blocktorch.xyz
        transaction = {
            "to": contract_address,
            "input": tx_data['data'],
            "value": "0x0",  # Assuming no value is sent with the transaction
            "error": {
                "data": raw_data
            }
        }
        response = send_post_request_to_blocktorch(transaction)
        if response:
            logging.info(f"Blocktorch response: Transaction function: {response['transaction']['functionFragment']['name']}, Error: {response['error']['name']}")
        else:
            logging.error("Failed to get a valid response from blocktorch")

def open_trade(latest_close_price, pairs, symbol, action, collateral=200, leverage=10, tp_price=0, sl_price=0):
    # leverageExperiment = 5
    try: 
        tx_data = None
        logging.warning(f"Attempting to open trade with symbol: {symbol}, action: {action}, collateral: {collateral}, leverage: {leverage}")
        
        pairObject = next(pair for pair in pairs if pair['symbol'] == symbol)
        logging.debug('Found index of symbol')
            
        nonce = web3.eth.get_transaction_count(wallet_address)
        logging.debug(f'Got transaction count {nonce}')
        gas_price = web3.eth.gas_price
        logging.debug(f'Got gas price {gas_price}')

        # latest_close_price = data.iloc[-1]['close']  # Use .iloc for positional indexing
        logging.debug(f'Latest close price: {latest_close_price}')  # Debug print for price

        _trade = {
            'user': wallet_address,
            'index': 0,  # uint32
            'pairIndex': int(pairObject['index']),  # uint16
            'leverage': int(leverage * 1000),  # uint24 (50x leverage)
            'long': action == 'open_long',  # bool
            'isOpen': True,  # bool
            'collateralIndex': 3,  # uint8
            'tradeType': 0,  # enum ITradingStorage.TradeType
            'collateralAmount': int(web3.to_wei(collateral, 'mwei')),  # uint120, BigNumber to string
            'openPrice': int(latest_close_price * 1e10),  # uint64, converting price to BigNumber
            'tp': int(tp_price * 1e10),  # uint64
            'sl': int(sl_price * 1e10),  # uint64
            '__placeholder': 0  # uint192, BigNumber to string
        }

        # Convert all values to native Python types
        _tradeForJsonDump = {k: int(v) if isinstance(v, (int, float)) else v for k, v in _trade.items()}

        logging.debug('Trade object: %s', json.dumps(_tradeForJsonDump, indent=2))  # Debug print for trade object 

        _max_slippage_p = 5000  # uint32  It's specified in parts per thousand (e.g., 1000 for 1%, 500 for 0.5%).
        _referrer = '0x0000000000000000000000000000000000000000'  # address
        
        
        # max_retries = 3  # Set the maximum number of retries
        # for attempt in range(max_retries):
        #     try:
        #         gas_estimate = contract.functions.openTrade(_trade, _max_slippage_p, _referrer).estimate_gas({'from': wallet_address})
        #         logging.debug(f'Gas estimate: {gas_estimate}')  # Debug print for gas estimate
        #         break  # Exit loop if successful
        #     except Exception as e:
        #         logging.warning(f"Gas estimation failed on attempt {attempt + 1}: {e}")
        #         if attempt == max_retries - 1:
        #             raise  # Raise the exception if the last attempt fails

        gas_estimate = contract.functions.openTrade(_trade, _max_slippage_p, _referrer).estimate_gas({'from': wallet_address})
        logging.debug(f'Gas estimate: {gas_estimate}')  # Debug print for gas estimate
        
        # gas_estimate = 3_000_000 #2500000

        # Calculate maxFeePerGas and maxPriorityFeePerGas
        base_fee = web3.eth.gas_price
        max_priority_fee_per_gas = web3.to_wei(1, 'gwei')  # Lowered priority fee
        max_fee_per_gas = base_fee + max_priority_fee_per_gas

        tx_data = contract.functions.openTrade(_trade, _max_slippage_p, _referrer).build_transaction({
            'gas': int(gas_estimate * 1.5),  # Reduced gas multiplier
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'nonce': nonce,
            'chainId': chain_id
        })
        logging.debug(f"Transaction data built: {tx_data}")

        tx = {
            'to': contract_address,
            'data': tx_data['data'],
            'gas': int(gas_estimate * 2),
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'nonce': nonce,
            'chainId': chain_id  # Specify the correct chain ID here
        }

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        logging.debug('Signed transaction')
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logging.debug(f'Transaction hash: {web3.to_hex(tx_hash)}')

        # Check for market cancellation
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt['status'] == 0:
            logging.debug('Market was canceled. Handling cancellation...')
            # Add your cancellation handling logic here
            # return -1  # Indicate failure due to market cancellation
            
        
        logging.info(f"Opened trade for symbol: {symbol}, Transaction hash: {receipt.transactionHash.hex()}")
        return web3.to_hex(tx_hash)  # Return transaction hash on success

    # except ContractLogicError as error:
    #     logging.error(f'Contract logic error occurred: {error}')
    #     if tx_data:
    #         decode_error(error, tx_data)
    #     else:
    #         decode_revert_reason(error)
    except Exception as error:
        logging.error(f'An unexpected error occurred: {error}')
        if tx_data:
            decode_error(error, tx_data)
        # decode_revert_reason(error)
        
def fetch_symbols():
    response = requests.get(os.getenv('GAINS_NETWORK_URL'))
    pairs = response.json()['pairs']
    return [{'symbol': pair['from'], 'index': idx, 'groupIndex': pair['groupIndex']} for idx, pair in enumerate(pairs)]

import random
def open_trades_for_symbols_with_risk_and_direction(symbols, collateral_shares, total_collateral, risk_levels, tp_percentage, sl_percentage, direction):
    """
    Opens trades for multiple symbols with specified collateral shares, risk levels, tp/sl percentages, and direction.

    :param symbols: List of symbols to trade.
    :param collateral_shares: List of collateral shares corresponding to each symbol.
    :param total_collateral: Total collateral amount to be distributed among symbols.
    :param risk_levels: List of risk levels corresponding to each symbol (0 to 1).
    :param tp_percentage: Take-profit percentage.
    :param sl_percentage: Stop-loss percentage.
    :param direction: Portfolio direction ('bullish' for long, 'bearish' for short).
    """
    # Initialize the exchange
    exchange = ccxt.binance()  # Replace 'binance' with your preferred exchange
    
    pairs = fetch_symbols()

    # Fetch the latest OHLC data from the new endpoint
    response = requests.get("https://backend-pricing.eu.gains.trade/charts")
    ohlc_data = response.json()

    for symbol, share, risk_level in zip(symbols, collateral_shares, risk_levels):
        # Fetch the latest close price using ccxt
        # ticker = exchange.fetch_ticker(symbol + '/USDT')
        # latest_close_price = ticker['last']
        
        # Get the pair index for the symbol
        pairObject = next(pair for pair in pairs if pair['symbol'] == symbol)
        pair_index = pairObject['index']

        # Extract the latest close price using the pair index
        latest_close_price = ohlc_data['closes'][pair_index]
        # print(pairObject, pair_index, latest_close_price)
        
        collateral = round(total_collateral * share)
        leverage = max(2, min(150, round(2 + (risk_level * (150 - 2)) * random.uniform(0.9, 1.1))))  # Calculate leverage based on risk level
        
        if tp_percentage:
            tp_price = latest_close_price * (1 + (tp_percentage / 100) / leverage) if direction == 'bullish' else latest_close_price * (1 - (tp_percentage / 100) / leverage)
        else:
            tp_price = 0
        
        if sl_percentage:
            sl_price = latest_close_price * (1 - (sl_percentage / 100) / leverage) if direction == 'bullish' else latest_close_price * (1 + (sl_percentage / 100) / leverage)
        else:
            sl_price = 0
        
        action = 'open_long' if direction == 'bullish' else 'open_short'
        
        # Assuming 'pairs' is available in the scope
        open_trade(latest_close_price, pairs, symbol, action, collateral, leverage, tp_price, sl_price)
        
# Approve the contract to spend tokens on behalf of the user
def approve_tokens(spender_address, amount, private_key):
    nonce = web3.eth.get_transaction_count(wallet_address)
    tx = contract.functions.approve(spender_address, amount).build_transaction({
        'chainId': chain_id,
        'gas': 200000,
        'gasPrice': web3.to_wei('5', 'gwei'),
        'nonce': nonce,
    })

    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def main():
    global web3, contract_address, wallet_address, private_key, contract, contract_abi, chain_id
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Open trades for symbols with specified collateral shares, risk levels, tp/sl percentages, and direction.')
    parser.add_argument('-e', '--env', type=str, help='Environment to use (sepolia or arbitrum).')
    parser.add_argument('-s', '--stop_loss_percentage', type=float, default=None, help='Stop-loss percentage to use.')
    parser.add_argument('-t', '--take_profit_percentage', type=float, default=None, help='Take-profit percentage to use.')
    parser.add_argument('-d', '--direction', type=str, default='bullish', help='Direction to use.')

    # Parse the arguments
    args = parser.parse_args()

    # Load the appropriate environment file
    if args.env:
        env_file = f".env.{args.env}"
    else:
        env_file = ".env"

    # Load environment variables from the specified file
    load_dotenv(env_file)
    
    chain_id = 42161 if args.env == 'prod' else 421614

    # Initialize Web3 with Alchemy URL after loading environment variables
    web3 = Web3(Web3.HTTPProvider(os.getenv('ALCHEMY_URL')))

    # Contract and Wallet details
    contract_address = os.getenv('CONTRACT_ADDRESS')
    private_key = os.getenv('PRIVATE_KEY')
    wallet_address = web3.eth.account.from_key(private_key).address

    # Define the contract ABI
    with open('./abi.json') as f:
        contract_abi = json.load(f)
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    
    # approve_tokens(wallet_address, 200, private_key)
    
    # STD, RWA, AI, DEPIN, GAMING, MEME
    
    # symbols_main = ['BTC', 'ETH', 'SOL', 'NEAR', 'TIA', 'MANTA', 'SEI', 'PEAQ', 'LINGO', 'SIDUS', 'UOS', 'GUNZILLA', 'TAO', 'AETHIR', 'PRIME', 'NATIX', 'IOTX', 'ORN', 'ORDERLY', 'GMX', 'ZEUS', 'PARTICLE', 'FOXY', 'PUFF']
    # symbols_sat = ['SOIL', 'CSIX', 'WINR', 'MLC', 'CTA', 'EOF', 'SAVM', 'TAP', 'SPOT', 'EESEE', 'ORNJ']
    
    # Given data
    tickers = ['1INCH', 'AAVE', 'ACT', 'ACX', 'ADA', 'AERO', 'AEVO', 'AGIX', 'ALGO', 'ALICE', 'ALPH', 'ALT', 'ANKR', 'ANT', 'APE', 'API3', 'APT', 'APU', 'AR', 'ARB', 'ARK', 'ASTR', 'ATH', 'ATOM', 'AUCTION', 'AVAIL', 'AVAX', 'AXS', 'BABYDOGE', 'BAL', 'BANANA', 'BAT', 'BCH', 'BEAM', 'BITCOIN', 'BLAST', 'BLUR', 'BNB', 'BNT', 'BNX', 'BOME', 'BONK', 'BRETT', 'BSV', 'BTC', 'BTT', 'CAKE', 'CAT', 'CATI', 'CELO', 'CFX', 'CHEX', 'CHILLGUY', 'CHZ', 'CKB', 'COMP', 'CORE', 'CRV', 'CVC', 'DAR', 'DASH', 'DEGEN', 'DOG', 'DOGE', 'DOGS', 'DOT', 'DYDX', 'DYM', 'EGLD', 'EIGEN', 'ENA', 'ENJ', 'ENS', 'EOS', 'ETC', 'ETH', 'ETHFI', 'FET', 'FIL', 'FLOKI', 'FLOW', 'FLUX', 'FTM', 'FTT', 'FXS', 'GALA', 'GMT', 'GMX', 'GOAT', 'GRASS', 'GRT', 'HBAR', 'HIPPO', 'HMSTR', 'HOT', 'ICP', 'ICX', 'ILV', 'IMX', 'INJ', 'IO', 'IOTA', 'IOTX', 'JASMY', 'JTO', 'JUP', 'KAS', 'KAVA', 'KLAY', 'KSM', 'LDO', 'LINK', 'LISTA', 'LL', 'LOOM', 'LRC', 'LTC', 'LUMIA', 'LUNA', 'MAGIC', 'MANA', 'MANTA', 'MASK', 'MATIC', 'MAVIA', 'MEME', 'MERL', 'METIS', 'MEW', 'MINA', 'MKR', 'MNT', 'MOG', 'MOODENG', 'MOTHER', 'MSN', 'MYRO', 'NEAR', 'NEIRO', 'NEIROCTO', 'NEO', 'NMR', 'NOT', 'NPC', 'NTRN', 'OCEAN', 'OM', 'OMG', 'OMNI', 'ONDO', 'OP', 'ORBS', 'ORDI', 'OSMO', 'PENDLE', 'PEOPLE', 'PEPE', 'PIXEL', 'PNUT', 'POL', 'POLYX', 'PONKE', 'POPCAT', 'PRCL', 'PYTH', 'QNT', 'QTUM', 'RARE', 'RATS', 'RAY', 'RDNT', 'REEF', 'REZ', 'RNDR', 'RONIN', 'ROSE', 'RPL', 'RSR', 'RUNE', 'RVN', 'SAFE', 'SAGA', 'SAND', 'SATS', 'SC', 'SEI', 'SHIB', 'SKL', 'SLERF', 'SNX', 'SOL', 'SPX', 'SSV', 'STG', 'STORJ', 'STRK', 'STX', 'SUI', 'SUN', 'SUNDOG', 'SUPER', 'SUSHI', 'SYN', 'SYS', 'TAO', 'THETA', 'TIA', 'TNSR', 'TON', 'TRB', 'TRX', 'TURBO', 'TWT', 'UMA', 'UNI', 'UXLINK', 'VET', 'VIRTUAL', 'W', 'WAVES', 'WIF', 'WLD', 'WOO', 'XLM', 'XMR', 'XRP', 'XTZ', 'YFI', 'ZEC', 'ZEN', 'ZETA', 'ZEUS', 'ZIL', 'ZK', 'ZRO', 'ZRX']
    
    if args.env == 'prod':
        symbols_main = ['BTC', 'ETH', 'SOL', 'NEAR', 'TIA', 'MANTA', 'SEI', 'PEAQ', 'LINGO', 'SIDUS', 'UOS', 'GUNZILLA', 'TAO', 'AETHIR', 'PRIME', 'NATIX', 'IOTX', 'ORN', 'ORDERLY', 'GMX', 'ZEUS', 'PARTICLE', 'FOXY', 'PUFF']
        symbols_sat = ['SOIL', 'CSIX', 'WINR', 'MLC', 'CTA', 'EOF', 'SAVM', 'TAP', 'SPOT', 'EESEE', 'ORNJ']
    else:
        symbols_main = ['BTC', 'ETH', 'SOL']
        symbols_sat = []

    # Matching
    main_matches = [symbol for symbol in symbols_main if symbol in tickers]
    sat_matches = [symbol for symbol in symbols_sat if symbol in tickers]

    collateral_shares_main = [0.1, 0.1, 0.08, 0.06, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02]
    remaining_value = (0.1 - 0.01) / 10  # Distribute remaining 0.09 across 10 values
    collateral_shares_sat = [0.01] + [remaining_value] * 10  # One 0.01 followed by ten 0.009s

    # Get corresponding collateral shares for matched symbols
    collateral_shares_main_matched = [share for symbol, share in zip(symbols_main, collateral_shares_main) 
                                    if symbol in main_matches]
    
    # For satellite tokens
    remaining_value = (0.1 - 0.01) / len(sat_matches) if sat_matches else 0  # Distribute remaining evenly
    collateral_shares_sat_matched = ([0.01] + [remaining_value] * (len(sat_matches) - 1)) if sat_matches else []
    
    # Combine matched symbols and their shares
    symbols = main_matches + sat_matches
    collateral_shares = collateral_shares_main_matched + collateral_shares_sat_matched
    
    # Normalize shares to ensure they sum to 1
    if collateral_shares:
        total_shares = sum(collateral_shares)
        collateral_shares = [round(share / total_shares, 2) for share in collateral_shares]
    
    # Calculate risk levels inversely proportional to shares, scaled between 0.1 and 0.5
    max_share = max(collateral_shares)
    min_share = min(collateral_shares)
    MIN_RISK = 0.075
    MAX_RISK = 0.25
    risk_levels = [round(MIN_RISK + (MAX_RISK - MIN_RISK) * (max_share - share) / (max_share - min_share), 2) for share in collateral_shares]
    
    print(len(symbols), len(collateral_shares), round(math.floor(sum(collateral_shares)), 2), symbols, collateral_shares, risk_levels)
    
    total_collateral = 87.5
    
    tp_percentage = args.take_profit_percentage
    sl_percentage = args.stop_loss_percentage
    direction = args.direction

    open_trades_for_symbols_with_risk_and_direction(symbols, collateral_shares, total_collateral, risk_levels, tp_percentage, sl_percentage, direction)

if __name__ == "__main__":
    main()

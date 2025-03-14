import os
import argparse
from websocket import WebSocketApp
import json
import glob
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3.common.monitor import Monitor
from utilities import calculate_reward
import pandas as pd
import logging
import ccxt
import threading
import queue
import pprint  # Add this import at the top of your file
from tabulate import tabulate  # Import tabulate

from interactions import setup_env, get_nonce, fetch_symbols, open_trade, close_trade, fetch_open_trades, close_all_open_trades
from man_adjust_sl import update_stop_loss_for_profitable_trades, fetch_open_trades2
import time

# Load environment variables
# from dotenv import load_dotenv
# load_dotenv()

# Initialize a buffer to store messages
message_buffer = {}

# Initialize a queue to communicate between threads
risk_management_queue = queue.Queue()

def risk_management_listener():
    while True:
        try:
            # Wait for a new message to process
            i, low_price, high_price = risk_management_queue.get()
            live_env.envs[0].get_wrapper_attr('handle_risk_management_basic')(i, low_price, high_price)
            logging.debug(f"Handled risk management for symbol index {i} with low: {low_price} and high: {high_price}")
        except Exception as e:
            logging.error(f"Error in risk management listener: {e}")

# Start the risk management listener in a separate thread
risk_thread = threading.Thread(target=risk_management_listener, daemon=True)
risk_thread.start()

# Define WebSocket event handlers
# Define WebSocket event handlers
def on_message(ws, message):
    logging.debug(f"Received raw message: {message}")  # Debug level log for raw message

    try:
        message = json.loads(message)
        logging.debug(f"Message decoded successfully")  # Info level log for successful decoding

        if 'k' in message:
            logging.debug("Key 'k' found in message")  # Debug level log for key presence
        
            candle = message['k']
            symbol = candle['s'][:-4]  # remove USDT from symbol
            logging.debug(f"Processing symbol: {symbol}")  # Info level log for symbol processing
            
            kline_data_1s = {
                'symbol': symbol,
                'timestamp': candle['t'],
                'open': float(candle['o']),
                'high': float(candle['h']),
                'low': float(candle['l']),
                'close': float(candle['c']),
                'volume': float(candle['v']),
            }
            logging.debug(f"Kline data prepared: {kline_data_1s}")  # Info level log for kline data preparation
            
            # Find the index of the symbol in valid_symbols
            if symbol in financial_params['symbols']:
                i = financial_params['symbols'].index(symbol)
                low_price = kline_data_1s['low']
                high_price = kline_data_1s['high']

                # Add the risk management task to the queue
                risk_management_queue.put((i, low_price, high_price))
                logging.debug(f"Queued risk management task for symbol {symbol}")
            
            if candle['x']:
                logging.info(f"Processing closed candle for symbol {symbol}")  # Debug level log for closed candle processing
                timestamp = candle['t']
                if timestamp not in message_buffer:
                    message_buffer[timestamp] = []
                    logging.debug(f"Created new entry in message_buffer for timestamp: {timestamp}")  # Debug level log for buffer entry creation
                
                kline_data = {
                    'symbol': symbol,
                    'timestamp': candle['t'],
                    'open': float(candle['o']),
                    'high': float(candle['h']),
                    'low': float(candle['l']),
                    'close': float(candle['c']),
                    'volume': float(candle['v']),
                }
                logging.debug(f"Kline data prepared: {kline_data}")  # Info level log for kline data preparation
                
                kline_df = pd.DataFrame([kline_data])
                kline_df['timestamp'] = pd.to_datetime(kline_df['timestamp'], unit='ms')
                kline_df[['open', 'high', 'low', 'close', 'volume']] = kline_df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)
                
                message_buffer[timestamp].append(kline_df)
                logging.debug(f"Appended kline data to message_buffer for timestamp: {timestamp}")  # Debug level log for data appending
                
                if len(message_buffer[timestamp]) == len(financial_params['symbols']):
                    from utilities import transform_to_matrix, add_technical_indicators
                    logging.info(f"Received all messages for timestamp: {timestamp}")  # Info level log for all messages received
                    
                    message_buffer[timestamp] = sorted(message_buffer[timestamp], key=lambda x: x.iloc[0]['symbol'])
                    logging.debug(f"Sorted message_buffer for timestamp: {timestamp}")  # Debug level log for buffer sorting
                    
                    # logging.info(f"Current window: {current_window}")
                    
                    for index, symbol in enumerate(sorted(financial_params['symbols'])):
                        cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                        
                        # Check if it's the first batch of messages
                        if len(message_buffer) == 1:
                            dfw = current_window[symbol]  # First batch
                            logging.debug(f"First batch for symbol {symbol}: {len(dfw)} candles")
                        else:
                            dfw = current_window[symbol].iloc[1:]  # Subsequent batches
                            logging.debug(f"Subsequent batch for symbol {symbol}: {len(dfw)} candles")

                        dfc = message_buffer[timestamp][index]
                        logging.debug(f"Current batch for symbol {symbol}: {len(dfc)} candles")
                        dfw.reset_index(inplace=True)
                        dfc.reset_index(inplace=True)
                        
                        # Concatenate without dropping duplicates immediately
                        current_window[symbol] = pd.concat([dfw[cols], dfc[cols]], axis=0)
                        
                        logging.debug(f"Before drop duplicates for symbol {symbol}: {len(current_window[symbol])} candles")  # Debug level log for window update
                        
                        # Sort and drop duplicates after concatenation
                        current_window[symbol] = current_window[symbol].sort_values(by='timestamp').drop_duplicates(subset=['timestamp'], keep='last')
                        current_window[symbol].set_index('timestamp', inplace=True)
                        
                        # if current_window[symbol] length is financial_params['limit'] - 1
                        if len(current_window[symbol]) == financial_params['limit'] - 1:
                            # duplicate the first row
                            current_window[symbol] = pd.concat([current_window[symbol].iloc[0:1], current_window[symbol]], axis=0)
                        
                        current_window[symbol] = add_technical_indicators(current_window[symbol])
                        
                        logging.info(f"Updated current window for symbol {symbol}: {len(current_window[symbol])} candles")  # Debug level log for window update
                        logging.debug(f"{current_window[symbol].head()}")  # Debug level log for window update
                    
                    # Print the columns of the DataFrame
                    # print(current_window[symbol].columns)
                
                    timestamps = current_window[symbol].index.tolist()

                    data = transform_to_matrix(current_window)
                    logging.debug(f"Preprocessed data for current_window")  # Debug level log for data preprocessing
                    
                    live_env.envs[0].get_wrapper_attr('update_data')(data, timestamps)
                    logging.info(f"Updated environment with new data")  # Info level log for environment update
                    
                    obs = live_env.envs[0].get_wrapper_attr('next_observation')()
                    logging.info(f"Obtained current observation from environment")  # Debug level log for observation retrieval
                    
                    action, _states = model.predict(obs)
                    logging.info(f"Predicted action: {action}")  # Info level log for action prediction
                    
                    # actions = [model.predict(obs)[0] for model in models]
                    # averaged_action = sum(actions) / len(actions)
                    # logging.info(f"Averaged action: {averaged_action}")  # Log the averaged action
                    
                    _, _, _, _, infos = live_env.envs[0].get_wrapper_attr('step')(action)
                    logging.info(f"Stepped environment with action {action}")  # Debug level log for environment stepping
                    
                    # Prepare pretty-printed orders for logging
                    orders_table = tabulate(
                        [{"key": key, **value} for key, value in infos['orders'].items()],
                        headers="keys",
                        tablefmt="pretty"
                    )
                    logging.info(f"Number of orders: {len(infos['orders'])} \n Orders:\n{orders_table}")
                    
                    # move the code below to a separate thread
                    # After the environment step
                    threading.Thread(target=process_orders, args=(infos,), daemon=True).start()
                    
                    # Prepare pretty-printed positions for email
                    positions_table = tabulate(
                        [{"key": live_env.envs[0].get_wrapper_attr('params')['symbols'][idx], **{k: v for k, v in position.items() if k in ["open_time", "type", "entry_price", "leverage", "collateral"]}} for idx, position in enumerate(infos['stats']['positions'])],
                        headers="keys",
                        tablefmt="pretty"
                    )
                    logging.info(f"Net worth: {infos['stats']['net_worth']}, Balance: {infos['stats']['balance']}, Positions:\n{positions_table}")

                    # Send email with pretty-printed positions
                    send_error_email("Stats", f"Net worth: {infos['stats']['net_worth']}, Balance: {infos['stats']['balance']}, Positions:\n{positions_table}")
                    
    except Exception as e:  
        logging.error(f"Error processing message: {e}")

def on_error(ws, error):
    logging.error(f"Error: {error}")
    # Attempt to reconnect
    logging.info("Attempting to reconnect...")
    time.sleep(5)  # Wait for 5 seconds before reconnecting
    start_trading_bot()  # Restart the trading bot

def on_close(ws, close_status_code, close_msg):
    logging.info(f"WebSocket closed: {close_status_code} - {close_msg}")
    # Attempt to reconnect
    logging.info("Attempting to reconnect...")
    time.sleep(5)  # Wait for 5 seconds before reconnecting
    start_trading_bot()  # Restart the trading bot

def on_open(ws):
    global live_env, model, financial_params, valid_symbols, current_window
    
    logging.info("WebSocket connection opened")
    logging.debug("Initializing trading bot components")

    from utilities import preprocess_data, select_cryptos
    from parameters import selected_params, training_params, log_parameters
    from environment import TradingEnvironment
    
    # close_all_open_trades()
    
    financial_params = selected_params
    financial_params['cooldown_period'] = 4
    # financial_params['kelly_fraction'] = 0.5
    financial_params['initial_balance'] = 50
    # financial_params['boost_factor'] = 10
    financial_params['basic_risk_mgmt'] = True
    
    # for prod
    if env == 'prod':
        financial_params['interval'] = '1h'  # for debugging
        financial_params['limit'] = 24 * 40
        # financial_params['symbols'] = sorted(['GRASS', 'PLUME', 'PONKE', 'VINE', 'ZEUS', 'HYPE', 'ARK', 'APT', 'APU', 'VVV'])
        financial_params['symbols'] = select_cryptos(financial_params['target_num_symbols'] * 2) #sorted(['BTC', 'ETH', 'SOL', 'NEAR', 'TIA', 'MANTA', 'SEI', 'IOTX', 'GMX', 'TAO'])
    else:
        financial_params['symbols'] = select_cryptos(financial_params['target_num_symbols'] * 2, network='sepolia')
        financial_params['interval'] = '1h'  # for debugging
        financial_params['limit'] = 24 * 40
        # financial_params['symbols'] = sorted(['BTC', 'ETH', 'SOL', 'NEAR', 'TIA', 'MANTA', 'SEI', 'IOTX', 'GMX', 'WIF'])
    
    
    log_parameters(financial_params)
    logging.debug(f"Financial parameters set: {financial_params}")

    # # Prepare historical data
    data_matrix, timestamps, mapping, valid_symbols, current_window = preprocess_data(financial_params['target_num_symbols'], financial_params['symbols'], financial_params['interval'], financial_params['limit'])
    financial_params['symbols'] = valid_symbols
    
    # Initialize the environment with live data
    environment = TradingEnvironment(data_matrix=data_matrix, timestamps=timestamps, mapping=mapping, render_mode='human', params=selected_params, reward_function=calculate_reward, market_data=None, live_mode=True)
    live_env = DummyVecEnv([lambda: Monitor(environment)])
    live_env = VecNormalize(live_env, norm_obs=True, norm_reward=True, clip_obs=10.)
    
    # _, _, live_env, live_agent, _ = initialize_environments(financial_params, training_params, plot_dir='.')
    logging.debug("Environment initialized and normalized")
    
    # Set the environment to the latest step
    live_env.envs[0].get_wrapper_attr('reset')()  # Ensure the environment is reset to start
    logging.debug("Environment reset to initial state")
    
    if current_window is None:
        logging.error("Failed to prepare historical data. Exiting.")
        raise RuntimeError('Failed to prepare historical data. Exiting.')
    
    logging.info(f"Prepared historical data for trading with {len(live_env.envs[0].get_wrapper_attr('params')['symbols'])} symbols")
    
    params = {
        "method": "SUBSCRIBE",
        "params": [f"{symbol.lower()}usdt@kline_{financial_params['interval']}" for symbol in financial_params['symbols']],
        "id": 1
    }
    ws.send(json.dumps(params))
    logging.info(f"Subscribed to {', '.join(financial_params['symbols'])} with interval {financial_params['interval']}")

    # Load the trained model
    model = PPO.load(model_path)
    
    # # Load all models from the directory
    # model_files = glob.glob(os.path.join(model_path, "model_ppo_crypto_trading*.zip"))
    # models = []
    # for model_file in model_files:
    #     # live_env = DummyVecEnv([lambda: CryptoTradingEnv(reshaped_data, mapping, sorted(valid_symbols), timestamps, financial_params)])
    #     model = PPO.load(model_file, env=live_env)
    #     model.policy.eval()
    #     models.append(model)
    logging.info(f"Models loaded from {model_path}") 

# Main function to start the WebSocket connection
def start_trading_bot():
    websocket_url = "wss://stream.binance.com:9443/ws"
    logging.info(f"Connecting to WebSocket at {websocket_url}")
    ws = WebSocketApp(websocket_url, 
                      on_message=on_message, 
                      on_error=on_error, 
                      on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
    
import logging
from logging.handlers import RotatingFileHandler

# Configure logging with INFO level to stdout and DEBUG level to a file
def setup_logging():
    # Create a custom logger
    logger = logging.getLogger()
    
    # Remove all handlers associated with the logger
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels of logs

    # Create a handler for DEBUG level logs to a file
    debug_handler = RotatingFileHandler('debug.log', maxBytes=1048576, backupCount=5)
    debug_handler.setLevel(logging.DEBUG)

    # Create a handler for INFO level logs to a different file
    info_handler = RotatingFileHandler('info.log', maxBytes=1048576, backupCount=5)
    info_handler.setLevel(logging.INFO)

    # Create a handler for INFO level logs to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.INFO)  # Ensure only INFO level logs are sent to stdout

    # Create formatters and add them to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    debug_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)
    stdout_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(stdout_handler)

    # Ensure no propagation to root logger
    logger.propagate = False
    

def stop_loss_listener():
    while True:
        try:
            open_trades = fetch_open_trades2()
            print(open_trades)

            # Use the parsed arguments
            update_stop_loss_for_profitable_trades(stop_loss_percentage=10, pnl_threshold=100)
        except Exception as e:
            logging.error(f"An error occurred: {e}")

        # Wait for 5 minutes before running again
        time.sleep(300)

def process_orders(infos):
    for symbol, info in infos['orders'].items():
        logging.info('----------------------------------------------------------------------')
        current_trades = fetch_open_trades(symbol)
        trade_type = info.get('type')
        nonce = get_nonce()
        # Fetch the latest price for the symbol using CCXT
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker(symbol + '/USDT')
        latest_price = ticker['last']  # Get the last price from the ticker

        if trade_type in ['open_long', 'open_short']:
            if current_trades:  # Close the latest trade if it exists
                latest_trade = current_trades[0]
                symbol, trade_index, is_long = latest_trade
                close_trade(nonce, trade_index, latest_price, is_long)
                nonce += 1

            open_trade(nonce, latest_price, fetch_symbols(), symbol, trade_type, round(info.get('collateral')), round(info.get('leverage')), info.get('tp_price'), info.get('sl_price'))
            nonce += 1
            logging.info(f"Opened {trade_type} for {symbol} with latest price {latest_price} and info {info}")

        elif trade_type == 'close' and current_trades:  # Close trades if they exist
            latest_trade = current_trades[0]
            symbol, trade_index, is_long = latest_trade
            close_trade(nonce, trade_index, latest_price, is_long)
            nonce += 1
            logging.info(f"Closed {trade_type} for {symbol} with info {info}")
        else:
            logging.info(f"No action required for {symbol} with type {trade_type}")

if __name__ == "__main__":
    from utilities import send_error_email
    from parameters import selected_params
    global model_path, env
    parser = argparse.ArgumentParser(description='Live trading for a trained PPO model on crypto.')
    parser.add_argument('-m', '--model_path', default=None, type=str, help='Path to the trained model file')
    parser.add_argument('-e', '--env', default=None, type=str, help='Environment to use (sepolia or arbitrum).')
    
    args = parser.parse_args()
    
    model_path = args.model_path
    if model_path is None:
        model_path = f"{selected_params['model_name']}.zip"
   
     # Load the appropriate environment file
    if args.env:
        if args.env == 'rail':
            env = 'prod'
            env_file = None
        else:
            env = args.env
            env_file = f".env.{args.env}"
    else:
        env = 'test'
        env_file = None
    setup_env(env_file)
    
    # sl_thread = threading.Thread(target=stop_loss_listener, daemon=True)
    # sl_thread.start()
    
    send_error_email("Live Trading Started", f"Live trading for a trained PPO model on crypto (env: {env}).")

    # Configure logging to write to a file
    # logging.basicConfig(filename='live_trading.log', level=logging.INFO, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
    setup_logging()
    start_trading_bot()
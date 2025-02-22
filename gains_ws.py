import asyncio
from websocket import WebSocketApp
import json

from interactions import fetch_symbols

async def process_price_updates(price_updates):
    # Initialize an empty dictionary to store pairId and pairPrice
    price_dict = {}

    # Iterate over the list in steps of 2
    for i in range(0, len(price_updates), 2):
        pair_id = price_updates[i]
        pair_price = price_updates[i + 1]
        price_dict[pair_id] = pair_price

    print(price_dict)  # Print or handle the parsed prices as needed

    pairs = fetch_symbols('sepolia')
    for pair in pairs:
        pair_id = pair['index']
        pair_price = price_dict[pair_id]
        print(f"{pair['symbol']}: {pair_price}")

def on_message(ws, message):
    # Assuming the message is a JSON array of price updates
    price_updates = json.loads(message)
    asyncio.run(process_price_updates(price_updates))

def on_error(ws, error):
    print(f"An error occurred: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket connection opened")

def main():
    uri = "wss://backend-pricing.eu.gains.trade"
    ws = WebSocketApp(uri,
                      on_message=on_message,
                      on_error=on_error,
                      on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

# Run the WebSocket client
main()

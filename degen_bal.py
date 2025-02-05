import os
from dotenv import load_dotenv
import requests
import re

url = "https://backend-arbitrum.gains.trade/personal-trading-history-table/" + "0x70cc190c423754ab228845711e0471120889ef39"
print(url)

# Fetch data from the URL
response = requests.get(url)
data = response.json()

# Find the pnl of all pairs that match the pattern "???DEGEN/USD"
pattern = re.compile(r"^[A-Z]{3}DEGEN/USD$")
total_pnl_degen = 0
total_pnl_all = 0
for entry in data:
    total_pnl_all += entry.get("pnl", 0)
    if pattern.match(entry.get("pair", "")):
        total_pnl_degen += entry.get("pnl", 0)

print(f"Total PnL for pairs matching ???DEGEN/USD: {total_pnl_degen}")
print(f"Total PnL for all pairs: {total_pnl_all}")
import json
from eth_utils import keccak

# Load the ABI from a file
with open('trading-bot/v7/abi.json', 'r') as abi_file:
    abi = json.load(abi_file)

# Selector from transaction log or error
selector = "0x5508e5c6"

# Find matching error
for item in abi:
    if item["type"] == "error":
        # Recreate the selector using Keccak hash
        signature = f"{item['name']}({','.join(i['type'] for i in item['inputs'])})"
        computed_selector = keccak(text=signature).hex()[:10]
        if computed_selector == selector:
            print(f"Matched Error: {item['name']}")
            print(f"Inputs: {item['inputs']}")
            break
else:
    print("No match found in ABI")
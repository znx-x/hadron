# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Console used to interact with your node.

import requests
import json
from parameters import parameters
from getpass import getpass

# Dynamically determine the API URL based on parameters
API_URL = f"http://localhost:{parameters['port']}"

def pretty_print(response):
    """Pretty prints the JSON response."""
    print(json.dumps(response, indent=4, sort_keys=True))

def get_input():
    """Handles user input."""
    try:
        return input(">> ").strip()
    except EOFError:
        return "exit"

def fetch_coinbase():
    """Fetch the miner's wallet address from parameters."""
    return parameters.get("miner_wallet_address", "N/A")

def fetch_block_height():
    """Fetch the current block height from the API."""
    try:
        response = requests.get(f"{API_URL}/blockchain/length")
        data = response.json()
        return data.get("length", "N/A")
    except Exception as e:
        print(f"Error fetching block height: {e}")
        return "N/A"

def fetch_data_directory():
    """Fetch the data directory path from parameters."""
    return parameters.get("data_directory", "N/A")

def handle_command(command):
    """Handles the commands entered by the user."""
    try:
        # Commands without additional arguments
        if command == "blockchain.info":
            response = requests.get(f"{API_URL}/blockchain/info")
            pretty_print(response.json())

        elif command == "blockchain.latest":
            response = requests.get(f"{API_URL}/blockchain/latest")
            pretty_print(response.json())

        elif command == "blockchain.hashRate":
            response = requests.get(f"{API_URL}/blockchain/hashrate")
            pretty_print(response.json())

        elif command == "blockchain.blockTime":
            response = requests.get(f"{API_URL}/blockchain/blocktime")
            pretty_print(response.json())

        # Commands with one argument
        elif command.startswith("blockchain.block "):
            _, index = command.split(maxsplit=1)
            response = requests.get(f"{API_URL}/blockchain/block/{index}")
            pretty_print(response.json())

        elif command.startswith("blockchain.blockHash "):
            _, block_hash = command.split(maxsplit=1)
            response = requests.get(f"{API_URL}/blockchain/blockhash/{block_hash}")
            pretty_print(response.json())

        elif command.startswith("blockchain.transaction "):
            _, tx_hash = command.split(maxsplit=1)
            response = requests.get(f"{API_URL}/blockchain/transaction/{tx_hash}")
            pretty_print(response.json())

        elif command.startswith("accounts.balance "):
            _, address = command.split(maxsplit=1)
            response = requests.get(f"{API_URL}/accounts/balance/{address}")
            pretty_print(response.json())

        elif command == "accounts.list":
            response = requests.get(f"{API_URL}/accounts/list")
            pretty_print(response.json())

        elif command.startswith("accounts.create"):
            password = getpass("Enter a password for the new wallet: ")
            response = requests.post(f"{API_URL}/accounts/create", json={"password": password})
            pretty_print(response.json())

        elif command.startswith("accounts.import "):
            _, private_key = command.split(maxsplit=1)
            password = getpass("Enter a password to encrypt this wallet: ")
            response = requests.post(f"{API_URL}/accounts/import", json={"private_key": private_key, "password": password})
            pretty_print(response.json())

        elif command.startswith("accounts.export "):
            _, address = command.split(maxsplit=1)
            response = requests.get(f"{API_URL}/accounts/export/{address}")
            pretty_print(response.json())

        elif command.startswith("transactions.create "):
            _, sender, recipient, amount = command.split()
            password = getpass(f"Enter password for {sender}: ")
            response = requests.post(f"{API_URL}/transactions/create", json={
                "sender": sender,
                "recipient": recipient,
                "amount": int(amount),
                "password": password
            })
            pretty_print(response.json())

        elif command.startswith("contracts.deploy "):
            _, bytecode, sender = command.split(maxsplit=2)
            response = requests.post(f"{API_URL}/contracts/deploy", json={"bytecode": bytecode, "sender": sender})
            pretty_print(response.json())

        elif command.startswith("contracts.call "):
            _, contract_address, method_name, sender = command.split(maxsplit=3)
            method_params = {}
            response = requests.post(f"{API_URL}/contracts/call", json={
                "contract_address": contract_address,
                "method_name": method_name,
                "method_params": method_params,
                "sender": sender
            })
            pretty_print(response.json())

        elif command.startswith("fts.create "):
            _, name, symbol, initial_supply, owner = command.split()
            response = requests.post(f"{API_URL}/fts/create", json={
                "name": name,
                "symbol": symbol,
                "initial_supply": int(initial_supply),
                "owner": owner
            })
            pretty_print(response.json())

        elif command.startswith("fts.balance "):
            _, symbol, address = command.split()
            response = requests.get(f"{API_URL}/fts/balance", params={"symbol": symbol, "address": address})
            pretty_print(response.json())

        elif command.startswith("fts.mint "):
            _, symbol, to, amount = command.split()
            response = requests.post(f"{API_URL}/fts/mint", json={
                "symbol": symbol,
                "to": to,
                "amount": int(amount)
            })
            pretty_print(response.json())

        elif command.startswith("fts.transfer "):
            _, symbol, from_address, to_address, amount = command.split()
            response = requests.post(f"{API_URL}/fts/transfer", json={
                "symbol": symbol,
                "from": from_address,
                "to": to_address,
                "amount": int(amount)
            })
            pretty_print(response.json())

        elif command.startswith("fts.burn "):
            _, symbol, from_address, amount = command.split()
            response = requests.post(f"{API_URL}/fts/burn", json={
                "symbol": symbol,
                "from": from_address,
                "amount": int(amount)
            })
            pretty_print(response.json())

        elif command == "exit":
            print("Exiting console...")
            return False

        else:
            print(f"Unknown command: {command}")
        return True

    except ValueError as e:
        print(f"Invalid command format: {e}")
        return True

def main():
    coinbase = fetch_coinbase()
    block_height = fetch_block_height()
    data_directory = fetch_data_directory()

    print("Welcome to your Hadron Node Console!")
    print("")
    print(f"Coinbase: {coinbase}")
    print(f"Block Height: {block_height}")
    print("Modules: accounts : blockchain : contracts : fts : transactions")
    print(f"Data Directory: {data_directory}")
    print("")
    print("Type 'exit' at any time to quit the console.")
    print("")
    
    running = True
    while running:
        command = get_input()
        if command:
            running = handle_command(command)

if __name__ == "__main__":
    main()

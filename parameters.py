# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Parameters and constants used across the protocol. These can be
# overwritten by a config.json file.

import os
import argparse
import json
import multiprocessing

# Network and Node Parameters
parameters = {
    "network_id": 1,
    "max_supply": 1000000,  # Set 0 to infinite supply
    "decimals": 10,  # Number of decimals of the native coin
    "block_reward": 12500000000,  # Coins rewarded per block mined in decimal points
    "epoch": 40320,  # Number of blocks per epoch
    "halving_epoch_interval": 100,  # Number of epochs between halvings
    "block_time": 15,  # In seconds
    "raw_tx_fee": 1,  # Flat fee per raw transaction
    "kb_tx_fee": 100,  # Additional fee per kilobyte of space used
    "block_size": 256,  # Maximum block size in kilobytes
    "data_directory": "./blockchain",  # Folder where the blockchain is stored
    "smart_contracts": True,  # Toggle smart contracts on/off
    "fts": True,  # Toggle fungible tokens on/off
    "nfts": True,  # Toggle non-fungible tokens on/off
    "system_account": '0000000000000000000000000000000000000000', # Don't change unless you really know what you're doing!
    
    # Difficulty-related parameters
    "initial_difficulty": 150000000,  # Initial difficulty level for genesis block
    "difficulty_adjustment_period": 4, # Number of blocks between difficulty adjustments
    "max_difficulty_increase": 1.005, # Maximum difficulty increase per adjustment
    "max_difficulty_decrease": 0.995, # Maximum difficulty decrease per adjustment

    # Node-specific parameters
    "host": "0.0.0.0",
    "port": 5000,
    "p2p_host": "0.0.0.0",
    "p2p_port": 5001,
    "log_file": "blockchain.log",
    "miner_wallet_address": "d95c02123362817f0b556e82f5d4ab3c0c2510f4",  # Default to the zero address
    
    # Node storage settings
    "node_storage_full": 0,  # Number of blocks stored by FULL nodes
    "node_storage_access": 40320,  # Number of blocks stored by ACCESS nodes
    "node_storage_light": 240,  # Number of blocks stored by LIGHT nodes
    
     # Miner-specific parameters
    "cpu_count": 1,  # Number of CPUs to be used; set to 0 will default to 1
    "sleep_time": 0,  # Time to sleep between mining attempts (set to 0 to remove sleep)
    "memory_usage": 8,  # Amount of memory to allocate per thread in MB; set to 0 will default to 4MB

    # Pre-funding allocations
    "allocations": [
    # Example allocation structure
    #    {
    #        "address": "3b6a27bccebfb8b348b87f3ed82f9220c0f86a54",  # Example address
    #        "balance": 5000000000000  # 50,000 coins (in smallest unit, considering 10 decimals)
    #    },
    #    {
    #        "address": "7f6a9dbe8d3bb8f328b67c3ed86e9200c2f86a98",  # Another example address
    #        "balance": 2500000000000  # 25,000 coins (in smallest unit, considering 10 decimals)
    #    }
    ]
}

def load_config_from_file(config_file="config.json"):
    """Loads configuration from an external JSON file."""
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            parameters.update(json.load(file))

def save_config_to_file(config_file="config.json"):
    """Saves the current configuration to an external JSON file."""
    with open(config_file, 'w') as file:
        json.dump(parameters, file, indent=4)

def override_with_env_vars():
    """Overrides config values with environment variables if they exist."""
    for key in parameters.keys():
        if key in os.environ:
            parameters[key] = os.environ[key]

def override_with_cli_args():
    """Overrides config values with CLI arguments if provided."""
    parser = argparse.ArgumentParser(description="Node configuration")
    parser.add_argument("--host", help="Host address")
    parser.add_argument("--port", help="Port number", type=int)
    parser.add_argument("--blockchain_dir", help="Blockchain directory")
    parser.add_argument("--log_file", help="Log file path")
    parser.add_argument("--network_id", help="Network ID", type=int)
    parser.add_argument("--block_reward", help="Block reward", type=int)
    parser.add_argument("--miner_wallet_address", help="Miner wallet address")
    parser.add_argument("--cpu_count", help="CPU count for mining", type=int)
    parser.add_argument("--sleep_time", help="Sleep time between mining attempts", type=float)
    parser.add_argument("--memory_usage", help="Percentage of memory to use for mining", type=int)

    args = parser.parse_args()
    
    if args.host:
        parameters["host"] = args.host
    if args.port:
        parameters["port"] = args.port
    if args.blockchain_dir:
        parameters["data_directory"] = args.blockchain_dir
    if args.log_file:
        parameters["log_file"] = args.log_file

    if args.network_id:
        parameters["network_id"] = args.network_id
    if args.block_reward:
        parameters["block_reward"] = args.block_reward
    if args.miner_wallet_address:
        parameters["miner_wallet_address"] = args.miner_wallet_address
    if args.cpu_count:
        parameters["cpu_count"] = args.cpu_count
    if args.sleep_time:
        parameters["sleep_time"] = args.sleep_time
    if args.memory_usage:
        parameters["memory_usage"] = args.memory_usage

# Initialize Configuration
load_config_from_file()
override_with_env_vars()
override_with_cli_args()

# Adjust CPU count if set to 0
if parameters['cpu_count'] == 0:
    parameters['cpu_count'] = multiprocessing.cpu_count() - 1  # Leave 1 CPU free

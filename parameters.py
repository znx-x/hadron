# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Network genesis parameters, used to generate the genesis block
# and set the network basic configuration thereon.

NETWORK_ID = 1
MAX_SUPPLY = 1000000  # Set 0 to infinite supply
DECIMALS = 10  # Number of decimals of the native coin
BLOCK_REWARD = 12500000000  # Number of coins initially rewarded per block mined in decimal points (eg. If 10 decimals, 12500000000 = 1.25)
APPENDIX_BLOCK_REWARD = 10  # Percentage of total reward paid to appendix blocks (eg. 10 = 10%)
EPOCH = 40320  # Number of blocks per Epoch
HALVING_EPOCH_INTERVAL = 100  # Number of Epochs between halvings, set 0 to disable halving
BLOCK_TIME = 15  # In seconds
RAW_TX_FEE = 1  # Flat fee charged per raw transaction in decimal points (eg. If 10 decimals, 1 = 0.0000000001)
KB_TX_FEE = 100  # Additional fee charged per kilobyte of space used in decimal points (eg. If 10 decimals, 100 = 0.0000000100)
BLOCK_SIZE = 256  # Maximum block size in kilobytes
DATA_DIRECTORY = "/blockchain"  # Folder where the blockchain is stored
SMART_CONTRACTS = True  # Toggle smart contracts on/off
FTS = True  # Toggle fungible tokens on/off
NFTS = True  # Toggle non-fungible tokens on/off

ALLOCATIONS = [
# Examples on how to structure pre-funding allocations to wallets:
#    {
#        "address": "3b6a27bccebfb8b348b87f3ed82f9220c0f86a54",  # Example address
#        "balance": 5000000000000  # 50,000 coins (in smallest unit, considering 10 decimals)
#    },
#    {
#        "address": "7f6a9dbe8d3bb8f328b67c3ed86e9200c2f86a98",  # Another example address
#        "balance": 2500000000000  # 25,000 coins (in smallest unit, considering 10 decimals)
#    }
]

NODE_STORAGE_FULL = 0 # Number of blocks stored by FULL nodes, set 0 to store the full blockchain history
NODE_STORAGE_ACCESS = 40320 # Number of blocks stored by ACCESS nodes, set 0 to store the full blockchain history
NODE_STORAGE_LIGHT = 240 # Number of blocks stored by LIGHT nodes, set 0 to store the full blockchain history

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
MAX_SUPPLY = 1000000  # set 0 to infinite
DECIMALS = 10  # number of decimals for the coin
BLOCK_REWARD = 50
APPENDIX_BLOCK_REWARD = 10
EPOCH = 128  # amount of blocks per epoch
HALVING_EPOCH_INTERVAL = 100  # amount of epochs between halvings, set 0 to disable halving
BLOCK_TIME = 15  # in seconds
TX_FEE = 1  # 10 decimals, so 1 becomes 0.0000000001 coin
BLOCK_SIZE = 64  # maximum size in kilobytes, blocks can also be empty
DATA_DIRECTORY = "/blockchain"  # folder where the blockchain will be stored

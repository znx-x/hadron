# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module handles the mining process, including finding valid
# blocks and earning rewards.

from server import blockchain
from pow import MineH
from consensus import Consensus
from parameters import parameters
from network import P2PNetwork
import threading
import time
import logging

class Miner:
    def __init__(self, wallet_address, p2p_network):
        self.wallet_address = wallet_address
        self.mineh = MineH()
        self.consensus = Consensus()
        self.p2p_network = p2p_network
        self.is_mining = False
        logging.basicConfig(filename=parameters['log_file'], level=logging.INFO)

    def mine(self):
        """Perform the mining process."""
        self.is_mining = True
        while self.is_mining:
            try:
                last_block = blockchain.chain[-1]
                new_block_data = {
                    "index": last_block['index'] + 1,
                    "transactions": blockchain.current_transactions,
                    "previous_hash": blockchain.hash(last_block),
                    "timestamp": time.time(),
                    "difficulty": self.consensus.adjust_difficulty(blockchain.chain[-parameters['epoch']:])
                }

                logging.info(f"Mining new block with difficulty: {new_block_data['difficulty']}")

                nonce = self.mineh.mine(str(new_block_data), new_block_data['difficulty'])
                new_block_data['proof'] = nonce
                new_block_data['hash'] = blockchain.hash(new_block_data)

                if self.validate_block(new_block_data):
                    blockchain.new_block(new_block_data['proof'], new_block_data['previous_hash'])
                    blockchain.state.update_balance(self.wallet_address, parameters['block_reward'])
                    blockchain.state.clear_transactions()
                    self.broadcast_block(new_block_data)
                    logging.info(f"Successfully mined block {new_block_data['index']} with hash {new_block_data['hash']}")

            except Exception as e:
                logging.error(f"Error during mining: {e}")

            time.sleep(parameters['block_time'])  # Wait before mining the next block

    def stop_mining(self):
        """Stops the mining process."""
        self.is_mining = False

    def validate_block(self, block_data):
        """Validate the mined block before adding it to the blockchain."""
        return blockchain.validate_block(block_data)

    def broadcast_block(self, block_data):
        """Broadcast the mined block to the network."""
        logging.info(f"Broadcasting block {block_data['index']} to the network.")
        self.p2p_network.broadcast({'type': 'block', 'block': block_data})

    def start_mining(self):
        """Start the mining process in a separate thread."""
        mining_thread = threading.Thread(target=self.mine)
        mining_thread.start()

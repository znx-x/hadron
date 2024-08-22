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

import logging
import json
import time
import threading
from pow import MineH
from parameters import parameters
from cryptography import Qhash3512


class Miner:
    def __init__(self, wallet_address, p2p_network, blockchain):
        self.wallet_address = wallet_address
        self.mineh = MineH()
        self.p2p_network = p2p_network
        self.blockchain = blockchain
        self.is_mining = True  # Control flag for mining
        logging.basicConfig(filename=parameters['log_file'], level=logging.INFO)

    def mine(self):
        while self.is_mining:
            try:
                last_block = self.blockchain.chain[-1]  # Get the last block in the chain
                previous_hash = last_block.get('block_hash', self.blockchain.hash_block(last_block))

                # Construct the new block data
                new_block_data = {
                    "block_number": last_block['block_number'] + 1,
                    "transactions": self.blockchain.current_transactions,
                    "parent_hash": previous_hash,
                    "state_root": self.blockchain.state.get_root(),
                    "tx_root": self.blockchain.calculate_merkle_root(self.blockchain.current_transactions),
                    "timestamp": time.time(),
                    "difficulty": self.blockchain.calculate_difficulty()
                }

                logging.info(f"Mining new block with difficulty: {new_block_data['difficulty']}")

                # Attempt to mine the block
                nonce, valid_hash = self.mineh.mine(json.dumps(new_block_data, sort_keys=True), new_block_data['difficulty'])
                new_block_data['nonce'] = nonce
                new_block_data['block_hash'] = valid_hash

                # Validate the mined block
                if self.validate_block(new_block_data):
                    block = self.blockchain.new_block(
                        proof=new_block_data['nonce'],
                        previous_hash=new_block_data['parent_hash']
                    )
                    self.blockchain.state.update_balance(self.wallet_address, parameters['block_reward'])
                    self.blockchain.state.clear_transactions()
                    self.broadcast_block(block)
                    logging.info(f"Successfully mined block {new_block_data['block_number']} with hash {new_block_data['block_hash']}")
                else:
                    logging.error(f"Block validation failed for block {new_block_data['block_number']}")

            except Exception as e:
                logging.error(f"Error during mining: {str(e)}")

            time.sleep(parameters['block_time'])

    def stop_mining(self):
        """Stop the mining process."""
        self.is_mining = False

    def validate_block(self, block_data):
        """Validate the newly mined block before adding it to the blockchain."""
        recalculated_hash = self.blockchain.hash_block(block_data)
        return recalculated_hash == block_data['block_hash']

    def broadcast_block(self, block_data):
        """Broadcast the newly mined block to the network."""
        logging.info(f"Broadcasting block {block_data['block_number']} to the network.")
        try:
            self.p2p_network.broadcast({'type': 'block', 'block': block_data})
        except Exception as e:
            logging.error(f"Error broadcasting block: {str(e)}")

    def start_mining(self):
        """Start the mining process in a new thread."""
        mining_thread = threading.Thread(target=self.mine)
        mining_thread.start()

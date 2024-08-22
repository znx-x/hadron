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

class Miner:
    def __init__(self, wallet_address, p2p_network, blockchain):
        self.wallet_address = wallet_address
        self.mineh = MineH()
        self.p2p_network = p2p_network
        self.blockchain = blockchain
        logging.basicConfig(filename=parameters['log_file'], level=logging.INFO)

    def mine(self):
        """Perform the mining process."""
        while True:
            try:
                last_block = self.blockchain.chain[-1]
                previous_hash = last_block.get('block_hash', self.blockchain.hash(last_block))

                # Construct the new block data
                new_block_data = {
                    "block_number": last_block['block_number'] + 1,
                    "transactions": self.blockchain.current_transactions,
                    "parent_hash": previous_hash,
                    "state_root": self.blockchain.state.get_root(),  # Calculate the state root
                    "tx_root": self.blockchain.calculate_merkle_root(self.blockchain.current_transactions),  # Calculate the transaction root
                    "timestamp": time.time(),
                    "difficulty": self.blockchain.calculate_difficulty(),
                    "miner": self.wallet_address,
                    "block_size": 0,  # This will be updated after the nonce and hash are calculated
                    "transaction_count": len(self.blockchain.current_transactions)
                }

                logging.info(f"Mining new block with difficulty: {new_block_data['difficulty']}")

                # Mine and get the nonce and valid hash
                nonce, valid_hash = self.mineh.mine(json.dumps(new_block_data, sort_keys=True), new_block_data['difficulty'])
                new_block_data['nonce'] = nonce
                new_block_data['block_hash'] = valid_hash  # Use the valid hash from the mining process

                # Calculate block size after setting nonce and hash
                new_block_data['block_size'] = len(json.dumps(new_block_data).encode('utf-8'))

                logging.debug(f"New block data: {json.dumps(new_block_data, indent=2)}")

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
                logging.error(f"Error during mining: {e}")

            time.sleep(parameters['block_time'])

    def stop_mining(self):
        """Stops the mining process."""
        self.is_mining = False

    def validate_block(self, block_data):
        """Validate the mined block before adding it to the blockchain."""
        return self.blockchain.validate_block(block_data)

    def broadcast_block(self, block_data):
        """Broadcast the mined block to the network."""
        logging.info(f"Broadcasting block {block_data['block_number']} to the network.")
        self.p2p_network.broadcast({'type': 'block', 'block': block_data})

    def start_mining(self):
        """Start the mining process in a separate thread."""
        mining_thread = threading.Thread(target=self.mine)
        mining_thread.start()

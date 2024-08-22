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
        self.mineh = MineH(memory_size=2**22, memory_update_interval=10)  # Increased memory size
        self.p2p_network = p2p_network
        self.blockchain = blockchain
        self.is_mining = True
        logging.basicConfig(filename=parameters['log_file'], level=logging.INFO)

    def mine(self):
        """Perform the mining process."""
        while self.is_mining:
            try:
                last_block = self.blockchain.chain[-1]
                previous_hash = last_block.get('block_hash', self.blockchain.hash(last_block))

                new_block_data = {
                    "block_number": last_block['block_number'] + 1,
                    "transactions": self.blockchain.current_transactions,
                    "parent_hash": previous_hash,
                    "state_root": self.blockchain.state.get_root(),
                    "tx_root": self.blockchain.calculate_merkle_root(self.blockchain.current_transactions),
                    "timestamp": time.time(),
                    "difficulty": self.blockchain.calculate_difficulty(),
                    "miner": self.wallet_address,
                    "block_size": 0,
                    "transaction_count": len(self.blockchain.current_transactions)
                }

                logging.info(f"→ Starting PoW Hashing (Difficulty: {new_block_data['difficulty']})")

                nonce, valid_hash = self.mineh.mine(json.dumps(new_block_data, sort_keys=True), new_block_data['difficulty'])
                new_block_data['nonce'] = nonce
                new_block_data['block_hash'] = valid_hash

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
                    logging.info(f"→ PoW Submission for Block {new_block_data['block_number']} (Status: ✓ Accepted)")
                    logging.info(f"  Hash: {new_block_data['block_hash']}")
                else:
                    logging.error(f"→ Will attempt new PoW for Block {new_block_data['block_number']}")

            except Exception as e:
                logging.error(f"Error during mining: {e}")

            # Remove or reduce sleep to increase CPU usage
            time.sleep(0.1)  # Lowering sleep time to a small value

    def stop_mining(self):
        """Stops the mining process."""
        self.is_mining = False

    def validate_block(self, block_data):
        """Validate the mined block before adding it to the blockchain."""
        return self.blockchain.validate_block(block_data)

    def broadcast_block(self, block_data):
        """Broadcast the mined block to the network."""
        logging.info(f"→ Broadcasting Block: {block_data['block_number']}")
        self.p2p_network.broadcast({'type': 'block', 'block': block_data})

    def start_mining(self):
        """Start the mining process in a separate thread."""
        mining_thread = threading.Thread(target=self.mine)
        mining_thread.start()

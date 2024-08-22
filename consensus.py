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
import multiprocessing
import psutil
from pow import MineH
from parameters import parameters
from consensus import Consensus  # Ensure correct import

class Miner:
    DEFAULT_MEMORY_USAGE_MB = 4  # Default memory usage per thread if not specified or invalid
    DEFAULT_CPU_COUNT = 1  # Default CPU count if not specified or invalid

    def __init__(self, wallet_address, p2p_network, blockchain):
        self.wallet_address = wallet_address
        self.p2p_network = p2p_network
        self.blockchain = blockchain
        self.consensus = Consensus(p2p_network)
        self.is_mining = True
        logging.basicConfig(filename=parameters['log_file'], level=logging.INFO)

        # Validate and adjust memory usage
        self.memory_usage = self.validate_memory_usage(parameters['memory_usage'])
        
        # Validate and adjust CPU count
        self.cpu_count = self.validate_cpu_count(parameters['cpu_count'])
        
        # Initialize MineH with validated memory usage
        memory_size_bytes = self.memory_usage * (2**20)  # Convert MB to Bytes
        self.mineh = MineH(memory_size=memory_size_bytes, memory_update_interval=10)

    def validate_memory_usage(self, memory_usage_mb):
        """Validate and adjust memory usage based on system availability."""
        total_memory_mb = psutil.virtual_memory().available // (2**20)  # Get available memory in MB
        if memory_usage_mb <= 0 or memory_usage_mb > total_memory_mb:
            logging.warning(f"Invalid or excessive memory usage specified ({memory_usage_mb}MB). Defaulting to {self.DEFAULT_MEMORY_USAGE_MB}MB per thread.")
            return self.DEFAULT_MEMORY_USAGE_MB
        return memory_usage_mb

    def validate_cpu_count(self, cpu_count):
        """Validate and adjust CPU count based on system availability."""
        max_cpus = multiprocessing.cpu_count() - 1  # Leave 1 CPU free for system operations
        if cpu_count <= 0 or cpu_count > max_cpus:
            logging.warning(f"Invalid or excessive CPU count specified ({cpu_count}). Defaulting to {self.DEFAULT_CPU_COUNT} CPU.")
            return self.DEFAULT_CPU_COUNT
        return cpu_count

    def mine(self):
        """Perform the mining process."""
        while self.is_mining:
            try:
                last_block = self.blockchain.chain[-1]
                previous_hash = last_block.get('block_hash', self.blockchain.hash(last_block))

                # Adjust difficulty using the consensus mechanism
                difficulty = self.consensus.adjust_difficulty(self.blockchain)

                new_block_data = {
                    "block_number": last_block['block_number'] + 1,
                    "transactions": self.blockchain.current_transactions,
                    "parent_hash": previous_hash,
                    "state_root": self.blockchain.state.get_root(),
                    "tx_root": self.blockchain.calculate_merkle_root(self.blockchain.current_transactions),
                    "timestamp": time.time(),
                    "difficulty": difficulty,
                    "miner": self.wallet_address,
                    "block_size": 0,
                    "transaction_count": len(self.blockchain.current_transactions)
                }

                start_time = time.time()
                nonce, valid_hash = self.mineh.mine(json.dumps(new_block_data, sort_keys=True), difficulty)
                end_time = time.time()
                
                # Calculate hashrate
                self.total_hashes += nonce
                self.update_hashrate()

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
            except Exception as e:
                logging.error(f"Error during mining: {e}")

            time.sleep(parameters['sleep_time'])  # Use configurable sleep time

    def update_hashrate(self):
        current_time = time.time()
        time_diff = current_time - self.last_hashrate_calc
        if time_diff > 0:
            self.hashrate = self.total_hashes / time_diff
            self.total_hashes = 0
            self.last_hashrate_calc = current_time

    def get_hashrate(self):
        """Return the current hashrate."""
        return self.hashrate

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
        """Start the mining process using the specified number of CPUs."""
        threads = []
        for _ in range(self.cpu_count):
            mining_thread = threading.Thread(target=self.mine)
            threads.append(mining_thread)
            mining_thread.start()

        for thread in threads:
            thread.join()  # Ensure all threads are executed

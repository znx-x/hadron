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

import json
import logging
import time
import threading
import multiprocessing
import psutil
from pow import MineH
from parameters import parameters
from consensus import Consensus

class Miner:
    def __init__(self, wallet_address, p2p_network, blockchain):
        self.wallet_address = wallet_address
        self.p2p_network = p2p_network
        self.blockchain = blockchain
        
        self.is_mining = True
        self.total_hashes = 0
        self.hashrate = 0
        self.last_hashrate_calc = time.time()
        logging.basicConfig(filename=parameters['log_file'], level=logging.INFO)

        self.memory_usage = self.validate_memory_usage(parameters['memory_usage'])
        self.cpu_count = self.validate_cpu_count(parameters['cpu_count'])
        memory_size_bytes = self.memory_usage * (2**20)  # Convert MB to Bytes
        self.mineh = MineH(memory_size=memory_size_bytes, memory_update_interval=10)

        self.consensus = Consensus(p2p_network, blockchain, self.mineh)

    def validate_memory_usage(self, memory_usage_mb):
        total_memory_mb = psutil.virtual_memory().available // (2**20)
        if memory_usage_mb <= 0 or memory_usage_mb > total_memory_mb:
            logging.warning(f"Invalid memory usage specified ({memory_usage_mb}MB). Defaulting to 4MB per thread.")
            return 4
        return memory_usage_mb

    def validate_cpu_count(self, cpu_count):
        max_cpus = multiprocessing.cpu_count() - 1
        if cpu_count <= 0 or cpu_count > max_cpus:
            logging.warning(f"Invalid CPU count specified ({cpu_count}). Defaulting to 1 CPU.")
            return 1
        return cpu_count

    def mine(self):
        scale_factor = 10**8
        while self.is_mining:
            try:
                last_block = self.blockchain.chain[-1]
                previous_hash = last_block.get('block_hash', self.blockchain.hash(last_block))
                logging.info(f"Previous block hash: {previous_hash}")
                new_block_data = {
                    "block_number": last_block['block_number'] + 1,
                    "transactions": self.blockchain.current_transactions,
                    "parent_hash": previous_hash,
                    "state_root": self.blockchain.state.get_root(),
                    "tx_root": self.blockchain.calculate_merkle_root(self.blockchain.current_transactions),
                    "timestamp": time.time(),
                    "difficulty": self.consensus.adjust_difficulty(self.blockchain.chain),
                    "miner": self.wallet_address,
                    "block_size": 0,
                    "transaction_count": len(self.blockchain.current_transactions)
                }
#                logging.info(f"New block data with parent_hash: {new_block_data}")
#                logging.info(f"New block data created: {new_block_data}")

                nonce, valid_hash = self.mineh.mine(json.dumps(new_block_data, sort_keys=True), new_block_data['difficulty'] // scale_factor)
                self.total_hashes += nonce
                self.update_hashrate()

                new_block_data['nonce'] = nonce
                new_block_data['block_hash'] = valid_hash
                new_block_data['block_size'] = len(json.dumps(new_block_data).encode('utf-8'))

#                logging.info(f"Updated block data with nonce and hash: {new_block_data}")

                if 'block_number' not in new_block_data:
                    logging.error(f"block_number is missing from new_block_data: {new_block_data}")

                if self.validate_block(new_block_data):
                    reward_transaction = {
                        "tx_hash": self.blockchain.hash_transaction({
                            "sender": parameters['system_account'],
                            "recipient": self.wallet_address,
                            "value": parameters['block_reward'],
                            "fee": 0,
                            "nonce": 0,
                            "input": "",
                            "timestamp": time.time(),
                            "block_number": new_block_data['block_number']
                        }),
                        "sender": parameters['system_account'],
                        "recipient": self.wallet_address,
                        "value": parameters['block_reward'],
                        "fee": 0,
                        "nonce": 0,
                        "size": 0,
                        "input": "",
                        "timestamp": time.time(),
                        "block_number": new_block_data['block_number']
                    }
                    
                    self.blockchain.current_transactions.append(reward_transaction)
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

            time.sleep(parameters['sleep_time'])

    def update_hashrate(self):
        current_time = time.time()
        time_diff = current_time - self.last_hashrate_calc
        if time_diff > 0:
            self.hashrate = self.total_hashes / time_diff
            self.total_hashes = 0
            self.last_hashrate_calc = current_time

    def get_hashrate(self):
        return self.hashrate

    def stop_mining(self):
        self.is_mining = False

    def validate_block(self, block_data):
        return self.blockchain.validate_block(block_data)

    def broadcast_block(self, block_data):
        logging.info(f"→ Broadcasting Block: {block_data['block_number']}")
        self.p2p_network.broadcast({'type': 'block', 'block': block_data})

    def start_mining(self):
        threads = []
        for _ in range(self.cpu_count):
            mining_thread = threading.Thread(target=self.mine)
            threads.append(mining_thread)
            mining_thread.start()

        for thread in threads:
            thread.join()

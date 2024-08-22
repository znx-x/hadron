# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

import json
import threading
import time
import logging
from cryptography import Qhash3512
from parameters import parameters
from database import BlockchainDatabase
from state import BlockchainState
from miner import Miner
from network import P2PNetwork
from consensus import Consensus

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

class Blockchain:
    def __init__(self):
        """Initialize the blockchain node with state, database, miner, and network."""
        self.chain = []
        self.current_transactions = []
        self.state = BlockchainState()
        self.db = BlockchainDatabase()
        self.miner_wallet_address = parameters.get("miner_wallet_address", "0000000000000000000000000000000000000000")
        self.p2p_network = P2PNetwork()

        # Initialize Consensus with the current blockchain and network
        self.consensus = Consensus(self.p2p_network, self, None)  # Passing `None` for `mineh` for now

        # Initialize the miner with consensus
        self.miner = Miner(self.miner_wallet_address, self.p2p_network, self)

        # After Miner is initialized, update the consensus object with the miner's `mineh`
        self.consensus.mineh = self.miner.mineh

        logging.info("Blockchain node initializing...")
        self.load_chain()

        if len(self.chain) == 0:
            self.new_block(previous_hash='1', proof=100)
            logging.info("Genesis block created...")
            time.sleep(2)

        logging.info("Blockchain loaded.")

    def load_chain(self):
        """Load the blockchain from the database."""
        block = self.db.get_last_block()
        chain = []

        while block:
            chain.append(block)
            block = self.db.get_block(block['parent_hash'])

        chain.reverse()
        self.chain = chain
        logging.info(f"{len(self.chain)} blocks loaded from the database.")

    def new_block(self, proof, previous_hash=None):
        """Create a new block and add it to the blockchain."""
        block = {
            'block_number': len(self.chain) + 1,
            'parent_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else '1',
            'state_root': self.state.get_root(),
            'tx_root': self.calculate_merkle_root(self.current_transactions),
            'difficulty': self.consensus.adjust_difficulty(self.chain),
            'nonce': proof,
            'timestamp': time.time(),
            'miner': self.miner_wallet_address,
            'block_size': 0,  # Placeholder, will be updated later
            'transaction_count': len(self.current_transactions),
            'transactions': self.current_transactions
        }

        # Calculate block size
        block['block_size'] = len(json.dumps(block).encode('utf-8'))

        self.current_transactions = []
        block_hash = self.hash(block)
        block['block_hash'] = block_hash
        self.chain.append(block)
        self.db.save_block(block_hash, block)
        logging.info(f"→ Update Network Height: {block['block_number']}")
        self.state.clear_transactions()
        return block

    def calculate_merkle_root(self, transactions):
        """Calculate the Merkle root of the transaction list."""
        if not transactions:
            return None

        def hash_pair(a, b):
            return Qhash3512.generate_hash(a + b)

        transaction_hashes = [Qhash3512.generate_hash(json.dumps(tx, sort_keys=True)) for tx in transactions]

        while len(transaction_hashes) > 1:
            if len(transaction_hashes) % 2 == 1:
                transaction_hashes.append(transaction_hashes[-1])
            transaction_hashes = [hash_pair(transaction_hashes[i], transaction_hashes[i + 1]) for i in range(0, len(transaction_hashes), 2)]

        return transaction_hashes[0]

    def calculate_block_size(self):
        """Calculate the size of the current block."""
        if not self.chain:
            return 0
        return len(json.dumps(self.chain[-1]).encode('utf-8'))

    def new_transaction(self, sender, recipient, amount, text=None, token=None, nft=None):
        """Create a new transaction and add it to the current transaction list."""
        fee = self.calculate_fee(amount, text)
        total_cost = amount + fee

        if self.state.get_balance(sender) >= total_cost:
            transaction = {
                'sender': sender,
                'recipient': recipient,
                'value': amount,
                'size': len(text.encode('utf-8')) if text else 0,
                'fee': fee,
                'nonce': self.state.get_nonce(sender),
                'input': text if text else "",
                'text': text if text else "",
                'token': token,
                'nft': nft,
                'timestamp': time.time()
            }
            self.current_transactions.append(transaction)
            self.state.update_balance(sender, -total_cost)
            self.state.update_balance(recipient, amount)
            self.state.update_balance(self.miner_wallet_address, fee)
            logging.info(f"Transaction added: {transaction}")
            return f"Transaction will be added to Block {len(self.chain) + 1}"
        return "Insufficient funds"

    def calculate_fee(self, amount, text=None):
        """Calculate the fee for a transaction based on its size."""
        base_fee = parameters['raw_tx_fee'] / (10 ** parameters['decimals'])
        additional_fee = 0
        if text:
            text_size = len(text.encode('utf-8'))
            additional_fee = (parameters['kb_tx_fee'] * text_size) / (10 ** parameters['decimals'])
        return base_fee + additional_fee

    def hash(self, block):
        """Generate a hash for a block, ensuring all data is included."""
        # Serialize block data with exact formatting and order
        block_data = json.dumps({
            'block_number': block['block_number'],
            'parent_hash': block['parent_hash'],
            'state_root': block['state_root'],
            'tx_root': block['tx_root'],
            'difficulty': block['difficulty'],
            'nonce': block['nonce'],
            'timestamp': block['timestamp'],
            'miner': block['miner'],
            'block_size': block['block_size'],
            'transaction_count': block['transaction_count'],
            'transactions': block.get('transactions', [])
        }, sort_keys=True)

        # Include memory data in the block hash calculation
        memory_data = self.miner.mineh.memory[:self.miner.mineh.memory_size]
        combined_data = f"{block_data}{memory_data.decode('latin1')}"

        # Calculate and return the hash
        recalculated_hash = Qhash3512.generate_hash(combined_data)
        return recalculated_hash

    def validate_block(self, block):
        """Validate the integrity and proof-of-work of a block."""
        last_block = self.chain[-1]

        if block['parent_hash'] != last_block['block_hash']:
            return False

        recalculated_hash = self.hash(block)

        # Pass the scaled difficulty to is_valid_hash
        if not Qhash3512.is_valid_hash(recalculated_hash, block['difficulty']):
            return False

        logging.info(f"→ Validated PoW for Block: {block['block_number']}")
        return True

    def mine_block(self):
        """Trigger the mining process for a new block."""
        return self.miner.mine()

    def run_node(self, shutdown_flag):
        """Run the blockchain node, handling mining and networking."""
        self.mining_thread = threading.Thread(target=self.consensus_algorithm, args=(shutdown_flag,))
        self.mining_thread.start()

    def consensus_algorithm(self, shutdown_flag):
        """Continuously mine blocks as long as the shutdown flag is not set."""
        while not shutdown_flag.is_set():
            self.mine_block()
            time.sleep(parameters['block_time'])

    def stop_node(self):
        """Stop the blockchain node and clean up resources."""
        logging.info("Stopping blockchain node...")
        if self.mining_thread is not None:
            self.mining_thread.join()
        logging.info("Blockchain node stopped.")

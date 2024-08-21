# node.py

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
from cryptography import Qhash3512
from parameters import parameters
from database import BlockchainDatabase
from state import BlockchainState
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.state = BlockchainState()
        self.db = BlockchainDatabase()
        self.miner_wallet_address = parameters.get("miner_wallet_address", "0000000000000000000000000000000000000000")
        logging.info("Blockchain node initializing...")
        self.load_chain()
        logging.info("Blockchain loaded.")
        self.new_block(previous_hash='1', proof=100)

    def load_chain(self):
        """Load the existing blockchain from the database."""
        block = self.db.get_last_block()
        while block:
            self.chain.append(block)
            block = self.db.get_block(block['block_hash'])
        logging.info(f"{len(self.chain)} blocks loaded from the database.")

    def new_block(self, proof, previous_hash=None):
        """Create a new block and reset the transaction pool."""
        block = {
            'block_number': len(self.chain) + 1,
            'parent_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else '1',
            'state_root': self.state.get_root(),  # Assuming state has a method to get its root
            'tx_root': self.calculate_merkle_root(self.current_transactions),
            'receipt_root': '',  # This would need to be calculated from receipts if implemented
            'logs_bloom': '',  # Placeholder, would be calculated from transaction logs if needed
            'difficulty': self.calculate_difficulty(),  # Placeholder, depending on your PoW logic
            'nonce': '',  # Placeholder, usually found after PoW
            'mix_hash': '',  # Placeholder, depending on your PoW algorithm
            'timestamp': time.time(),
            'miner': self.miner_wallet_address,
            'block_size': self.calculate_block_size(),  # Assuming you have logic to calculate the size
            'transaction_count': len(self.current_transactions),
            'transactions': self.current_transactions
        }

        self.current_transactions = []
        self.chain.append(block)
        block_hash = self.hash(block)
        self.db.save_block(block_hash, block)
        logging.info(f"New block mined: {block_hash} at height {block['block_number']}")
        self.state.clear_transactions()
        return block

    def calculate_merkle_root(self, transactions):
        """Calculate the Merkle root of transactions in the block."""
        # Implement your Merkle root calculation here
        return ''

    def calculate_difficulty(self):
        """Calculate the difficulty for the current block."""
        # Implement your difficulty adjustment algorithm here
        return 0

    def calculate_block_size(self):
        """Calculate the size of the current block."""
        # Implement your block size calculation here
        return 0

    def new_transaction(self, sender, recipient, amount, text=None, token=None, nft=None):
        """Create a new transaction, with optional text, token, or NFT transfers."""
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
        """Calculate the transaction fee based on the amount and text size."""
        base_fee = parameters['raw_tx_fee'] / (10 ** parameters['decimals'])
        additional_fee = 0
        if text:
            text_size = len(text.encode('utf-8'))
            additional_fee = (parameters['kb_tx_fee'] * text_size) / (10 ** parameters['decimals'])
        return base_fee + additional_fee

    @staticmethod
    def hash(block):
        """Generate a hash for a block."""
        block_string = json.dumps(block, sort_keys=True).encode()
        return Qhash3512.generate_hash(block_string.decode())

    def mine_block(self):
        """Mine a new block using the Proof-of-Work algorithm."""
        last_block = self.chain[-1]
        proof = self.proof_of_work(last_block['proof'])
        if self.miner_wallet_address != "0000000000000000000000000000000000000000":
            self.state.update_balance(self.miner_wallet_address, parameters['block_reward'])
        previous_hash = self.hash(last_block)
        block = self.new_block(proof, previous_hash)
        self.state.update_state(block)
        return block

    def proof_of_work(self, last_proof):
        """Simple Proof-of-Work algorithm."""
        proof = 0
        last_hash = Qhash3512.generate_hash(str(last_proof))
        while self.valid_proof(last_hash, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_hash, proof):
        """Validate the proof by checking if it meets the difficulty criteria."""
        guess = f'{last_hash}{proof}'.encode()
        guess_hash = Qhash3512.generate_hash(guess.decode())
        return guess_hash[:4] == "0000"

    def validate_block(self, block):
        """Validate a block before adding it to the chain."""
        last_block = self.chain[-1]
        if block['previous_hash'] != self.hash(last_block):
            return False
        if not self.valid_proof(block['proof'], last_block['proof']):
            return False
        return True

    def run_node(self):
        """Run the node and handle the consensus algorithm."""
        miner_thread = threading.Thread(target=self.consensus_algorithm)
        miner_thread.start()

    def consensus_algorithm(self):
        """Continuously mine blocks and maintain consensus."""
        while True:
            time.sleep(parameters['block_time'])
            self.mine_block()

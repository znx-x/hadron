import json
import threading
import time
import math
from hashlib import sha256
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

        if len(self.chain) == 0:
            # Create genesis block with proof 100
            self.new_block(previous_hash='1', proof=100)
            logging.info("Genesis block created.")

        logging.info("Blockchain loaded.")

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
            'state_root': self.state.get_root(),
            'tx_root': self.calculate_merkle_root(self.current_transactions),
            'difficulty': self.calculate_difficulty(),
            'nonce': proof,  # Set the proof of work result as the nonce
            'timestamp': time.time(),
            'miner': self.miner_wallet_address,
            'block_size': self.calculate_block_size(),
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
        if not transactions:
            return None

        def hash_pair(a, b):
            return sha256((a + b).encode('utf-8')).hexdigest()

        # Start with the transactions' hashes
        transaction_hashes = [sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest() for tx in transactions]

        while len(transaction_hashes) > 1:
            if len(transaction_hashes) % 2 == 1:
                transaction_hashes.append(transaction_hashes[-1])
            transaction_hashes = [hash_pair(transaction_hashes[i], transaction_hashes[i + 1]) for i in range(0, len(transaction_hashes), 2)]

        return transaction_hashes[0]

    def calculate_difficulty(self):
        """Calculate the difficulty for the current block."""
        if len(self.chain) < 2:
            return parameters['initial_difficulty']
        
        last_block = self.chain[-1]
        previous_block = self.chain[-2]

        # Calculate the time taken to mine the last block
        actual_time = last_block['timestamp'] - previous_block['timestamp']
        target_time = parameters['block_time']

        if actual_time < target_time * 0.75:
            return last_block['difficulty'] + 1
        elif actual_time > target_time * 1.25:
            return max(1, last_block['difficulty'] - 1)
        else:
            return last_block['difficulty']

    def calculate_block_size(self):
        """Calculate the size of the current block."""
        if not self.chain:
            return 0
        return len(json.dumps(self.chain[-1]).encode('utf-8'))

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
        proof = self.proof_of_work(last_block['nonce'])
        if self.miner_wallet_address != "0000000000000000000000000000000000000000":
            self.state.update_balance(self.miner_wallet_address, parameters['block_reward'])
        previous_hash = self.hash(last_block)
        block = self.new_block(proof, previous_hash)
        self.state.update_state(block)
        return block

    def proof_of_work(self, last_nonce):
        """Simple Proof-of-Work algorithm."""
        proof = 0
        last_hash = Qhash3512.generate_hash(str(last_nonce))
        while self.valid_proof(last_hash, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_hash, proof):
        """Validate the proof by checking if it meets the difficulty criteria."""
        guess = f'{last_hash}{proof}'.encode()
        guess_hash = Qhash3512.generate_hash(guess.decode())
        return guess_hash[:parameters['difficulty_prefix']] == "0" * parameters['difficulty_prefix']

    def validate_block(self, block):
        """Validate a block before adding it to the chain."""
        if not self.chain:
            return False
        last_block = self.chain[-1]
        if block['parent_hash'] != self.hash(last_block):
            return False
        if not self.valid_proof(block['nonce'], last_block['nonce']):
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

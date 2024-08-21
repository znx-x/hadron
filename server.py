# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Blockchain node module.

import json
import math
from cryptography import Qhash3512
from parameters import parameters
from state import BlockchainState
from database import BlockchainDatabase
import time
import threading

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.state = BlockchainState()
        self.db = BlockchainDatabase()
        self.miner_wallet_address = parameters.get("miner_wallet_address", "0000000000000000000000000000000000000000")
        self.load_chain()
        self.new_block(previous_hash='1', proof=100)

    def load_chain(self):
        """Load the existing blockchain from the database."""
        block = self.db.get_last_block()
        while block:
            self.chain.append(block)
            block = self.db.get_block(block['index'] + 1)

    def new_block(self, proof, previous_hash=None):
        """Create a new block and reset the transaction pool."""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        self.db.save_block(block['index'], block)
        self.state.clear_transactions()
        return block

    def new_transaction(self, sender, recipient, amount, text=None, token=None, nft=None):
        """Create a new transaction, with optional text, token, or NFT transfers."""
        fee = self.calculate_fee(amount, text)
        total_cost = amount + fee

        if self.state.get_balance(sender) >= total_cost:
            transaction = {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'fee': fee,
                'text': text if text else "",
                'token': token,
                'nft': nft
            }
            self.current_transactions.append(transaction)
            self.state.update_balance(sender, -total_cost)
            self.state.update_balance(recipient, amount)
            self.state.update_balance(self.miner_wallet_address, fee)
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

blockchain = Blockchain()

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Blockchain node module.

# server.py

import json
import math
from cryptography import Qhash3512
from parameters import BLOCK_TIME, BLOCK_REWARD, TX_FEE, DECIMALS, update_balance
import time
import threading

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.balances = {}
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount, text=None):
        fee = self.calculate_fee(amount, text)
        total_cost = amount + fee

        if update_balance(sender, -total_cost, self) >= 0:
            transaction = {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'fee': fee,
                'text': text if text else ""
            }
            self.current_transactions.append(transaction)
            update_balance(recipient, amount, self)
            update_balance("miner_wallet_address", fee, self)  # Fee goes to miner
            return f"Transaction will be added to Block {len(self.chain) + 1}"
        return "Insufficient funds"

    def calculate_fee(self, amount, text=None):
        base_fee = TX_FEE / (10 ** DECIMALS)
        additional_fee = 0
        if text:
            text_size = len(text.encode('utf-8'))
            additional_fee = (TX_FEE * text_size) / (10 ** DECIMALS)
        return base_fee + additional_fee

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return Qhash3512.generate_hash(block_string.decode())

    def mine_block(self):
        last_block = self.chain[-1]
        proof = self.proof_of_work(last_block['proof'])
        update_balance("miner_wallet_address", BLOCK_REWARD, self)
        previous_hash = self.hash(last_block)
        block = self.new_block(proof, previous_hash)
        return block

    def proof_of_work(self, last_proof):
        proof = 0
        last_hash = Qhash3512.generate_hash(str(last_proof))
        while self.valid_proof(last_hash, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_hash, proof):
        guess = f'{last_hash}{proof}'.encode()
        guess_hash = Qhash3512.generate_hash(guess.decode())
        return guess_hash[:4] == "0000"

    def run_node(self):
        miner_thread = threading.Thread(target=self.consensus_algorithm)
        miner_thread.start()

    def consensus_algorithm(self):
        while True:
            time.sleep(BLOCK_TIME)
            self.mine_block()

blockchain = Blockchain()

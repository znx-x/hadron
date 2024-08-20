from cryptography import quantumhash
from parameters import BLOCK_TIME, BLOCK_REWARD, update_balance
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

    def new_transaction(self, sender, recipient, amount):
        if update_balance(sender, -amount, self) >= 0:
            self.current_transactions.append({
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
            })
            update_balance(recipient, amount, self)
            return f"Transaction will be added to Block {len(self.chain) + 1}"
        return "Insufficient funds"

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return quantumhash(block_string.decode())

    def mine_block(self):
        last_block = self.chain[-1]
        proof = self.proof_of_work(last_block['proof'])
        update_balance("miner_wallet_address", BLOCK_REWARD, self)
        previous_hash = self.hash(last_block)
        block = self.new_block(proof, previous_hash)
        return block

    def proof_of_work(self, last_proof):
        proof = 0
        last_hash = quantumhash(str(last_proof))
        while self.valid_proof(last_hash, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_hash, proof):
        guess = f'{last_hash}{proof}'.encode()
        guess_hash = quantumhash(guess.decode())
        return guess_hash[:4] == "0000"

    def run_node(self):
        # Add threading to run the node
        miner_thread = threading.Thread(target=self.consensus_algorithm)
        miner_thread.start()

    def consensus_algorithm(self):
        while True:
            time.sleep(BLOCK_TIME)
            self.mine_block()

blockchain = Blockchain()

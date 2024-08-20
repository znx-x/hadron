# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Manages the blockchain's state, including balances, transaction
# pools, and pending transactions.

class BlockchainState:
    def __init__(self):
        self.balances = {}
        self.transaction_pool = []

    def get_balance(self, address):
        return self.balances.get(address, 0)

    def update_balance(self, address, amount):
        if address in self.balances:
            self.balances[address] += amount
        else:
            self.balances[address] = amount

    def add_transaction(self, transaction):
        self.transaction_pool.append(transaction)

    def clear_transactions(self):
        self.transaction_pool = []

    def get_transactions(self):
        return self.transaction_pool

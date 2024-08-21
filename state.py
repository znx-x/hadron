# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Manages the blockchain's state, including balances, transaction pools,
# smart contracts, tokens, and NFTs.

from collections import defaultdict

class BlockchainState:
    def __init__(self):
        self.balances = defaultdict(int)
        self.accounts = set()  # Index of all accounts with non-zero balances
        self.transaction_pool = []
        self.contracts = {}
        self.tokens = {}
        self.nfts = {}

    def update_balance(self, address, amount):
        """Update the balance of an account."""
        if amount < 0 and self.balances[address] + amount < 0:
            raise ValueError("Insufficient funds.")
        
        if self.balances[address] == 0 and amount > 0:
            self.accounts.add(address)
        self.balances[address] += amount
        
        if self.balances[address] == 0:
            self.accounts.discard(address)

    def get_balance(self, address):
        """Get the balance of a specific account."""
        return self.balances[address]

    def add_transaction(self, transaction):
        """Add a transaction to the pool if valid."""
        if self.validate_transaction(transaction):
            self.transaction_pool.append(transaction)
        else:
            raise ValueError("Invalid transaction.")

    def validate_transaction(self, transaction):
        """Validate a transaction before adding it to the pool."""
        sender_balance = self.get_balance(transaction['sender'])
        return sender_balance >= transaction['amount']

    def remove_transactions(self, transactions):
        """Remove transactions from the pool that have been included in a block."""
        for tx in transactions:
            if tx in self.transaction_pool:
                self.transaction_pool.remove(tx)

    def deploy_contract(self, address, contract_code):
        """Deploy a new smart contract to the blockchain."""
        if address in self.contracts:
            raise ValueError("Contract already exists at this address.")
        self.contracts[address] = contract_code

    def execute_contract(self, address, data):
        """Execute a smart contract."""
        if address not in self.contracts:
            raise ValueError("Contract not found.")
        contract_code = self.contracts[address]
        # Execute the contract logic here (using the VM module)
        result = self.execute_contract_logic(contract_code, data)
        return result

    def issue_token(self, token_id, initial_supply):
        """Issue a new fungible token."""
        if token_id in self.tokens:
            raise ValueError("Token already exists.")
        self.tokens[token_id] = {
            "supply": initial_supply,
            "holders": defaultdict(int)
        }

    def transfer_token(self, token_id, from_address, to_address, amount):
        """Transfer fungible tokens between accounts."""
        if self.tokens[token_id]['holders'][from_address] < amount:
            raise ValueError("Insufficient token balance.")
        self.tokens[token_id]['holders'][from_address] -= amount
        self.tokens[token_id]['holders'][to_address] += amount

    def mint_nft(self, nft_id, owner_address):
        """Mint a new NFT."""
        if nft_id in self.nfts:
            raise ValueError("NFT already exists.")
        self.nfts[nft_id] = owner_address

    def transfer_nft(self, nft_id, from_address, to_address):
        """Transfer an NFT between accounts."""
        if self.nfts[nft_id] != from_address:
            raise ValueError("Transfer not authorized by the current owner.")
        self.nfts[nft_id] = to_address

    def execute_contract_logic(self, contract_code, data):
        """Placeholder for executing contract logic (to be integrated with VM)."""
        # Actual implementation would interact with the VM module
        return f"Executed contract with data: {data}"

    def reset_transaction_pool(self):
        """Clear all pending transactions from the transaction pool."""
        self.transaction_pool = []

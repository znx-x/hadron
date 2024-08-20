# fts.py
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module handles the creation and management of fungible tokens (FTs).

class FungibleToken:
    def __init__(self, name, symbol, initial_supply, decimals=18):
        self.name = name
        self.symbol = symbol
        self.decimals = decimals
        self.total_supply = initial_supply * (10 ** decimals)
        self.balances = {}

    def mint(self, account, amount):
        """Mint new tokens to a specified account."""
        amount_with_decimals = amount * (10 ** self.decimals)
        if account in self.balances:
            self.balances[account] += amount_with_decimals
        else:
            self.balances[account] = amount_with_decimals
        self.total_supply += amount_with_decimals

    def transfer(self, sender, recipient, amount):
        """Transfer tokens from one account to another."""
        amount_with_decimals = amount * (10 ** self.decimals)
        if sender not in self.balances or self.balances[sender] < amount_with_decimals:
            return False  # Insufficient balance
        self.balances[sender] -= amount_with_decimals
        if recipient in self.balances:
            self.balances[recipient] += amount_with_decimals
        else:
            self.balances[recipient] = amount_with_decimals
        return True

    def balance_of(self, account):
        """Return the balance of a specified account."""
        return self.balances.get(account, 0) / (10 ** self.decimals)

    def burn(self, account, amount):
        """Burn (destroy) tokens from a specified account."""
        amount_with_decimals = amount * (10 ** self.decimals)
        if account not in self.balances or self.balances[account] < amount_with_decimals:
            return False  # Insufficient balance
        self.balances[account] -= amount_with_decimals
        self.total_supply -= amount_with_decimals
        return True

# Example usage
if __name__ == "__main__":
    token = FungibleToken("ExampleToken", "EXT", 1000)
    token.mint("alice", 500)
    token.transfer("alice", "bob", 100)
    print(f"Alice's balance: {token.balance_of('alice')}")
    print(f"Bob's balance: {token.balance_of('bob')}")

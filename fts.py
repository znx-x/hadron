# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

class FungibleToken:
    def __init__(self, name, symbol, initial_supply, max_supply=None, mintable=True, pausable=True, owner=None):
        self.name = name
        self.symbol = symbol
        self.total_supply = initial_supply
        self.max_supply = max_supply if max_supply else float('inf')
        self.mintable = mintable
        self.pausable = pausable
        self.owner = owner
        self.balances = {owner: initial_supply}
        self.allowances = {}  # To manage allowances for spending
        self.paused = False

    def mint(self, to, amount):
        if not self.mintable:
            raise Exception("Token is not mintable.")
        if self.total_supply + amount > self.max_supply:
            raise Exception("Minting exceeds max supply.")
        if self.paused:
            raise Exception("Token is paused.")
        self.total_supply += amount
        self.balances[to] = self.balances.get(to, 0) + amount

    def transfer(self, from_address, to_address, amount):
        if self.paused:
            raise Exception("Token is paused.")
        if self.balances.get(from_address, 0) < amount:
            raise Exception("Insufficient balance.")
        self.balances[from_address] -= amount
        self.balances[to_address] = self.balances.get(to_address, 0) + amount

    def burn(self, from_address, amount):
        if self.balances.get(from_address, 0) < amount:
            raise Exception("Insufficient balance.")
        self.balances[from_address] -= amount
        self.total_supply -= amount

    def balance_of(self, address):
        return self.balances.get(address, 0)

    def approve(self, owner, spender, amount):
        if owner not in self.allowances:
            self.allowances[owner] = {}
        self.allowances[owner][spender] = amount

    def allowance(self, owner, spender):
        return self.allowances.get(owner, {}).get(spender, 0)

    def transfer_from(self, spender, from_address, to_address, amount):
        if self.paused:
            raise Exception("Token is paused.")
        if self.allowance(from_address, spender) < amount:
            raise Exception("Allowance exceeded.")
        if self.balances.get(from_address, 0) < amount:
            raise Exception("Insufficient balance.")
        self.allowances[from_address][spender] -= amount
        self.transfer(from_address, to_address, amount)

    def transfer_ownership(self, new_owner):
        if self.owner is None:
            raise Exception("Token is not owned by anyone.")
        self.owner = new_owner

    def pause(self):
        if not self.pausable:
            raise Exception("Token is not pausable.")
        self.paused = True

    def unpause(self):
        if not self.pausable:
            raise Exception("Token is not pausable.")
        self.paused = False

    def total_supply(self):
        return self.total_supply

    def transfer_ownership(self, new_owner):
        """Transfers ownership of the token to a new owner."""
        if self.owner is None:
            raise Exception("Token is not owned by anyone.")
        self.owner = new_owner

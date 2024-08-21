# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

class NonFungibleToken:
    def __init__(self, name, symbol, owner):
        self.name = name
        self.symbol = symbol
        self.owner = owner
        self.tokens = {}
        self.token_owners = {}
        self.approvals = {}
        self.operators = {}

    def mint(self, to, token_id, metadata):
        if token_id in self.tokens:
            raise Exception("Token ID already exists")
        self.tokens[token_id] = metadata
        self.token_owners[token_id] = to

    def transfer(self, from_address, to_address, token_id):
        if self.token_owners.get(token_id) != from_address:
            raise Exception("Transfer not authorized by token owner")
        self.token_owners[token_id] = to_address

    def approve(self, approved, token_id):
        owner = self.token_owners.get(token_id)
        if owner is None:
            raise Exception("Token does not exist")
        self.approvals[token_id] = approved

    def get_approved(self, token_id):
        return self.approvals.get(token_id, None)

    def set_approval_for_all(self, operator, approved):
        self.operators[operator] = approved

    def is_approved_for_all(self, owner, operator):
        return self.operators.get(operator, False)

    def burn(self, token_id):
        if token_id not in self.tokens:
            raise Exception("Token ID does not exist")
        del self.tokens[token_id]
        del self.token_owners[token_id]
        if token_id in self.approvals:
            del self.approvals[token_id]

    def owner_of(self, token_id):
        return self.token_owners.get(token_id, None)

    def balance_of(self, owner):
        return sum(1 for token_owner in self.token_owners.values() if token_owner == owner)

    def token_metadata(self, token_id):
        return self.tokens.get(token_id, None)

    def transfer_from(self, from_address, to_address, token_id):
        if self.get_approved(token_id) != from_address and not self.is_approved_for_all(self.owner_of(token_id), from_address):
            raise Exception("Transfer not approved")
        self.transfer(from_address, to_address, token_id)

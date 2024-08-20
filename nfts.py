# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module handles the creation and management of non-fungible tokens (NFTs).

class NonFungibleToken:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.tokens = {}
        self.owners = {}

    def mint(self, token_id, owner):
        """Mint a new non-fungible token with a specified ID to a specified owner."""
        if token_id in self.tokens:
            return False  # Token already exists
        self.tokens[token_id] = owner
        self.owners[owner] = self.owners.get(owner, []) + [token_id]
        return True

    def transfer(self, sender, recipient, token_id):
        """Transfer a non-fungible token from one account to another."""
        if token_id not in self.tokens or self.tokens[token_id] != sender:
            return False  # Token does not belong to sender
        self.tokens[token_id] = recipient
        self.owners[sender].remove(token_id)
        if recipient in self.owners:
            self.owners[recipient].append(token_id)
        else:
            self.owners[recipient] = [token_id]
        return True

    def owner_of(self, token_id):
        """Return the owner of a specified token."""
        return self.tokens.get(token_id, None)

    def tokens_of_owner(self, owner):
        """Return a list of token IDs owned by a specified account."""
        return self.owners.get(owner, [])

# Example usage
if __name__ == "__main__":
    nft = NonFungibleToken("ExampleNFT", "ENFT")
    nft.mint(1, "alice")
    nft.mint(2, "alice")
    nft.transfer("alice", "bob", 1)
    print(f"Owner of token 1: {nft.owner_of(1)}")
    print(f"Alice's tokens: {nft.tokens_of_owner('alice')}")
    print(f"Bob's tokens: {nft.tokens_of_owner('bob')}")

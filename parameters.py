BLOCK_REWARD = 50
BLOCK_TIME = 15  # in seconds
MAX_TRANSACTIONS = 15000

def update_balance(wallet_address, amount, blockchain):
    """Update the balance of the wallet in the blockchain."""
    if wallet_address in blockchain['balances']:
        blockchain['balances'][wallet_address] += amount
    else:
        blockchain['balances'][wallet_address] = amount
    return blockchain['balances'][wallet_address]

def get_balance(wallet_address, blockchain):
    """Return the balance of the wallet."""
    return blockchain['balances'].get(wallet_address, 0)

-- Schema for Blocks
CREATE TABLE IF NOT EXISTS blocks (
    block_hash TEXT PRIMARY KEY,
    block_number INTEGER NOT NULL,
    parent_hash TEXT,
    state_root TEXT,
    tx_root TEXT,
    difficulty INTEGER,
    nonce INTEGER,
    timestamp REAL,
    miner TEXT,
    block_size INTEGER,
    transaction_count INTEGER
);

-- Schema for Transactions
CREATE TABLE IF NOT EXISTS transactions (
    tx_hash TEXT PRIMARY KEY,
    block_hash TEXT,
    block_number INTEGER,
    sender TEXT,
    recipient TEXT,
    value INTEGER,
    size INTEGER,
    fee INTEGER,
    nonce INTEGER,
    input TEXT,
    transaction_index INTEGER,
    timestamp REAL,
    text TEXT,
    token TEXT,
    nft TEXT,
    FOREIGN KEY(block_hash) REFERENCES blocks(block_hash)
);

-- Schema for Accounts
CREATE TABLE IF NOT EXISTS accounts (
    address TEXT PRIMARY KEY,
    balance INTEGER,
    nonce INTEGER,
    code_hash TEXT,
    storage_root TEXT
);

-- Schema for State
CREATE TABLE IF NOT EXISTS state (
    state_root TEXT PRIMARY KEY,
    account_address TEXT,
    storage_root TEXT,
    FOREIGN KEY (account_address) REFERENCES accounts(address)
);

-- Schema for Contracts
CREATE TABLE IF NOT EXISTS contracts (
    contract_address TEXT PRIMARY KEY,
    owner_address TEXT,
    code TEXT,
    creation_block INTEGER,
    creation_tx_hash TEXT,
    contract_name TEXT,
    contract_version TEXT,
    contract_metadata TEXT,
    FOREIGN KEY (owner_address) REFERENCES accounts(address)
);

-- Schema for Fungible Tokens
CREATE TABLE IF NOT EXISTS fts (
    token_id TEXT PRIMARY KEY,
    name TEXT,
    symbol TEXT,
    total_supply INTEGER,
    max_supply INTEGER,
    decimals INTEGER,
    owner_address TEXT,
    FOREIGN KEY (owner_address) REFERENCES accounts(address)
);

CREATE TABLE IF NOT EXISTS ft_balances (
    token_id TEXT,
    owner_address TEXT,
    balance INTEGER,
    PRIMARY KEY (token_id, owner_address),
    FOREIGN KEY (token_id) REFERENCES fts(token_id),
    FOREIGN KEY (owner_address) REFERENCES accounts(address)
);

CREATE TABLE IF NOT EXISTS ft_allowances (
    token_id TEXT,
    owner_address TEXT,
    spender_address TEXT,
    allowance INTEGER,
    PRIMARY KEY (token_id, owner_address, spender_address),
    FOREIGN KEY (token_id) REFERENCES fts(token_id),
    FOREIGN KEY (owner_address) REFERENCES accounts(address),
    FOREIGN KEY (spender_address) REFERENCES accounts(address)
);

-- Schema for Non-Fungible Tokens
CREATE TABLE IF NOT EXISTS nfts (
    nft_id TEXT PRIMARY KEY,
    name TEXT,
    symbol TEXT,
    owner_address TEXT,
    metadata TEXT,
    FOREIGN KEY (owner_address) REFERENCES accounts(address)
);

CREATE TABLE IF NOT EXISTS nft_ownerships (
    nft_id TEXT,
    owner_address TEXT,
    PRIMARY KEY (nft_id, owner_address),
    FOREIGN KEY (nft_id) REFERENCES nfts(nft_id),
    FOREIGN KEY (owner_address) REFERENCES accounts(address)
);

CREATE TABLE IF NOT EXISTS nft_approvals (
    nft_id TEXT,
    approved_address TEXT,
    PRIMARY KEY (nft_id, approved_address),
    FOREIGN KEY (nft_id) REFERENCES nfts(nft_id),
    FOREIGN KEY (approved_address) REFERENCES accounts(address)
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_blocks_number ON blocks(block_number);
CREATE INDEX IF NOT EXISTS idx_transactions_block_hash ON transactions(block_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_sender ON transactions(sender);
CREATE INDEX IF NOT EXISTS idx_transactions_recipient ON transactions(recipient);
CREATE INDEX IF NOT EXISTS idx_contracts_owner ON contracts(owner_address);
CREATE INDEX IF NOT EXISTS idx_fts_owner ON fts(owner_address);
CREATE INDEX IF NOT EXISTS idx_nfts_owner ON nfts(owner_address);

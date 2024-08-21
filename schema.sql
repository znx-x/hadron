-- Schema for Blocks
CREATE TABLE IF NOT EXISTS blocks (
    block_hash TEXT PRIMARY KEY,
    block_number INTEGER,
    parent_hash TEXT,
    state_root TEXT,
    tx_root TEXT,
    receipt_root TEXT,
    logs_bloom TEXT,
    difficulty INTEGER,
    nonce TEXT,
    mix_hash TEXT,
    timestamp INTEGER,
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
    size INTEGER,  -- Size in kilobytes, acts as gas in Ethereum
    fee INTEGER,  -- Fee based on size, acts as gas price in Ethereum
    nonce INTEGER,
    input TEXT,
    transaction_index INTEGER,
    timestamp INTEGER,
    text TEXT,
    token TEXT,
    nft TEXT,
    FOREIGN KEY (block_hash) REFERENCES blocks(block_hash)
);

-- Schema for Accounts
CREATE TABLE IF NOT EXISTS accounts (
    address TEXT PRIMARY KEY,
    balance INTEGER,
    nonce INTEGER,
    code_hash TEXT,  -- For smart contracts
    storage_root TEXT  -- For smart contract storage
);

-- Schema for State
CREATE TABLE IF NOT EXISTS state (
    state_root TEXT PRIMARY KEY,
    account_address TEXT,
    storage_root TEXT,
    FOREIGN KEY (account_address) REFERENCES accounts(address)
);

-- Schema for Receipts
CREATE TABLE IF NOT EXISTS receipts (
    tx_hash TEXT PRIMARY KEY,
    block_hash TEXT,
    block_number INTEGER,
    cumulative_size INTEGER,  -- Acts as cumulative gas used
    logs_bloom TEXT,
    status INTEGER,  -- Success or failure
    logs TEXT,  -- Event logs
    FOREIGN KEY (tx_hash) REFERENCES transactions(tx_hash)
);

-- Schema for Logs
CREATE TABLE IF NOT EXISTS logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash TEXT,
    block_hash TEXT,
    block_number INTEGER,
    log_index INTEGER,
    address TEXT,
    data TEXT,
    topics TEXT,
    FOREIGN KEY (tx_hash) REFERENCES transactions(tx_hash)
);

-- Schema for WASM Smart Contracts
CREATE TABLE IF NOT EXISTS contracts (
    contract_address TEXT PRIMARY KEY,
    owner_address TEXT,
    code TEXT,  -- WASM code
    creation_block INTEGER,
    creation_tx_hash TEXT,
    contract_name TEXT,
    contract_version TEXT,
    contract_metadata TEXT,  -- JSON metadata about the contract
    FOREIGN KEY (owner_address) REFERENCES accounts(address)
);

-- Schema for Fungible Tokens (FTs)
CREATE TABLE IF NOT EXISTS fts (
    token_id TEXT PRIMARY KEY,
    name TEXT,
    symbol TEXT,
    total_supply INTEGER,
    max_supply INTEGER,  -- Optional, for capped tokens
    decimals INTEGER,
    owner_address TEXT,  -- Address of the token creator
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

-- Schema for Non-Fungible Tokens (NFTs)
CREATE TABLE IF NOT EXISTS nfts (
    nft_id TEXT PRIMARY KEY,
    name TEXT,
    symbol TEXT,
    owner_address TEXT,  -- Address of the NFT creator
    metadata TEXT,  -- JSON metadata (e.g., URI, traits)
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

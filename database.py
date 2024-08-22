# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Manages blockchain data storage using SQLite.

import sqlite3
import os
from parameters import parameters

class BlockchainDatabase:
    def __init__(self):
        """Initialize the SQLite connection using the specified database file."""
        db_path = os.path.join(parameters["data_directory"], 'blockchain.db')

        if not os.path.exists(parameters["data_directory"]):
            os.makedirs(parameters["data_directory"])

        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database schema if it doesn't exist."""
        schema = """
        CREATE TABLE IF NOT EXISTS blocks (
            block_hash TEXT PRIMARY KEY,
            block_number INTEGER,
            parent_hash TEXT,
            state_root TEXT,
            tx_root TEXT,
            difficulty INTEGER,
            nonce TEXT,
            timestamp INTEGER,
            miner TEXT,
            block_size INTEGER,
            transaction_count INTEGER
        );
        CREATE TABLE IF NOT EXISTS transactions (
            tx_hash TEXT PRIMARY KEY,
            block_hash TEXT,
            sender TEXT,
            recipient TEXT,
            value INTEGER,
            fee INTEGER,
            nonce INTEGER,
            input TEXT,
            timestamp INTEGER
        );
        """
        self.cursor.executescript(schema)
        self.connection.commit()
        print("[Blockchain] Initialized and ready.")

    def save_block(self, block_hash, block_data):
        """Saves a block to the SQLite database using the block hash as the key."""
        try:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO blocks (
                    block_hash, block_number, parent_hash, state_root, tx_root, difficulty, 
                    nonce, timestamp, miner, block_size, transaction_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    block_hash,
                    block_data["block_number"],
                    block_data["parent_hash"],
                    block_data["state_root"],
                    block_data["tx_root"],
                    block_data["difficulty"],
                    block_data["nonce"],
                    block_data["timestamp"],
                    block_data["miner"],
                    block_data["block_size"],
                    block_data["transaction_count"],
                )
            )
            self.connection.commit()
            print(f"[Blockchain] Added Block to DB: {block_hash}")
        except sqlite3.Error as e:
            print(f"[Blockchain] Error saving block {block_hash}: {e}")

    def get_block(self, block_hash):
        """Retrieves a block from the database using the block hash as the key."""
        try:
            self.cursor.execute("SELECT * FROM blocks WHERE block_hash=?", (block_hash,))
            block = self.cursor.fetchone()
            if block:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, block))
            return None
        except sqlite3.Error as e:
            print(f"[Blockchain] Unexpected error retrieving block {block_hash}: {e}")
            return None

    def get_last_block(self):
        """Retrieves the last block in the blockchain."""
        try:
            self.cursor.execute("SELECT * FROM blocks ORDER BY block_number DESC LIMIT 1")
            block = self.cursor.fetchone()
            if block:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, block))
            return None
        except sqlite3.Error as e:
            print(f"[Blockchain] Error retrieving the last block: {e}")
            return None
    
    def save_transaction(self, transaction):
        """Saves a transaction to the SQLite database."""
        try:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO transactions (
                    tx_hash, block_hash, sender, recipient, value, fee, nonce, input, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction['tx_hash'],
                    transaction['block_hash'],
                    transaction['sender'],
                    transaction['recipient'],
                    transaction['value'],
                    transaction['fee'],
                    transaction['nonce'],
                    transaction['input'],
                    transaction['timestamp'],
                )
            )
            self.connection.commit()  # Ensure that the transaction is committed to the database
            print(f"[Blockchain] Added Transaction to DB: {transaction['tx_hash']}")
        except sqlite3.Error as e:
            print(f"[Blockchain] Error saving transaction {transaction['tx_hash']}: {e}")

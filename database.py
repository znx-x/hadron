# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module handles interactions with SQLite to store and retrieve
# blockchain data.

import sqlite3
import os
from parameters import parameters

class BlockchainDatabase:
    def __init__(self):
        """Initialize the SQLite connection using the specified database file."""
        db_path = os.path.join(parameters["data_directory"], 'blockchain.db')

        if not os.path.exists(parameters["data_directory"]):
            os.makedirs(parameters["data_directory"])

        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self._initialize_database()

    def _initialize_database(self):
        """Load the schema from the SQL file and execute it."""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as schema_file:
            schema = schema_file.read()
        self.cursor.executescript(schema)
        self.connection.commit()
        print("[Database] Initialized and ready.")

    def save_block(self, block_hash, block_data):
        """Saves a block to the SQLite database using the block hash as the key."""
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO blocks (block_hash, block_number, parent_hash, state_root, tx_root, receipt_root, logs_bloom, difficulty, nonce, mix_hash, timestamp, miner, block_size, transaction_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (block_hash, block_data["block_number"], block_data["parent_hash"], block_data["state_root"], block_data["tx_root"], block_data["receipt_root"], block_data["logs_bloom"], block_data["difficulty"], block_data["nonce"], block_data["mix_hash"], block_data["timestamp"], block_data["miner"], block_data["block_size"], block_data["transaction_count"])
            )
            self.connection.commit()
            print(f"[Database] Block {block_hash} saved.")
        except sqlite3.Error as e:
            print(f"[Database] Error saving block {block_hash}: {e}")

    def get_block(self, block_hash):
        """Retrieves a block from the database using the block hash as the key."""
        try:
            self.cursor.execute("SELECT * FROM blocks WHERE block_hash=?", (block_hash,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"[Database] Unexpected error retrieving block {block_hash}: {e}")
            return None

    def get_last_block(self):
        """Retrieves the last block in the blockchain."""
        try:
            self.cursor.execute("SELECT * FROM blocks ORDER BY block_number DESC LIMIT 1")
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"[Database] Error retrieving the last block: {e}")
            return None

    def block_exists(self, block_hash):
        """Checks if a block exists in the database."""
        try:
            self.cursor.execute("SELECT 1 FROM blocks WHERE block_hash=?", (block_hash,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"[Database] Error checking existence of block {block_hash}: {e}")
            return False

    def validate_block(self, block_data):
        """Validates the block data before saving it to the database."""
        required_fields = ["block_number", "timestamp", "miner"]
        return all(field in block_data for field in required_fields)

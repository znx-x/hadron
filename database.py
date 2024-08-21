# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module handles interactions with LevelDB to store and retrieve
# blockchain data.

import leveldb
import json
from parameters import parameters
from cryptography import Qhash3512

class BlockchainDatabase:
    def __init__(self):
        """Initialize the LevelDB connection using the specified data directory."""
        self.db = leveldb.LevelDB(parameters["data_directory"])

    def save_block(self, index, block_data):
        """Saves a block to the LevelDB database using the block index as the key."""
        if self.validate_block(block_data):  # Ensure block data is valid before saving
            try:
                self.db.Put(str(index).encode('utf-8'), json.dumps(block_data).encode('utf-8'))
            except Exception as e:
                print(f"Error saving block {index}: {e}")
        else:
            print(f"Invalid block data for index {index}. Block not saved.")

    def get_block(self, index):
        """Retrieves a block from the database using the block index as the key."""
        try:
            block_data = self.db.Get(str(index).encode('utf-8'))
            return json.loads(block_data.decode('utf-8'))
        except KeyError:
            return None
        except json.JSONDecodeError:
            print(f"Data corruption detected for block {index}.")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving block {index}: {e}")
            return None

    def get_last_block(self):
        """Retrieves the last block in the blockchain."""
        try:
            last_key = None
            for key, _ in self.db.RangeIter(reverse=True):
                last_key = key.decode('utf-8')
                break  # We only need the first (last) key
            if last_key:
                return self.get_block(last_key)
        except Exception as e:
            print(f"Error retrieving the last block: {e}")
        return None

    def block_exists(self, index):
        """Checks if a block exists in the database."""
        try:
            self.db.Get(str(index).encode('utf-8'))
            return True
        except KeyError:
            return False
        except Exception as e:
            print(f"Error checking existence of block {index}: {e}")
            return False

    def validate_block(self, block_data):
        """Validates the block data before saving it to the database."""
        # Basic validation
        if not isinstance(block_data, dict) or "index" not in block_data or "timestamp" not in block_data:
            return False

        # Check for necessary fields
        required_fields = ["index", "timestamp", "transactions", "proof", "previous_hash", "hash"]
        for field in required_fields:
            if field not in block_data:
                return False

        # Check that the block's hash is correct
        calculated_hash = Qhash3512.hash_block(block_data)
        if calculated_hash != block_data["hash"]:
            return False

        # Ensure the block's previous hash matches the last block's hash in the chain
        if block_data["index"] > 1:
            previous_block = self.get_block(block_data["index"] - 1)
            if previous_block is None or block_data["previous_hash"] != previous_block["hash"]:
                return False

        return True

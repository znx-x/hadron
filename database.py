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
        # Implement block validation logic (e.g., structure, necessary fields)
        if isinstance(block_data, dict) and "index" in block_data and "timestamp" in block_data:
            return True
        return False

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module handles interactions with LevelDB to store and retrieve
# blockchain data.

import leveldb
import json
from parameters import BLOCKCHAIN_DIR

class BlockchainDatabase:
    def __init__(self):
        self.db = leveldb.LevelDB(BLOCKCHAIN_DIR)

    def save_block(self, index, block_data):
        self.db.Put(str(index).encode('utf-8'), json.dumps(block_data).encode('utf-8'))

    def get_block(self, index):
        try:
            block_data = self.db.Get(str(index).encode('utf-8'))
            return json.loads(block_data.decode('utf-8'))
        except KeyError:
            return None

    def get_last_block(self):
        last_index = None
        for key, value in self.db.RangeIter():
            last_index = key.decode('utf-8')
        if last_index:
            return self.get_block(last_index)
        return None

# Example usage
if __name__ == "__main__":
    db = BlockchainDatabase()
    block = {
        'index': 1,
        'timestamp': 1234567890,
        'transactions': [],
        'proof': 100,
        'previous_hash': '1'
    }
    db.save_block(1, block)
    retrieved_block = db.get_block(1)
    print(retrieved_block)

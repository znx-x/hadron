# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module implements the MineH algorithm, a custom Proof-of-Work
# algorithm that is memory-hard and CPU-friendly.

import hashlib
import os
import random
import time

class MineH:
    def __init__(self, memory_size=2**20):
        """Initializes the MineH algorithm with a specific memory size."""
        self.memory_size = memory_size
        self.memory = bytearray(os.urandom(memory_size))
        self.last_memory_update = time.time()

    def mine(self, block_data: str, difficulty: int) -> int:
        """Mines a new block by finding a nonce that meets the difficulty requirement."""
        nonce = 0
        while True:
            # Update memory periodically to maintain memory-hard properties
            if time.time() - self.last_memory_update > 60:  # Update every minute
                self.update_memory()

            # Combine block data, nonce, and a portion of the memory
            combined_data = f"{block_data}{nonce}".encode('utf-8') + self.memory[nonce % self.memory_size:]
            hash_result = hashlib.sha512(combined_data).hexdigest()

            if self.is_valid_hash(hash_result, difficulty):
                return nonce, hash_result  # Return both nonce and valid hash
            nonce += 1

    @staticmethod
    def is_valid_hash(hash_result: str, difficulty: int) -> bool:
        """Checks if the hash meets the difficulty criteria."""
        target = '0' * difficulty
        return hash_result.startswith(target)

    def update_memory(self):
        """Periodically updates the memory to ensure the algorithm remains memory-hard."""
        for i in range(self.memory_size):
            self.memory[i] = random.randint(0, 255)
        self.last_memory_update = time.time()


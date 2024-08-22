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

# pow.py

import os
import random
import time
from cryptography import Qhash3512

class MineH:
    def __init__(self, memory_size=2**20):
        """Initializes the MineH algorithm with a specific memory size."""
        self.memory_size = memory_size
        self.memory = bytearray(os.urandom(memory_size))
        self.last_memory_update = time.time()

    def mine(self, block_data: str, difficulty: int) -> int:
        nonce = 0
        while True:
            # Update memory periodically to maintain memory-hard properties
            if time.time() - self.last_memory_update > 60:  # Update every minute
                self.update_memory()

            combined_data = f"{block_data}{nonce}" + self.memory[nonce % self.memory_size:].decode('latin1')
            hash_result = Qhash3512.generate_hash(combined_data)

            if Qhash3512.is_valid_hash(hash_result, difficulty):
                # Log the hash result and combined data for debugging
                print(f"DEBUG: Mined hash: {hash_result}, Nonce: {nonce}, Combined Data: {combined_data}")
                return nonce, hash_result  # Return both nonce and valid hash

            nonce += 1

    def update_memory(self):
        """Periodically updates the memory to ensure the algorithm remains memory-hard."""
        for i in range(self.memory_size):
            self.memory[i] = random.randint(0, 255)
        self.last_memory_update = time.time()

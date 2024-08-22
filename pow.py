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

import os
import time
from cryptography import Qhash3512

class MineH:
    def __init__(self, memory_size, memory_update_interval=10):
        """
        Initializes the MineH algorithm with a specified memory size and update interval.
        :param memory_size: Size of the memory array used in the algorithm.
        :param memory_update_interval: Time interval (in seconds) to update the memory.
        """
        self.memory_size = memory_size
        self.memory = bytearray(os.urandom(memory_size))
        self.memory_update_interval = memory_update_interval
        self.memory_segment_size = 64  # Keep segment size manageable
        self.last_memory_update = time.time()

    def mine(self, block_data: str, difficulty: int):
        """
        Executes the mining process by iterating through nonces until a valid hash is found.
        :param block_data: The serialized block data to be hashed.
        :param difficulty: The required difficulty level (number of leading zeros in the hash).
        :return: A tuple containing the valid nonce and the corresponding valid hash.
        """
        nonce = 0

        while True:
            self._maybe_update_memory()

            # Optimization: Avoid unnecessary string concatenation in the loop
            combined_data = f"{block_data}{nonce}"
            memory_segment = self._get_memory_segment(nonce)
            hash_result = Qhash3512.generate_hash(combined_data + memory_segment)

            # Ensure difficulty is treated as an integer
            if Qhash3512.is_valid_hash(hash_result, difficulty):
                return nonce, hash_result

            nonce += 1

    def _maybe_update_memory(self):
        """Updates the memory array if the specified update interval has passed."""
        if time.time() - self.last_memory_update > self.memory_update_interval:
            self._update_memory()

    def _update_memory(self):
        """Refreshes the memory array with new random data."""
        self.memory = bytearray(os.urandom(self.memory_size))
        self.last_memory_update = time.time()

    def _get_memory_segment(self, nonce):
        """
        Retrieves a segment of the memory array based on the current nonce.
        :param nonce: The current nonce used in the mining process.
        :return: A segment of the memory array as a string.
        """
        start_index = nonce % (self.memory_size - self.memory_segment_size)
        return self.memory[start_index:start_index + self.memory_segment_size].decode('latin1')

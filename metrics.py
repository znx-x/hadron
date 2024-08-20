# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module collects and logs network metrics.

import time

class Metrics:
    def __init__(self):
        self.start_time = time.time()
        self.block_times = []
        self.hash_rates = []

    def add_block_time(self, block_time):
        self.block_times.append(block_time)

    def add_hash_rate(self, hash_rate):
        self.hash_rates.append(hash_rate)

    def get_average_block_time(self):
        return sum(self.block_times) / len(self.block_times) if self.block_times else 0

    def get_average_hash_rate(self):
        return sum(self.hash_rates) / len(self.hash_rates) if self.hash_rates else 0

# Example usage
if __name__ == "__main__":
    metrics = Metrics()
    metrics.add_block_time(15.5)
    metrics.add_block_time(14.7)
    print(f"Average Block Time: {metrics.get_average_block_time()} seconds")

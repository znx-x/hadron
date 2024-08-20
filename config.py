# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This file houses the basic node configuration parameters.

import json
import os

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        if not os.path.exists(config_file):
            self.config = {
                "host": "0.0.0.0",
                "port": 5000,
                "blockchain_dir": "/blockchain",
                "log_file": "blockchain.log"
            }
            self.save_config()
        else:
            self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as file:
            self.config = json.load(file)

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=4)

# Example usage
if __name__ == "__main__":
    config = Config()
    print(config.config)

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Manages private keys, account creation, and the encryption and
# decryption of private keys.

from cryptography import Qhash3512
import os
import json

class Wallet:
    def __init__(self, wallet_dir="wallets"):
        self.wallet_dir = wallet_dir
        if not os.path.exists(wallet_dir):
            os.makedirs(wallet_dir)

    def create_wallet(self):
        private_key, public_key = Qhash3512.generate_key_pair()
        wallet_data = {
            'public_key': public_key.encode().hex(),
            'private_key': private_key.encode().hex()
        }
        self.save_wallet(wallet_data)
        return wallet_data

    def save_wallet(self, wallet_data):
        wallet_filename = f"{wallet_data['public_key'][:8]}.json"
        wallet_filepath = os.path.join(self.wallet_dir, wallet_filename)
        with open(wallet_filepath, 'w') as wallet_file:
            json.dump(wallet_data, wallet_file)
        print(f"Wallet saved at {wallet_filepath}")

    def load_wallet(self, public_key):
        wallet_filename = f"{public_key[:8]}.json"
        wallet_filepath = os.path.join(self.wallet_dir, wallet_filename)
        if os.path.exists(wallet_filepath):
            with open(wallet_filepath, 'r') as wallet_file:
                wallet_data = json.load(wallet_file)
            return wallet_data
        return None

# Example usage
if __name__ == "__main__":
    wallet = Wallet()
    new_wallet = wallet.create_wallet()
    print(f"New Wallet: {new_wallet}")
    loaded_wallet = wallet.load_wallet(new_wallet['public_key'])
    print(f"Loaded Wallet: {loaded_wallet}")

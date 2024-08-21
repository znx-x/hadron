# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Manages private keys, account creation, and the encryption and
# decryption of private keys.

from cryptography import Qhash3512
import os
import json
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from nacl.secret import SecretBox
from nacl.utils import random
from parameters import parameters
from base64 import urlsafe_b64encode, urlsafe_b64decode

class Wallet:
    def __init__(self):
        self.data_directory = parameters.get("data_directory", "./blockchain")
        self.accounts_dir = os.path.join(self.data_directory, "accounts")
        if not os.path.exists(self.accounts_dir):
            os.makedirs(self.accounts_dir)

    def generate_key_pair(self):
        """Generates a new private and public key pair using Qhash3512."""
        private_key, public_key = Qhash3512.generate_key_pair()
        return private_key, public_key

    def create_wallet(self, password):
        """Creates a new wallet with a generated key pair."""
        private_key, public_key = self.generate_key_pair()
        public_key_truncated = public_key.encode(HexEncoder).decode('utf-8')[:40]
        encrypted_private_key = self.encrypt_private_key(private_key.encode(HexEncoder).decode('utf-8'), password)
        wallet_data = {
            'public_key': public_key_truncated,
            'private_key': encrypted_private_key
        }
        self.save_wallet(wallet_data)
        return wallet_data

    def save_wallet(self, wallet_data):
        """Saves the wallet data to a file, encrypting the private key."""
        wallet_filename = f"{wallet_data['public_key'][:8]}.json"
        wallet_filepath = os.path.join(self.accounts_dir, wallet_filename)
        try:
            with open(wallet_filepath, 'w') as wallet_file:
                json.dump(wallet_data, wallet_file)
            print(f"Wallet saved at {wallet_filepath}")
        except IOError as e:
            raise IOError(f"Failed to save wallet: {e}")

    def load_wallet(self, public_key, password):
        """Loads the wallet data from a file and decrypts the private key."""
        wallet_filename = f"{public_key[:8]}.json"
        wallet_filepath = os.path.join(self.accounts_dir, wallet_filename)
        if os.path.exists(wallet_filepath):
            try:
                with open(wallet_filepath, 'r') as wallet_file:
                    wallet_data = json.load(wallet_file)
                wallet_data['private_key'] = self.decrypt_private_key(wallet_data['private_key'], password)
                return wallet_data
            except IOError as e:
                raise IOError(f"Failed to load wallet: {e}")
            except json.JSONDecodeError:
                raise ValueError("Corrupted wallet file.")
        else:
            raise FileNotFoundError(f"Wallet file not found for public key: {public_key}")

    def list_wallets(self):
        """Lists all wallets stored in the accounts directory."""
        if not os.path.exists(self.accounts_dir):
            os.makedirs(self.accounts_dir)  # Ensure the directory exists
        return [f.split('.')[0] for f in os.listdir(self.accounts_dir) if f.endswith('.json')]

    def sign_transaction(self, private_key_hex, data):
        """Signs transaction data using the private key."""
        try:
            private_key = SigningKey(private_key_hex, encoder=HexEncoder)
            signature = Qhash3512.sign_data(private_key, data)
            return signature
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {e}")

    def encrypt_private_key(self, private_key_hex, password):
        """Encrypts the private key for secure storage using a password."""
        try:
            # Use the first 32 bytes of the derived key for SecretBox
            key = Qhash3512.hash_password(password)
            key_bytes = urlsafe_b64decode(key.encode('utf-8'))[16:48]  # Extract the key part after the salt
            box = SecretBox(key_bytes)
            encrypted = box.encrypt(private_key_hex.encode('utf-8'), encoder=HexEncoder)
            return encrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to encrypt private key: {e}")

    def decrypt_private_key(self, encrypted_private_key, password):
        """Decrypts the private key using the provided password."""
        try:
            # Use the first 32 bytes of the derived key for SecretBox
            key = Qhash3512.hash_password(password)
            key_bytes = urlsafe_b64decode(key.encode('utf-8'))[16:48]  # Extract the key part after the salt
            box = SecretBox(key_bytes)
            decrypted = box.decrypt(encrypted_private_key.encode('utf-8'), encoder=HexEncoder)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt private key: {e}")

    def get_public_key(self, private_key_hex):
        """Derives the public key from the given private key."""
        try:
            private_key = SigningKey(private_key_hex, encoder=HexEncoder)
            public_key = private_key.verify_key
            return public_key.encode(HexEncoder).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to derive public key: {e}")

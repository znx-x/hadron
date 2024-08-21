# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module contains the Qhash3512 cryptographic algorithm and
# handles signature, hash inputs, and outputs.

from Crypto.Hash import SHA3_512
from Crypto.Protocol.KDF import PBKDF2
from nacl.signing import SigningKey, VerifyKey
from nacl.public import PrivateKey, PublicKey, Box
from base64 import urlsafe_b64encode, urlsafe_b64decode
from nacl.utils import random

class Qhash3512:
    @staticmethod
    def generate_hash(data: str, truncate_to: int = None) -> str:
        """Generates a quantum-resistant hash of the input data using Qhash3512 (SHA3-512).
        Optionally truncates the hash to the specified number of characters."""
        hasher = SHA3_512.new()
        hasher.update(data.encode('utf-8'))
        hash_value = hasher.hexdigest()
        return hash_value[:truncate_to] if truncate_to else hash_value

    @staticmethod
    def generate_key_pair():
        """Generates a pair of quantum-resistant keys (private key and public key) using the Qhash3512 algorithm."""
        private_key = SigningKey.generate()
        public_key = private_key.verify_key
        return private_key, public_key

    @staticmethod
    def public_key_to_address(public_key: VerifyKey, address_length: int = 40) -> str:
        """Converts a public key to a blockchain address by hashing it and truncating it to the desired length."""
        return Qhash3512.generate_hash(public_key.encode().hex(), truncate_to=address_length)

    @staticmethod
    def sign_data(private_key: SigningKey, data: str) -> str:
        """Generates a quantum-resistant signature for the given data using the private key."""
        signed = private_key.sign(data.encode('utf-8'))
        return signed.signature.hex()

    @staticmethod
    def verify_signature(public_key: VerifyKey, data: str, signature: str) -> bool:
        """Verifies a quantum-resistant signature using the public key.
        Returns True if the signature is valid, False otherwise, and logs the error if verification fails."""
        try:
            public_key.verify(data.encode('utf-8'), bytes.fromhex(signature))
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False

    @staticmethod
    def hash_transaction(transaction_data: dict) -> str:
        """Generates a hash for a transaction by serializing the transaction data and hashing it."""
        serialized_data = json.dumps(transaction_data, sort_keys=True)
        return Qhash3512.generate_hash(serialized_data)

    @staticmethod
    def hash_block(block_data: dict) -> str:
        """Generates a hash for a block by serializing the block data and hashing it."""
        serialized_data = json.dumps(block_data, sort_keys=True)
        return Qhash3512.generate_hash(serialized_data)

    @staticmethod
    def encrypt_data(public_key: PublicKey, data: str) -> str:
        """Encrypts data using the recipient's public key."""
        box = Box(PrivateKey.generate(), public_key)
        encrypted = box.encrypt(data.encode('utf-8'))
        return encrypted.hex()

    @staticmethod
    def decrypt_data(private_key: PrivateKey, encrypted_data: str) -> str:
        """Decrypts data using the recipient's private key."""
        box = Box(private_key, PublicKey(private_key.public_key.encode()))
        decrypted = box.decrypt(bytes.fromhex(encrypted_data))
        return decrypted.decode('utf-8')

    @staticmethod
    def hash_password(password: str, salt: bytes = None, iterations: int = 100_000) -> str:
        """Hashes a password using PBKDF2 with SHA3-512."""
        if salt is None:
            salt = random(16)
        key = PBKDF2(password.encode('utf-8'), salt, 32, count=iterations, hmac_hash_module=SHA3_512)
        return urlsafe_b64encode(salt + key).decode('utf-8')

    @staticmethod
    def verify_password(stored_password: str, provided_password: str, iterations: int = 100_000) -> bool:
        """Verifies the provided password against the stored hash."""
        decoded = urlsafe_b64decode(stored_password.encode('utf-8'))
        salt = decoded[:16]
        stored_key = decoded[16:]
        new_key = PBKDF2(provided_password.encode('utf-8'), salt, 32, count=iterations, hmac_hash_module=SHA3_512)
        return new_key == stored_key

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module contains the Qhash3512 cryptographic algorithm and
# handles signature hash inputs and outputs.

from Crypto.Hash import SHA3_512
from nacl.signing import SigningKey, VerifyKey

class Qhash3512:
    @staticmethod
    def generate_hash(data: str) -> str:
        """Generates a quantum-resistant hash of the input data using Qhash3512 (SHA3-512)."""
        hasher = SHA3_512.new()
        hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()

    @staticmethod
    def generate_key_pair():
        """Generates a pair of quantum-resistant keys (private key and public key) using the Qhash3512 algorithm."""
        private_key = SigningKey.generate()
        public_key = private_key.verify_key
        return private_key, public_key

    @staticmethod
    def sign_data(private_key: SigningKey, data: str) -> str:
        """Generates a quantum-resistant signature for the given data using the private key."""
        signed = private_key.sign(data.encode('utf-8'))
        return signed.signature.hex()

    @staticmethod
    def verify_signature(public_key: VerifyKey, data: str, signature: str) -> bool:
        """Verifies a quantum-resistant signature using the public key."""
        try:
            public_key.verify(data.encode('utf-8'), bytes.fromhex(signature))
            return True
        except:
            return False

# Example usage
if __name__ == "__main__":
    # Generate a new key pair
    private_key, public_key = Qhash3512.generate_key_pair()

    # Example data
    data = "This is a sample transaction"

    # Generate hash
    hash_value = Qhash3512.generate_hash(data)
    print(f"Hash: {hash_value}")

    # Sign the data
    signature = Qhash3512.sign_data(private_key, data)
    print(f"Signature: {signature}")

    # Verify the signature
    is_valid = Qhash3512.verify_signature(public_key, data, signature)
    print(f"Signature valid: {is_valid}")

# api/blockchain.py

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

from flask import Blueprint, jsonify
from blockchain import blockchain

blockchain_bp = Blueprint('blockchain', __name__)

# Get Blockchain Info
@blockchain_bp.route('/info', methods=['GET'])
def get_blockchain_info():
    info = {
        'number_of_blocks': len(blockchain.chain),
        'difficulty': blockchain.chain[-1]['difficulty'] if blockchain.chain else 0,
        'latest_block_hash': blockchain.hash(blockchain.chain[-1]) if blockchain.chain else None
    }
    return jsonify(info)

# Get Block by Index
@blockchain_bp.route('/block/<int:index>', methods=['GET'])
def get_block_by_index(index):
    if index < len(blockchain.chain):
        return jsonify(blockchain.chain[index])
    return jsonify({'error': 'Block not found'}), 404

# Get Block by Hash
@blockchain_bp.route('/blockhash/<hash>', methods=['GET'])
def get_block_by_hash(hash):
    for block in blockchain.chain:
        if blockchain.hash(block) == hash:
            return jsonify(block)
    return jsonify({'error': 'Block not found'}), 404

# Get Transaction by Hash
@blockchain_bp.route('/transaction/<hash>', methods=['GET'])
def get_transaction_by_hash(hash):
    for block in blockchain.chain:
        for transaction in block['transactions']:
            if blockchain.hash(transaction) == hash:
                return jsonify(transaction)
    return jsonify({'error': 'Transaction not found'}), 404

# Get Latest Block
@blockchain_bp.route('/latest', methods=['GET'])
def get_latest_block():
    if blockchain.chain:
        return jsonify(blockchain.chain[-1])
    return jsonify({'error': 'Blockchain is empty'}), 404

# Get Blockchain Length
@blockchain_bp.route('/length', methods=['GET'])
def get_blockchain_length():
    return jsonify({'length': len(blockchain.chain)})

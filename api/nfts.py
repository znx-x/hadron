# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

from flask import Blueprint, request, jsonify
from server import blockchain
from wallet import Wallet

nfts_bp = Blueprint('nfts', __name__)

# Create NFT
@nfts_bp.route('/create', methods=['POST'])
def create_nft():
    data = request.json
    name = data.get('name')
    metadata = data.get('metadata')
    owner = data.get('owner')

    if not name or not metadata or not owner:
        return jsonify({'error': 'Name, metadata, and owner address are required'}), 400

    token_id = blockchain.create_nft(name, metadata, owner)
    return jsonify({'token_id': token_id, 'status': 'NFT created successfully'})

# Transfer NFT
@nfts_bp.route('/transfer', methods=['POST'])
def transfer_nft():
    data = request.json
    token_id = data.get('token_id')
    sender = data.get('sender')
    recipient = data.get('recipient')

    if not token_id or not sender or not recipient:
        return jsonify({'error': 'Token ID, sender, and recipient are required'}), 400

    transfer_status = blockchain.transfer_nft(token_id, sender, recipient)
    if transfer_status:
        return jsonify({'status': 'Transfer successful'})
    return jsonify({'error': 'Transfer failed'}), 400

# Get NFT Metadata
@nfts_bp.route('/metadata/<token_id>', methods=['GET'])
def get_nft_metadata(token_id):
    metadata = blockchain.get_nft_metadata(token_id)
    if metadata:
        return jsonify({'metadata': metadata})
    return jsonify({'error': 'NFT not found'}), 404

# Check Ownership
@nfts_bp.route('/owner/<token_id>', methods=['GET'])
def check_ownership(token_id):
    owner = blockchain.get_nft_owner(token_id)
    if owner:
        return jsonify({'owner': owner})
    return jsonify({'error': 'NFT not found'}), 404

# Transfer NFT Ownership
@nfts_bp.route('/transfer_ownership', methods=['POST'])
def transfer_nft_ownership():
    data = request.json
    token_id = data.get('token_id')
    current_owner = data.get('current_owner')
    new_owner = data.get('new_owner')

    if not token_id or not current_owner or not new_owner:
        return jsonify({'error': 'Token ID, current owner, and new owner are required'}), 400

    transfer_status = blockchain.transfer_nft_ownership(token_id, current_owner, new_owner)
    if transfer_status:
        return jsonify({'status': 'Ownership transferred successfully'})
    return jsonify({'error': 'Ownership transfer failed'}), 400

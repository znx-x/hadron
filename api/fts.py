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

fts_bp = Blueprint('fts', __name__)

# Create Token
@fts_bp.route('/create', methods=['POST'])
def create_token():
    data = request.json
    name = data.get('name')
    symbol = data.get('symbol')
    total_supply = data.get('total_supply')
    owner = data.get('owner')

    if not name or not symbol or not total_supply or not owner:
        return jsonify({'error': 'Name, symbol, total supply, and owner address are required'}), 400

    token_address = blockchain.create_token(name, symbol, total_supply, owner)
    return jsonify({'token_address': token_address, 'status': 'Token created successfully'})

# Transfer Tokens
@fts_bp.route('/transfer', methods=['POST'])
def transfer_tokens():
    data = request.json
    token_address = data.get('token_address')
    sender = data.get('sender')
    recipient = data.get('recipient')
    amount = data.get('amount')

    if not token_address or not sender or not recipient or not amount:
        return jsonify({'error': 'Token address, sender, recipient, and amount are required'}), 400

    transfer_status = blockchain.transfer_tokens(token_address, sender, recipient, amount)
    if transfer_status:
        return jsonify({'status': 'Transfer successful'})
    return jsonify({'error': 'Transfer failed'}), 400

# Check Balance
@fts_bp.route('/balance/<token_address>/<account>', methods=['GET'])
def check_balance(token_address, account):
    balance = blockchain.get_token_balance(token_address, account)
    if balance is not None:
        return jsonify({'balance': balance})
    return jsonify({'error': 'Account or token not found'}), 404

# Get Token Info
@fts_bp.route('/info/<token_address>', methods=['GET'])
def get_token_info(token_address):
    token_info = blockchain.get_token_info(token_address)
    if token_info:
        return jsonify(token_info)
    return jsonify({'error': 'Token not found'}), 404

# Transfer Token Ownership
@fts_bp.route('/transfer_ownership', methods=['POST'])
def transfer_token_ownership():
    data = request.json
    token_address = data.get('token_address')
    current_owner = data.get('current_owner')
    new_owner = data.get('new_owner')

    if not token_address or not current_owner or not new_owner:
        return jsonify({'error': 'Token address, current owner, and new owner are required'}), 400

    transfer_status = blockchain.transfer_token_ownership(token_address, current_owner, new_owner)
    if transfer_status:
        return jsonify({'status': 'Ownership transferred successfully'})
    return jsonify({'error': 'Ownership transfer failed'}), 400

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

from flask import Blueprint, request, jsonify
from wallet import Wallet
from state import BlockchainState

accounts_bp = Blueprint('accounts', __name__)

# Initialize the Wallet and BlockchainState instances
wallet = Wallet()
blockchain_state = BlockchainState()

# Create Account
@accounts_bp.route('/create', methods=['POST'])
def create_account():
    new_wallet = wallet.create_wallet()
    return jsonify({
        'address': new_wallet['public_key'],
        'private_key': new_wallet['private_key']
    })

# Get Account Balance
@accounts_bp.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = blockchain_state.get_balance(address)
    return jsonify({
        'address': address,
        'balance': balance
    })

# List All Accounts
@accounts_bp.route('/list', methods=['GET'])
def list_accounts():
    accounts = wallet.list_wallets()
    accounts_with_balances = [
        {'address': acc['public_key'], 'balance': blockchain_state.get_balance(acc['public_key'])}
        for acc in accounts
    ]
    return jsonify(accounts_with_balances)

# Import Account
@accounts_bp.route('/import', methods=['POST'])
def import_account():
    data = request.get_json()
    private_key = data.get('private_key')
    if not private_key:
        return jsonify({'error': 'Private key is required'}), 400
    imported_wallet = wallet.import_wallet(private_key)
    return jsonify({
        'address': imported_wallet['public_key']
    })

# Export Account
@accounts_bp.route('/export/<address>', methods=['GET'])
def export_account(address):
    private_key = wallet.export_wallet(address)
    if not private_key:
        return jsonify({'error': 'Account not found'}), 404
    return jsonify({
        'address': address,
        'private_key': private_key
    })

# Get Account Ownership
@accounts_bp.route('/ownership/<address>', methods=['GET'])
def check_ownership(address):
    is_owned = wallet.check_ownership(address)
    return jsonify({
        'address': address,
        'is_owned': is_owned
    })

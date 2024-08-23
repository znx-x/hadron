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
from database import BlockchainDatabase  # Import the database

accounts_bp = Blueprint('accounts', __name__)

# Initialize the Wallet, Database, and BlockchainState instances
wallet = Wallet()
db = BlockchainDatabase()  # Create the database instance
blockchain_state = BlockchainState(db)  # Pass the database instance to BlockchainState

# Create Account
@accounts_bp.route('/create', methods=['POST'])
def create_account():
    data = request.get_json()
    password = data.get('password')
    if not password:
        return jsonify({'error': 'Password is required'}), 400

    try:
        new_wallet = wallet.create_wallet(password)
        return jsonify({
            'address': new_wallet['public_key'],
            'private_key': new_wallet['private_key']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    accounts_with_balances = []
    account_filenames = wallet.list_wallets()

    for filename in account_filenames:
        try:
            wallet_data = wallet.load_wallet(filename)
            public_key = wallet_data['public_key']
            balance = blockchain_state.get_balance(public_key)
            accounts_with_balances.append({
                'address': public_key,
                'balance': balance
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify(accounts_with_balances)

# Import Account
@accounts_bp.route('/import', methods=['POST'])
def import_account():
    data = request.get_json()
    private_key = data.get('private_key')
    if not private_key:
        return jsonify({'error': 'Private key is required'}), 400
    public_key = wallet.get_public_key(private_key)
    wallet_data = {
        'public_key': public_key,
        'private_key': private_key
    }
    wallet.save_wallet(wallet_data)
    return jsonify({
        'address': public_key
    })

# Export Account
@accounts_bp.route('/export/<address>', methods=['GET'])
def export_account(address):
    try:
        wallet_data = wallet.load_wallet(address)
        return jsonify({
            'address': wallet_data['public_key'],
            'private_key': wallet_data['private_key']
        })
    except FileNotFoundError:
        return jsonify({'error': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Account Ownership
@accounts_bp.route('/ownership/<address>', methods=['GET'])
def check_ownership(address):
    try:
        wallet_data = wallet.load_wallet(address)
        return jsonify({
            'address': address,
            'is_owned': True
        })
    except FileNotFoundError:
        return jsonify({
            'address': address,
            'is_owned': False
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

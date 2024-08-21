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
import json

contracts_bp = Blueprint('contracts', __name__)

# Deploy Contract
@contracts_bp.route('/deploy', methods=['POST'])
def deploy_contract():
    data = request.json
    bytecode = data.get('bytecode')
    constructor_params = data.get('constructor_params', {})
    sender = data.get('sender')

    if not bytecode or not sender:
        return jsonify({'error': 'Bytecode and sender address are required'}), 400

    contract_address = blockchain.deploy_contract(bytecode, constructor_params, sender)
    return jsonify({'contract_address': contract_address, 'status': 'Contract deployed successfully'})

# Call Contract Method
@contracts_bp.route('/call', methods=['POST'])
def call_contract_method():
    data = request.json
    contract_address = data.get('contract_address')
    method_name = data.get('method_name')
    method_params = data.get('method_params', {})
    sender = data.get('sender')

    if not contract_address or not method_name or not sender:
        return jsonify({'error': 'Contract address, method name, and sender address are required'}), 400

    result = blockchain.call_contract(contract_address, method_name, method_params, sender)
    return jsonify({'result': result, 'status': 'Method called successfully'})

# Get Contract Info
@contracts_bp.route('/info/<contract_address>', methods=['GET'])
def get_contract_info(contract_address):
    contract_info = blockchain.get_contract_info(contract_address)
    if contract_info:
        return jsonify(contract_info)
    return jsonify({'error': 'Contract not found'}), 404

# Transfer Contract Ownership
@contracts_bp.route('/transfer', methods=['POST'])
def transfer_contract_ownership():
    data = request.json
    contract_address = data.get('contract_address')
    current_owner = data.get('current_owner')
    new_owner = data.get('new_owner')

    if not contract_address or not current_owner or not new_owner:
        return jsonify({'error': 'Contract address, current owner, and new owner are required'}), 400

    transfer_status = blockchain.transfer_contract_ownership(contract_address, current_owner, new_owner)
    if transfer_status:
        return jsonify({'status': 'Ownership transferred successfully'})
    return jsonify({'error': 'Ownership transfer failed'}), 400

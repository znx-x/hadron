# api/transactions.py

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

from flask import Blueprint, request, jsonify

def create_transactions_blueprint(blockchain):
    transactions_bp = Blueprint('transactions', __name__)

    # Create Transaction
    @transactions_bp.route('/create', methods=['POST'])
    def create_transaction():
        data = request.json
        sender = data.get('sender')
        recipient = data.get('recipient')
        amount = data.get('amount')
        text = data.get('text')

        if not sender or not recipient or not amount:
            return jsonify({'error': 'Sender, recipient, and amount are required'}), 400

        tx_id = blockchain.new_transaction(sender, recipient, amount, text)
        return jsonify({'transaction_id': tx_id, 'status': 'Transaction created successfully'})

    # Get Transaction Status
    @transactions_bp.route('/status/<tx_id>', methods=['GET'])
    def get_transaction_status(tx_id):
        status = blockchain.get_transaction_status(tx_id)
        if status:
            return jsonify({'status': status})
        return jsonify({'error': 'Transaction not found'}), 404

    # Get Transaction Details
    @transactions_bp.route('/details/<tx_id>', methods=['GET'])
    def get_transaction_details(tx_id):
        transaction = blockchain.get_transaction_details(tx_id)
        if transaction:
            return jsonify({'transaction': transaction})
        return jsonify({'error': 'Transaction not found'}), 404

    # Get All Transactions
    @transactions_bp.route('/all', methods=['GET'])
    def get_all_transactions():
        transactions = blockchain.get_all_transactions()
        return jsonify({'transactions': transactions})

    return transactions_bp

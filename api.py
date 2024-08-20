# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module handles the JSON API requests for the node and RPC
# users (when HTTP or WS is enabled) to interact with the blockchain

from flask import Flask, jsonify, request
import json
from server import blockchain

app = Flask(__name__)

@app.route('/balance', methods=['GET'])
def get_balance():
    address = request.args.get('address')
    balance = blockchain.get_balance(address)
    return jsonify({'balance': balance}), 200

@app.route('/transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    result = blockchain.new_transaction(data['sender'], data['recipient'], data['amount'])
    return jsonify({'message': result}), 201

@app.route('/mine', methods=['GET'])
def mine():
    block = blockchain.mine_block()
    return jsonify({'block': block}), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    return jsonify(blockchain.chain), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

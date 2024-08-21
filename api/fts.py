# api/fts.py

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

from flask import Blueprint, request, jsonify

def create_fts_blueprint(blockchain):
    fts_bp = Blueprint('fts', __name__)

    # Create a new fungible token
    @fts_bp.route('/create', methods=['POST'])
    def create_token():
        data = request.get_json()
        name = data.get('name')
        symbol = data.get('symbol')
        initial_supply = data.get('initial_supply', 0)
        max_supply = data.get('max_supply')
        mintable = data.get('mintable', True)
        pausable = data.get('pausable', True)
        owner = data.get('owner')

        token = blockchain.create_token(name, symbol, initial_supply, max_supply, mintable, pausable, owner)
        return jsonify({"message": f"Token {name} ({symbol}) created successfully.", "total_supply": token.total_supply}), 201

    # Mint new tokens
    @fts_bp.route('/mint', methods=['POST'])
    def mint_tokens():
        data = request.get_json()
        symbol = data.get('symbol')
        to = data.get('to')
        amount = data.get('amount')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        try:
            token.mint(to, amount)
            return jsonify({"message": f"{amount} tokens minted to {to}.", "total_supply": token.total_supply})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Transfer tokens
    @fts_bp.route('/transfer', methods=['POST'])
    def transfer_tokens():
        data = request.get_json()
        symbol = data.get('symbol')
        from_address = data.get('from')
        to_address = data.get('to')
        amount = data.get('amount')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        try:
            token.transfer(from_address, to_address, amount)
            return jsonify({"message": f"{amount} tokens transferred from {from_address} to {to_address}."})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Burn tokens
    @fts_bp.route('/burn', methods=['POST'])
    def burn_tokens():
        data = request.get_json()
        symbol = data.get('symbol')
        from_address = data.get('from')
        amount = data.get('amount')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        try:
            token.burn(from_address, amount)
            return jsonify({"message": f"{amount} tokens burned from {from_address}.", "total_supply": token.total_supply})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Get balance of an address
    @fts_bp.route('/balance', methods=['GET'])
    def get_balance():
        symbol = request.args.get('symbol')
        address = request.args.get('address')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        balance = token.balance_of(address)
        return jsonify({"address": address, "balance": balance})

    # Approve a spender
    @fts_bp.route('/approve', methods=['POST'])
    def approve_spender():
        data = request.get_json()
        symbol = data.get('symbol')
        owner = data.get('owner')
        spender = data.get('spender')
        amount = data.get('amount')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        try:
            token.approve(owner, spender, amount)
            return jsonify({"message": f"Approved {spender} to spend {amount} tokens on behalf of {owner}."})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Get allowance
    @fts_bp.route('/allowance', methods=['GET'])
    def get_allowance():
        symbol = request.args.get('symbol')
        owner = request.args.get('owner')
        spender = request.args.get('spender')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        allowance = token.allowance(owner, spender)
        return jsonify({"owner": owner, "spender": spender, "allowance": allowance})

    # Transfer tokens from an approved spender
    @fts_bp.route('/transfer-from', methods=['POST'])
    def transfer_from():
        data = request.get_json()
        symbol = data.get('symbol')
        spender = data.get('spender')
        from_address = data.get('from')
        to_address = data.get('to')
        amount = data.get('amount')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        try:
            token.transfer_from(spender, from_address, to_address, amount)
            return jsonify({"message": f"{amount} tokens transferred from {from_address} to {to_address} by {spender}."})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Transfer ownership of the token
    @fts_bp.route('/transfer-ownership', methods=['POST'])
    def transfer_ownership():
        data = request.get_json()
        symbol = data.get('symbol')
        new_owner = data.get('new_owner')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        try:
            token.transfer_ownership(new_owner)
            return jsonify({"message": f"Ownership of token {symbol} transferred to {new_owner}."})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Pause the token
    @fts_bp.route('/pause', methods=['POST'])
    def pause_token():
        data = request.get_json()
        symbol = data.get('symbol')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        try:
            token.pause()
            return jsonify({"message": f"Token {symbol} paused."})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Unpause the token
    @fts_bp.route('/unpause', methods=['POST'])
    def unpause_token():
        data = request.get_json()
        symbol = data.get('symbol')

        token = blockchain.get_token(symbol)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        try:
            token.unpause()
            return jsonify({"message": f"Token {symbol} unpaused."})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return fts_bp

# api/nfts.py

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

from flask import Blueprint, request, jsonify

def create_nfts_blueprint(blockchain):
    nfts_bp = Blueprint('nfts', __name__)

    @nfts_bp.route('/mint', methods=['POST'])
    def mint_nft():
        data = request.json
        to = data['to']
        token_id = data['token_id']
        metadata = data.get('metadata', {})
        try:
            blockchain.mint_nft(to, token_id, metadata)
            return jsonify({"status": "success", "message": "NFT minted successfully"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @nfts_bp.route('/transfer', methods=['POST'])
    def transfer_nft():
        data = request.json
        from_address = data['from']
        to_address = data['to']
        token_id = data['token_id']
        try:
            blockchain.transfer_nft(from_address, to_address, token_id)
            return jsonify({"status": "success", "message": "NFT transferred successfully"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @nfts_bp.route('/approve', methods=['POST'])
    def approve_nft():
        data = request.json
        approved = data['approved']
        token_id = data['token_id']
        try:
            blockchain.approve_nft(approved, token_id)
            return jsonify({"status": "success", "message": "NFT approved successfully"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @nfts_bp.route('/burn', methods=['POST'])
    def burn_nft():
        data = request.json
        token_id = data['token_id']
        try:
            blockchain.burn_nft(token_id)
            return jsonify({"status": "success", "message": "NFT burned successfully"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @nfts_bp.route('/owner', methods=['GET'])
    def owner_of_nft():
        token_id = request.args.get('token_id')
        owner = blockchain.owner_of_nft(token_id)
        if owner:
            return jsonify({"status": "success", "owner": owner}), 200
        return jsonify({"status": "error", "message": "Token does not exist"}), 404

    @nfts_bp.route('/balance', methods=['GET'])
    def balance_of_nft():
        owner = request.args.get('owner')
        balance = blockchain.balance_of_nft(owner)
        return jsonify({"status": "success", "balance": balance}), 200

    @nfts_bp.route('/metadata', methods=['GET'])
    def nft_metadata():
        token_id = request.args.get('token_id')
        metadata = blockchain.get_nft_metadata(token_id)
        if metadata:
            return jsonify({"status": "success", "metadata": metadata}), 200
        return jsonify({"status": "error", "message": "Token does not exist"}), 404

    @nfts_bp.route('/transfer_from', methods=['POST'])
    def transfer_from_nft():
        data = request.json
        from_address = data['from']
        to_address = data['to']
        token_id = data['token_id']
        try:
            blockchain.transfer_nft_from(from_address, to_address, token_id)
            return jsonify({"status": "success", "message": "NFT transferred successfully"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    return nfts_bp

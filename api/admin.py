# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

import re
from flask import Blueprint, request, jsonify, current_app

def create_admin_blueprint():
    """
    Creates a Blueprint for admin-related functionality:
      - GET /admin/info
      - POST /admin/connectPeer
      - POST /admin/disconnectPeer
    """

    admin_bp = Blueprint('admin_bp', __name__)

    def parse_enode(enode_str):
        """
        Parses an enode-like address: enode://<node_id>@<ip>:<port>
        Returns (node_id, ip, port) if valid, otherwise (None, None, None).
        """
        pattern = r"enode://([^@]+)@([\d\.]+):(\d+)"
        match = re.match(pattern, enode_str)
        if match:
            node_id, ip, port = match.groups()
            return node_id, ip, int(port)
        return None, None, None

    @admin_bp.route('/info', methods=['GET'])
    def node_info():
        """
        Returns basic info about this node: Node ID, enode, peer count, and peer list.
        """
        # Retrieve references from Flask's current_app config
        blockchain = current_app.config.get('blockchain')
        if not blockchain:
            return jsonify({"error": "Blockchain not found in app config"}), 500

        # If you store a P2P network reference in blockchain, or separately in app.config:
        network = current_app.config.get('network') or getattr(blockchain, 'p2p_network', None)
        if not network:
            return jsonify({"error": "Network not found"}), 500

        # If your blockchain object already has node_id or a method get_enode(), adapt as needed:
        node_id = getattr(blockchain, 'node_id', 'N/A')
        enode = getattr(blockchain, 'get_enode', lambda: 'N/A')()

        info = {
            "node_id": node_id,
            "enode": enode,
            "peer_count": len(network.peers),
            "peers": list(network.peers.keys())
        }
        return jsonify(info), 200

    @admin_bp.route('/connectPeer', methods=['POST'])
    def connect_peer():
        """
        Connects to a peer given an enode address:
        Expects JSON: { "enode": "enode://<node_id>@<ip>:<port>" }
        """
        data = request.get_json() or {}
        enode = data.get('enode')
        if not enode:
            return jsonify({"error": "Missing 'enode' parameter"}), 400

        blockchain = current_app.config.get('blockchain')
        if not blockchain:
            return jsonify({"error": "Blockchain not found in app config"}), 500
        network = current_app.config.get('network') or getattr(blockchain, 'p2p_network', None)
        if not network:
            return jsonify({"error": "Network not found"}), 500

        node_id, ip, port = parse_enode(enode)
        if not node_id or not ip or not port:
            return jsonify({"error": "Invalid enode format"}), 400

        try:
            # Use your existing method to connect to a peer:
            # e.g., network.connect_to_peer(enode) or network.connect_to_peer(ip, port).
            network.connect_to_peer(enode)
            return jsonify({"status": "Peer connection initiated", "enode": enode}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @admin_bp.route('/disconnectPeer', methods=['POST'])
    def disconnect_peer():
        """
        Disconnects from a peer given an enode address:
        Expects JSON: { "enode": "enode://<node_id>@<ip>:<port>" }
        """
        data = request.get_json() or {}
        enode = data.get('enode')
        if not enode:
            return jsonify({"error": "Missing 'enode' parameter"}), 400

        blockchain = current_app.config.get('blockchain')
        if not blockchain:
            return jsonify({"error": "Blockchain not found in app config"}), 500
        network = current_app.config.get('network') or getattr(blockchain, 'p2p_network', None)
        if not network:
            return jsonify({"error": "Network not found"}), 500

        try:
            if enode in network.peers:
                peer_socket = network.peers.pop(enode, None)
                if peer_socket:
                    peer_socket.close()
                return jsonify({"status": "Peer disconnected", "enode": enode}), 200
            else:
                return jsonify({"error": "Peer not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return admin_bp

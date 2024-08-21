# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module handles networking, messaging, and the connection
# between different nodes.

import socket
import threading
import json
import os
import uuid
from parameters import parameters
from server import blockchain

class P2PNetwork:
    def __init__(self, host='0.0.0.0', port=5000):
        self.peers = {}
        self.host = host
        self.port = port
        self.server = None
        self.node_id = f"node://{uuid.uuid4()}@{self.host}:{self.port}"  # Concatenated Node Identifier
        self.max_peers = parameters.get("max_node_peers", 128)
        self.prime_bootnodes = [
            "node://prime_bootnode_id1@192.0.2.1:30303",
            "node://prime_bootnode_id2@192.0.2.2:30303",
            "node://prime_bootnode_id3@192.0.2.3:30303"
        ]  # List of Prime Bootnodes
        self.is_prime_node = False  # Flag to check if this node is the prime node

    def start_server(self):
        """Start the server to listen for incoming peer connections."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(self.max_peers)
        print(f"Server started on {self.host}:{self.port}, Node ID: {self.node_id}")

        threading.Thread(target=self.accept_peers).start()

    def accept_peers(self):
        """Accept incoming peer connections."""
        while True:
            client, address = self.server.accept()
            if len(self.peers) < self.max_peers:
                peer_id = client.recv(1024).decode('utf-8')
                self.peers[peer_id] = client
                print(f"New connection from {address}, Peer ID: {peer_id}")
                threading.Thread(target=self.handle_peer, args=(client, peer_id)).start()
                self.exchange_peers(client)
            else:
                client.close()

    def handle_peer(self, client, peer_id):
        """Handle incoming messages from a peer."""
        while True:
            try:
                data = client.recv(1024).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                self.process_message(message, peer_id)
            except (socket.error, json.JSONDecodeError) as e:
                print(f"Error handling peer {peer_id}: {e}")
                self.peers.pop(peer_id, None)
                client.close()
                break

    def process_message(self, message, peer_id):
        """Process and respond to incoming messages from peers."""
        if not isinstance(message, dict) or 'type' not in message:
            print(f"Received invalid message from {peer_id}")
            return
        
        message_type = message.get('type')

        if message_type == 'transaction':
            transaction = message['transaction']
            response = blockchain.new_transaction(**transaction)
            self.broadcast(response, exclude_peer=peer_id)

        elif message_type == 'block':
            block = message['block']
            if blockchain.validate_block(block):
                blockchain.chain.append(block)
                self.broadcast(block, exclude_peer=peer_id)

        elif message_type == 'peer_list':
            peers = message['peers']
            for peer in peers:
                if peer['node'] not in self.peers and len(self.peers) < self.max_peers:
                    self.connect_to_peer(peer['node'])

    def broadcast(self, data, exclude_peer=None):
        """Broadcast data to all connected peers except the sender."""
        for peer_id, peer in self.peers.items():
            if peer_id != exclude_peer:
                try:
                    peer.send(json.dumps(data).encode('utf-8'))
                except socket.error as e:
                    print(f"Error broadcasting to peer {peer_id}: {e}")
                    self.peers.pop(peer_id, None)
                    peer.close()

    def connect_to_peer(self, node):
        """Connect to a new peer using the full node string."""
        if node in self.peers:
            print(f"Already connected to {node}")
            return
        
        parsed_node = self.parse_node_string(node)
        peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            peer.connect((parsed_node['host'], parsed_node['port']))
            peer_id = node
            self.peers[peer_id] = peer
            peer.send(self.node_id.encode('utf-8'))
            print(f"Connected to {parsed_node['host']}:{parsed_node['port']}, Peer ID: {peer_id}")
            threading.Thread(target=self.handle_peer, args=(peer, peer_id)).start()
        except socket.error as e:
            print(f"Failed to connect to {node}: {e}")

    def parse_node_string(self, node_string):
        """Parse a node string in the format 'node://<node_id>@<ip>:<port>'."""
        node_id_part, address_part = node_string.split('@')
        host, port = address_part.split(':')
        return {'node_id': node_id_part, 'host': host, 'port': int(port)}

    def exchange_peers(self, client):
        """Exchange peer information with a new peer."""
        peer_list = [{'node': pid} for pid in self.peers.keys()]
        client.send(json.dumps({'type': 'peer_list', 'peers': peer_list}).encode('utf-8'))

    def load_bootnodes(self, bootnodes_file='bootnodes.json'):
        """Load and connect to bootnodes from a file."""
        bootnodes = []

        # Try connecting to prime bootnodes first
        for node in self.prime_bootnodes:
            try:
                self.connect_to_peer(node)
            except Exception as e:
                print(f"Failed to connect to prime bootnode {node}: {e}")
        
        # Load bootnodes from the file if the prime bootnodes fail
        if os.path.exists(bootnodes_file):
            with open(bootnodes_file, 'r') as file:
                bootnodes = json.load(file)
                for node in bootnodes:
                    self.connect_to_peer(node['node'])

        # If no connections established, consider self as prime node
        if not self.peers:
            self.is_prime_node = True
            print("No bootnodes found. This node is now the prime node.")

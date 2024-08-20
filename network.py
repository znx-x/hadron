# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Handles the peer-to-peer networking, including peer discovery,
# connection management, and message handling.

import socket
import threading
import json

class P2PNetwork:
    def __init__(self, host='0.0.0.0', port=5000):
        self.peers = []
        self.host = host
        self.port = port
        self.server = None

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        threading.Thread(target=self.accept_peers).start()

    def accept_peers(self):
        while True:
            client, address = self.server.accept()
            self.peers.append(client)
            print(f"New connection from {address}")
            threading.Thread(target=self.handle_peer, args=(client,)).start()

    def handle_peer(self, client):
        while True:
            try:
                data = client.recv(1024).decode('utf-8')
                if not data:
                    break
                self.broadcast(data, client)
            except:
                self.peers.remove(client)
                client.close()
                break

    def broadcast(self, data, client):
        for peer in self.peers:
            if peer != client:
                try:
                    peer.send(data.encode('utf-8'))
                except:
                    self.peers.remove(peer)
                    peer.close()

    def connect_to_peer(self, host, port):
        peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer.connect((host, port))
        self.peers.append(peer)
        print(f"Connected to {host}:{port}")
        threading.Thread(target=self.handle_peer, args=(peer,)).start()

# Example usage
if __name__ == "__main__":
    network = P2PNetwork()
    network.start_server()

# server.py

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

import threading
import logging
from blockchain import blockchain
from network import P2PNetwork
from api import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

def start_node():
    # Start the blockchain node
    logging.info("Starting blockchain node...")
    blockchain.run_node()

def start_network():
    # Start the P2P network
    logging.info("Starting P2P network...")
    p2p_network = P2PNetwork(host='0.0.0.0', port=5001)
    p2p_network.start_server()

def start_api():
    # Start the Flask API server
    logging.info("Starting API server...")
    app = create_app()
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Start node, networking, and API server in separate threads
    logging.info("Initializing...")
    threading.Thread(target=start_node).start()
    threading.Thread(target=start_network).start()
    threading.Thread(target=start_api).start()

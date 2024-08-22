# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Manages the core blockchain operations, including block creation,
# transaction handling, and proof-of-work.

import threading
import logging
from node import Blockchain
from network import P2PNetwork
from api import create_app
from miner import Miner
from parameters import parameters  # Import the parameters from parameters.py
import signal
import sys
import time
from waitress import serve  # Use waitress for production-ready server


# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# Initialize the blockchain
blockchain = Blockchain()

# Initialize P2P Network
p2p_network = P2PNetwork(host=parameters['p2p_host'], port=parameters['p2p_port'] + 1)

# Initialize Miner
miner = Miner(wallet_address=parameters['miner_wallet_address'], p2p_network=p2p_network, blockchain=blockchain)

# Initialize shutdown flag
shutdown_flag = threading.Event()

def start_node(shutdown_flag):
    """Start the blockchain node."""
    logging.info("Starting blockchain node...")
    blockchain.run_node(shutdown_flag)

def start_network(shutdown_flag):
    """Start the P2P network."""
    logging.info("Starting P2P network...")
    p2p_network.start_server()

def start_miner(shutdown_flag):
    """Start the mining process."""
    logging.info("Starting miner...")
    miner_thread = threading.Thread(target=miner.start_mining)
    miner_thread.start()
    return miner_thread

def start_api(shutdown_flag):
    """Start the Flask API server."""
    logging.info("Starting API server...")
    app = create_app(blockchain, miner)
    server = threading.Thread(target=serve_api, args=(app, shutdown_flag))
    server.start()
    return server

def serve_api(app, shutdown_flag):
    """Serve the Flask API using Waitress."""
    serve(app, host=parameters['host'], port=parameters['port'], threads=4)

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logging.info("Shutdown signal received. Stopping all services...")
    shutdown_flag.set()
    blockchain.stop_node()  # Ensure we shut down cleanly
    time.sleep(2)  # Allow time for clean shutdown
    logging.info("All services stopped. Exiting now.")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start services
    logging.info("Initializing services...")
    node_thread = threading.Thread(target=start_node, args=(shutdown_flag,))
    network_thread = threading.Thread(target=start_network, args=(shutdown_flag,))
    miner_thread = start_miner(shutdown_flag)
    api_thread = start_api(shutdown_flag)
    node_thread.start()
    network_thread.start()

    # Keep the main thread alive to listen for shutdown signals
    try:
        while not shutdown_flag.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

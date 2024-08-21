# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

import signal
import threading
from network import P2PNetwork
from api import create_app
from node import Blockchain

# Event to signal shutdown
shutdown_event = threading.Event()

def start_network():
    try:
        p2p_network = P2PNetwork()
        p2p_network.start_server()
        while not shutdown_event.is_set():
            # Accept peers or perform network operations
            pass
    except RuntimeError:
        print("RuntimeError caught during shutdown.")
    finally:
        p2p_network.shutdown()

def signal_handler(sig, frame):
    print("Signal received, shutting down...")
    shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Start your blockchain node and network
blockchain = Blockchain()
network_thread = threading.Thread(target=start_network)
network_thread.start()

# Start the API server
app = create_app(blockchain)
app.run(host=blockchain.parameters['host'], port=blockchain.parameters['port'])

# Wait for the network thread to finish before exiting
network_thread.join()

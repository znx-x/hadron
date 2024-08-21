# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# This module handles the blockchain consensus mechanism and ensures
# all nodes work in synergy to keep the blockchain running.

from server import blockchain
from pow import MineH
from network import P2PNetwork

class Consensus:
    def __init__(self, p2p_network: P2PNetwork):
        self.mineh = MineH()
        self.p2p_network = p2p_network

    def adjust_difficulty(self, previous_blocks: list, target_time_per_block: int = 15) -> int:
        """Adjusts the mining difficulty based on the time taken to mine the last blocks."""
        total_time = previous_blocks[-1]['timestamp'] - previous_blocks[0]['timestamp']
        average_time = total_time / len(previous_blocks)
        if average_time < target_time_per_block:
            return previous_blocks[-1]['difficulty'] + 1
        elif average_time > target_time_per_block:
            return max(previous_blocks[-1]['difficulty'] - 1, 1)
        return previous_blocks[-1]['difficulty']

    def achieve_consensus(self):
        """Ensures all nodes in the network agree on the longest valid chain."""
        longest_chain = blockchain.chain
        for peer_chain in self.get_peer_chains():
            if len(peer_chain) > len(longest_chain) and self.is_chain_valid(peer_chain):
                longest_chain = peer_chain
        if longest_chain != blockchain.chain:
            blockchain.chain = longest_chain

    def get_peer_chains(self):
        """Retrieves blockchain data from connected peers."""
        peer_chains = []
        for peer_id, peer_socket in self.p2p_network.peers.items():
            try:
                peer_socket.send(json.dumps({"type": "request_chain"}).encode('utf-8'))
                data = peer_socket.recv(4096).decode('utf-8')
                chain = json.loads(data)
                if self.is_chain_valid(chain):
                    peer_chains.append(chain)
            except Exception as e:
                print(f"Failed to retrieve chain from peer {peer_id}: {e}")
        return peer_chains

    def is_chain_valid(self, chain):
        """Validates a blockchain."""
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]

            # Check that the block's previous hash matches the hash of the previous block
            if current_block['previous_hash'] != blockchain.hash_block(previous_block):
                return False

            # Check that the block's hash meets the difficulty criteria
            if not self.mineh.is_valid_hash(current_block['hash'], current_block['difficulty']):
                return False

        return True

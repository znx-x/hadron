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

import json
import logging
from pow import MineH
from network import P2PNetwork
from parameters import parameters

class Consensus:
    def __init__(self, p2p_network: P2PNetwork, blockchain, mineh):
        self.mineh = mineh
        self.p2p_network = p2p_network
        self.blockchain = blockchain

    def adjust_difficulty(self, previous_blocks: list) -> int:
        """
        Adjusts the mining difficulty based on the time taken to mine the last blocks.

        :param previous_blocks: List of previous blocks to consider for difficulty adjustment.
        :return: New difficulty level (scaled by 10^8).
        """
        target_time_per_block = parameters['block_time']  # Use the block time from parameters directly
        adjustment_interval = parameters['difficulty_adjustment_period']
        scale_factor = 10**8

        if len(previous_blocks) < adjustment_interval + 1:
            return parameters['initial_difficulty']

        # Fetch the timestamps for the blocks used in the adjustment
        last_block_time = previous_blocks[-1]['timestamp']
        first_block_in_interval_time = previous_blocks[-(adjustment_interval + 1)]['timestamp']
        total_time = last_block_time - first_block_in_interval_time

        # Expected total time for the blocks
        expected_time = target_time_per_block * adjustment_interval

        # Calculate the new difficulty
        adjustment_ratio = total_time / expected_time  # Adjust ratio should be total_time/expected_time
        current_difficulty = previous_blocks[-1]['difficulty']

        # Calculate the potential new difficulty
        new_difficulty = int(current_difficulty / adjustment_ratio)

        # Ensure the adjustment is capped to a maximum of 10% increase or decrease
        max_increase = int(current_difficulty * parameters['max_difficulty_increase'])
        max_decrease = int(current_difficulty * parameters['max_difficulty_decrease'])

        # Apply the cap to the adjustment
        if new_difficulty > max_increase:
            new_difficulty = max_increase
        elif new_difficulty < max_decrease:
            new_difficulty = max_decrease

        # Ensure the new difficulty does not fall below the minimum threshold
        new_difficulty = max(new_difficulty, 100000000)

#        logging.info(f"Difficulty adjusted from {previous_blocks[-1]['difficulty']} to {new_difficulty} "
#                    f"based on total time {total_time:.2f}s (expected {expected_time:.2f}s)")

#        logging.info(f"Proposed Difficuty Adjustment: {new_difficulty}")

        return new_difficulty

    def achieve_consensus(self):
        """Ensures all nodes in the network agree on the longest valid chain."""
        longest_chain = self.blockchain.chain
        for peer_chain in self.get_peer_chains():
            if len(peer_chain) > len(longest_chain) and self.is_chain_valid(peer_chain):
                longest_chain = peer_chain
        if longest_chain != self.blockchain.chain:
            self.blockchain.chain = longest_chain

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
            if current_block['previous_hash'] != self.blockchain.hash_block(previous_block):
                return False

            # Check that the block's hash meets the difficulty criteria
            if not self.mineh.is_valid_hash(current_block['hash'], current_block['difficulty']):
                return False

        return True

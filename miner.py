from server import blockchain

def mine():
    while True:
        blockchain.mine_block()

if __name__ == "__main__":
    mine()


class Blockchain:

    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        # Adds a new block to the blockchain.
        pass

    def new_transaction(self):
        # Adds a new transaction to a block.
        pass

    @property
    def last_block(self):
        # returns the last block.
        pass

    @staticmethod
    def hash(block):
        # Generates a block's hash
        pass

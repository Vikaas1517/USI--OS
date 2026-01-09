import hashlib
import json
import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Create a unique string based on contents
        block_string = json.dumps(self.data, sort_keys=True) + str(self.index) + str(self.timestamp) + self.previous_hash
        return hashlib.sha256(block_string.encode()).hexdigest()

class IndustrialBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time.time(), "Genesis Block - System Init", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        """Adds a new event to the ledger."""
        prev_block = self.get_latest_block()
        new_block = Block(
            index=prev_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=prev_block.hash
        )
        self.chain.append(new_block)
        return new_block
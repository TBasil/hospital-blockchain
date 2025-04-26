from .block import Block
from .transaction import MedicalTransaction
from typing import List, Dict
import hashlib
import json
from time import time

class HealthcareBlockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.current_transactions: List[Dict] = []
        self.nodes = set()
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time(), "0")
        self.chain.append(genesis_block)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: MedicalTransaction) -> int:
        self.current_transactions.append(transaction.to_dict())
        return self.last_block.index + 1

    def mine_block(self) -> Block:
        if not self.current_transactions:
            return None

        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.current_transactions,
            timestamp=time(),
            previous_hash=last_block.compute_hash()
        )
        
        self.current_transactions = []
        self.chain.append(new_block)
        return new_block

    def validate_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current.previous_hash != previous.compute_hash():
                return False
                
            if current.compute_hash() != current.compute_hash():
                return False
                
        return True
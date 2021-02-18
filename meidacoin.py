# Create a Blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify


# Part 1 - building a blockchain

class Blockchain:
        
    # inicialize the blockchain
    def __init__(self):
        self.chain = []
        # creates the genesis block
        self.create_block(proof = 1, previous_hash = '0' )


    # used after minning a block and founded the proof
    # or in the first block creation
    def create_block(self, proof, previous_hash):
        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            }
        
        # adds to the chain 
        self.chain.append(block)
        return block
    
    
    
    # returns the last block of the chain 
    def get_last_block(self):
        return self.chain[-1]
    
    
    # finds a new proof considering the last proof
    # considering 4 zeros in front
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            # creates an hash
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest() 
            # founded new proof
            if hash_operation[:4] == '0000':
                check_proof = True
            # tries to find another with new proof
            else:
                new_proof += 1
                
        return new_proof
    
    
    # hashing a block information
    def hash(self, block):
        # puts block dict as a string in the right format
        encoded_block = json.dumps(block, sort_keys=True).encode()
        # returns the hash in hexadecimal
        return hashlib.sha256(encoded_block).hexdigest()
        
                
                
    # check if the chain block are valid
    def is_chain_valid(self, chain):
        
        # first block of the chain
        previous_block = chain[0]
        # second block
        block_index = 1
       
        # stop when blcok_index is in the last block of the chain
        while block_index < len(chain):
            
            # current block
            block = chain[block_index]
            
            # check if previous hash parameter of the block is equal
            # to the hash of the previous block in the chain
            if block['previous_hash'] != self.hash(previous_block):
                # chain is not valid
                return False
            
            # proof of the previous block
            previous_proof = previous_block['proof']
            # rpoof of the current block
            proof = block['proof']
            
            # checks if hashoperation starts with 4 leading zeros
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest() 
            if hash_operation[:4] != '0000':
                # chain is not valid    
                return False
            
            previous_block = block
            block_index += 1
        return True    
                
                
                
                
                
# Creating a web app
app = Flask(__name__)

# creating a blockchain
blockchain = Blockchain()
   

# Route mining a new block             
@app.route('/mine_block', methods=['GET'])             
def mine_block():
    # gets previous block
    previous_block = blockchain.get_last_block()
    # get proof from last block in the chain
    previous_proof = previous_block['proof']
    
    # gets a new proof    
    proof = blockchain.proof_of_work(previous_proof)
                
    # gets the previous hash
    previous_hash = blockchain.hash(previous_block)
    
    # creates the new block
    block = blockchain.create_block(proof, previous_hash)
                
                
    response = {'message': 'You just mined an block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}         
    
                
    return jsonify(response), 200            
       



@app.route('/is_valid', methods=['GET'])
def is_valid():         
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'The chain of the blockchain is valid'}
    else:
         response = {'message': 'The chain of the blockchain is not valid'}
    return jsonify(response), 200

          
# Route getting the fulll blockchain
@app.route('/get_chain', methods=['GET'])             
def get_chain():
    # gets the hole chain
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
               
                
    return jsonify(response), 200            

                
                
                
                
# running the app
app.run(host = '0.0.0.0', port = 5000)               
                
                
                
                
                
                
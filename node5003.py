# Create a Cryptocurrency


import datetime
import hashlib
import json
import requests
from uuid import uuid4
from urllib.parse import urlparse
from flask import Flask, jsonify, request


# Part 1 - building a blockchain

class Blockchain:
        
    # inicialize the blockchain
    def __init__(self):
        self.chain = []
        # variable will be emptied after inserted in the block
        self.transactions = []
        # creates the genesis block
        self.create_block(proof = 1, previous_hash = '0' )
        # will contain the nodes 
        self.nodes = set()


    # used after minning a block and founded the proof
    # or in the first block creation
    def create_block(self, proof, previous_hash):
        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
            }
        
        # empty the list 
        self.transactions = []
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
                
                
    def add_transaction(self, sender, receiver, amount):
        # adds the new transaction to the list of transactions
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})                
        previous_block = self.get_last_block()
        # returns the index of the current block 
        return previous_block['index'] + 1             
                
                
    def add_node(self, address):
        # parsses the url 
        parsed_url = urlparse(address)
        # adds only the netlock of the url , Ex: 127.0.0.1:5000
        self.nodes.add(parsed_url.netloc)
                
        
        
        
    # consensus protocol 
    # if there is a bigger chain in other node,     
    # this node must be updated to that chain    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
        
# Creating a web app
app = Flask(__name__)

# Creating an adress for our node on Port 5000
node_address =  str(uuid4()).replace('-','')

# creating a blockchain
blockchain = Blockchain()











# ROUTES

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
    
    # adds the transaction to the one who minned (compensation to minner)
    blockchain.add_transaction(sender= node_address, receiver='node5003', amount=6.5)
    
    # creates the new block
    block = blockchain.create_block(proof, previous_hash)
                
                
    response = {'message': 'You just mined an block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}         
    
                
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

                
 # post for new transaction                
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    
    # requested keys
    transaction_keys = ['sender', 'receiver', 'amount']     
    # checks if there are not missing keys     
    if not all (key in json for key in transaction_keys):
        return "Some elements of the transaction are missing", 400
    
    # adds the transaction to the blockchain transactions
    # returns the index of the transaction
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    
    reponse = {'messsage': f'This transaction  will be added to Block {index}'}
    return jsonify(reponse), 201



# connecting al nodes in the blockchain
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    
    # list of nodes to connect in the blockchain
    # each node is an url 
    nodes = json.get('nodes')
    
    if nodes is None:
        return "No nodes", 400
    
    for node in nodes:
        # adds each node to the blockchain
        blockchain.add_node(node)

    response = {'message': 'All the nodes are now connected. Contains the following:',
                'total_nodes': list(blockchain.nodes)}

    return jsonify(response), 201



# replacing the chain by the longest if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():         
    
    # runs teh cocensus protocol
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains, but they were all replaced by the longest',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'Your chain is the longest one',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200






# running the app
app.run(host = '0.0.0.0', port = 5003)               
                
                
                
                
                
                
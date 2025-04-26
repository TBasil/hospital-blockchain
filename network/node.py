from flask import Flask, request, jsonify
from core.blockchain import HealthcareBlockchain
from core.transaction import MedicalTransaction 
from utils.crypto import generate_keys
import threading
import time
import requests  # Added for node communication

app = Flask(__name__)
blockchain = HealthcareBlockchain()

# Home endpoint
@app.route('/')
def home():
    return """
    Hospital Blockchain Node API<br><br>
    Endpoints:<br>
    - GET /chain : View full blockchain<br>
    - POST /transactions/new : Add new transaction<br>
    - GET /mine : Mine new block<br>
    - POST /nodes/register : Register new nodes<br>
    - GET /nodes/resolve : Resolve chain conflicts<br>
    """

# Node registration endpoint
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    
    if not values or 'nodes' not in values:
        return "Error: Please supply a valid list of nodes", 400
    
    nodes = values['nodes']
    if not isinstance(nodes, list):
        return "Error: Nodes must be a list", 400
    
    for node in nodes:
        blockchain.nodes.add(node)
    
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

# Chain resolution endpoint
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = resolve_conflicts()
    
    response = {
        'message': 'Our chain is authoritative',
        'chain': [block.__dict__ for block in blockchain.chain]
    }
    
    if replaced:
        response['message'] = 'Our chain was replaced'
    
    return jsonify(response), 200

def resolve_conflicts():
    """Consensus algorithm to resolve conflicts"""
    longest_chain = None
    max_length = len(blockchain.chain)

    for node in blockchain.nodes:
        try:
            response = requests.get(f'{node}/chain', timeout=5)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                if length > max_length and blockchain.validate_chain(chain):
                    max_length = length
                    longest_chain = chain
        except requests.exceptions.RequestException:
            continue
    
    if longest_chain:
        blockchain.chain = longest_chain
        return True
    return False

# Your existing endpoints
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['patient_id', 'doctor_id', 'record_type', 'data']
    if not all(k in values for k in required):
        return "Missing values", 400
        
    transaction = MedicalTransaction(
        values['patient_id'],
        values['doctor_id'],
        values['record_type'],
        values['data'],
        signature=values.get('signature')
    )
    
    index = blockchain.add_transaction(transaction)
    return jsonify({'message': f'Transaction added to Block {index}'}), 201

@app.route('/mine', methods=['GET'])
def mine():
    block = blockchain.mine_block()
    if not block:
        return jsonify({'message': 'No transactions to mine'}), 400
        
    response = {
        'message': "New Block Mined",
        'index': block.index,
        'transactions': block.transactions,
        'previous_hash': block.previous_hash
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': [block.__dict__ for block in blockchain.chain],
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

def start_miner():
    while True:
        time.sleep(10)
        with app.app_context():
            mine()

if __name__ == '__main__':
    miner_thread = threading.Thread(target=start_miner)
    miner_thread.daemon = True
    miner_thread.start()
    
    # Get port from command line or use default 5000
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    
    app.run(host='0.0.0.0', port=args.port)
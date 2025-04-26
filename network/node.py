from flask import Flask, request, jsonify
from core.blockchain import HealthcareBlockchain
from core.transaction import MedicalTransaction
import threading
import time
import requests

app = Flask(__name__)
blockchain = HealthcareBlockchain()

@app.route('/')
def home():
    return "Hospital Blockchain Node - Use endpoints: /transactions/new, /mine, /chain, /nodes/register, /nodes/resolve"

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    try:
        values = request.get_json()
        required = ['patient_id', 'doctor_id', 'record_type', 'data']
        if not all(k in values for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
            
        transaction = MedicalTransaction(
            patient_id=values['patient_id'],
            doctor_id=values['doctor_id'],
            record_type=values['record_type'],
            data=values['data'],
            signature=values.get('signature', '')
        )
        
        index = blockchain.add_transaction(transaction.to_dict())
        return jsonify({'message': f'Transaction added to Block {index}'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    if not values or 'nodes' not in values:
        return "Error: Please supply a valid list of nodes", 400
    
    for node in values['nodes']:
        blockchain.nodes.add(node)
    
    return jsonify({
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    longest_chain = None
    max_length = len(blockchain.chain)

    for node in blockchain.nodes:
        try:
            response = requests.get(f'{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length:
                    max_length = length
                    longest_chain = chain
        except:
            continue

    if longest_chain:
        blockchain.chain = longest_chain
        return jsonify({
            'message': 'Chain was replaced',
            'new_chain': blockchain.chain
        }), 200
    return jsonify({
        'message': 'Chain is authoritative',
        'chain': blockchain.chain
    }), 200

def start_miner():
    while True:
        time.sleep(10)
        with app.app_context():
            mine()

if __name__ == '__main__':
    miner_thread = threading.Thread(target=start_miner)
    miner_thread.daemon = True
    miner_thread.start()
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=True)
from blockchains.python.blockchain import Blockchain
from textwrap import dedent
import json
from flask import Flask, jsonify
from uuid import uuid4


app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')

# Instantiate the blockchain
blockchain = Blockchain()


@app.route('/', methods=['GET'])
def life():
    return jsonify({'status': 'OK'})

@app.route('/mine', methods=['GET'])
def mine():
    return 'MINING'

@app.route('/transactions/new', methods=['GET'])
def new_transaction():
    return 'NEW TRANSACTION'

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain,
    }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)

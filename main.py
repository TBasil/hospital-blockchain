from network.node import app
import argparse

def run_node():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)

if __name__ == '__main__':
    run_node()
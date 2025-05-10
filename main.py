import argparse
from network.node import app
from gui.app import run_gui

def run_node(port):
    """Run the blockchain node in network mode"""
    app.run(host='0.0.0.0', port=port, debug=True)

def main():
    parser = argparse.ArgumentParser(description='Hospital Blockchain System')
    parser.add_argument(
        '--mode', 
        choices=['gui', 'node'], 
        default='gui',
        help='Run in GUI mode or network node mode (default: gui)'
    )
    parser.add_argument(
        '-p', '--port', 
        type=int, 
        default=5000,
        help='Port to use in node mode (default: 5000)'
    )
    args = parser.parse_args()

    if args.mode == 'gui':
        run_gui()
    else:
        run_node(args.port)

if __name__ == '__main__':
    main()
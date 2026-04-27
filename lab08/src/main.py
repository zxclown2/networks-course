import argparse
from peer import Peer
import threading

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--client_port', type=int, default=8888)
    parser.add_argument('--server_port', type=int, default=8080)
    parser.add_argument('--drop_rate', type=float, default=0.3)
    parser.add_argument('--timeout', type=int, default=2)

    args = parser.parse_args()

    server = Peer('server', args.server_port, args.drop_rate, args.timeout)
    client = Peer('client', args.client_port, args.drop_rate, args.timeout)

    t1 = threading.Thread(target=server.serve)
    t1.start()
    t2 = threading.Thread(target=client.serve)
    t2.start()
    client.send_data(args.host, args.server_port, ['packet_1', 'packet_2'])
    server.send_data(args.host, args.client_port, ['packet_3', 'packet_4'])
    server.stop()
    client.stop()
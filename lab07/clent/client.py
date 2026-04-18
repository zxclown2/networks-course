import argparse
import random
import socket
from datetime import datetime


def ping(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)

    for i in range(10):
        try:
            start = datetime.now()
            sock.sendto(f'ping {i * 10 + 1} {start}'.encode('utf-8'), (host, port))
            data, _ = sock.recvfrom(1024)
            end = datetime.now()
            print(f'{data.decode('utf-8')}, RTT: {end - start}')
        except socket.timeout as e:
            print('Request timed out')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8888)

    args = parser.parse_args()

    ping(args.host, args.port)
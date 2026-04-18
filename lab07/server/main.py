import argparse
import socket
import random

def serve(host, port, drop_rate):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            if random.random() < drop_rate:
                print('packet dropped')
                continue

            msg = data.decode('utf-8')
            sock.sendto(msg.upper().encode('utf-8'), addr)
        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8888)
    parser.add_argument('--drop_rate', default=0.2)

    args = parser.parse_args()

    serve(args.host, args.port, args.drop_rate)
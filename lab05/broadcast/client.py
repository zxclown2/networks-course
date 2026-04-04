import argparse
import socket

def start_client(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        try:
            while True:
                data, addr = s.recvfrom(1024)
                time_str = data.decode('utf-8')
                print(time_str)
        except Exception as e:
            print(f'Error: {e}')
            return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="broadcast client")

    parser.add_argument(
        '--port',
        type=int,
        default=8080
    )

    args = parser.parse_args()

    start_client(args.port)

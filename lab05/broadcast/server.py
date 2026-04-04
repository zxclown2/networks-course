import argparse
import socket
import time
import datetime

def start_time_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        try:
            while True:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                s.sendto(current_time.encode('utf-8'), ('255.255.255.255', port))
                
                time.sleep(1)
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

    start_time_server(args.port)


import argparse
import socket

def send_command(server, port, command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((server, port))
            s.sendall(command.encode('utf-8'))            
            data = s.recv(4096)
            return data.decode('utf-8')
        except Exception as e:
            print(e)
            return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="remote client")

    parser.add_argument (
        '--server',
        type=str,
        default='127.0.0.1'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8080
    )

    parser.add_argument(
        '--command',
        type=str
    )

    args = parser.parse_args()

    result = send_command(args.server, args.port, args.command)
    print(result)
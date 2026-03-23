import argparse
import requests

def run_client(server_host, server_port, filename):
    if not filename.startswith('/'):
        filename = '/' + filename

    try:
        response = requests.get(f'http://{server_host}:{server_port}{filename}')
        print(response.text)
    except Exception as e:
        print(f'Error ocured: {e.what()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'server_host', 
        type=str, 
    )
    parser.add_argument(
        'server_port', 
        type=int,
    )
    parser.add_argument(
        'filename',
        type=str,
    )

    args = parser.parse_args()

    run_client(args.server_host, args.server_port, args.filename)
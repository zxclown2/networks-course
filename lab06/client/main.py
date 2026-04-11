import argparse
from ftplib import FTP
from pathlib import Path


class Client:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = 10
        self.ftp = FTP()

    def start(self):
        self.ftp.connect(self.host, self.port, timeout=self.timeout)
        self.ftp.login(self.user, self.password)
        self.ftp.encoding = 'utf-8'

    def close(self):
        self.ftp.close()

    def list_rec(self, path='/', level=0):
        space = '-' * (level * 2)

        try:
            for file, data in self.ftp.mlsd(path):
                if file in ('.', '..'):
                    continue
                if data['type'] == 'file':
                    print(f'{space}{file} {data.get("size", "?")} {data.get("modify", "?")}')
                    continue
                elif data['type'] == 'dir':
                    print(f'{space}{file} {data["modify"]}:')
                    self.list_rec(f'{path.rstrip("/")}/{file}', level + 1)
        except Exception as e:
            print(f'Listing failed: {e}')

    def upload(self, src, dst):
        src_path = Path(src)
        if not src_path.is_file():
            print(f'Upload failed: {src} does no exists')
            return

        try:
            with open(src_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {dst}', f) 
        except Exception as e:
            print(f'Upload failed: {e}')
            return

    def download(self, src, dst):
        try:
            dst_path = Path(dst)
            with open(dst_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {src}', f.write)
        except Exception as e:
            print(f'Downoad failed: {e}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=21)
    parser.add_argument('--user', default='')
    parser.add_argument('--password', default='')

    subparsers = parser.add_subparsers(dest='command', required=True)

    list_parser = subparsers.add_parser('list',)
    list_parser.add_argument('--path', default='/')

    upload_parser = subparsers.add_parser('upload')
    upload_parser.add_argument('src_path')
    upload_parser.add_argument('dst_path')

    download_parser = subparsers.add_parser('download')
    download_parser.add_argument('src_path')
    download_parser.add_argument('dst_path')

    args = parser.parse_args()

    client = Client(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
    )

    try:
        client.start()

        if args.command == 'list':
            client.list_rec(args.path)

        elif args.command == 'upload':
            client.upload(args.src_path, args.dst_path)

        elif args.command == 'download':
            client.download(args.src_path, args.dst_path)

    finally:
        client.close()

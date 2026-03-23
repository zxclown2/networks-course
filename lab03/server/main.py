import argparse
import http.server
import json
import multiprocessing

from concurrent.futures import ProcessPoolExecutor


class WorkerHandler(http.server.BaseHTTPRequestHandler):
    def _send_response(self, content, code):
        encoded_content = content
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded_content)))
        self.end_headers()
        self.wfile.write(encoded_content)

    def do_GET(self):
        content, code = f'file {self.path} not found'.encode('utf-8'), 404
        try:
            with open(self.path, 'rb') as f:
                content, code = f.read(), 200
        except Exception:
            pass
        self._send_response(content, code)


def _run_worker(pipe_conn, host):
    server = http.server.HTTPServer((host, 0), WorkerHandler)
    pipe_conn.send(server.server_port)
    pipe_conn.close()
    
    server.handle_request()
    server.server_close()


class MainHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parent_conn, child_conn = multiprocessing.Pipe(duplex=False)
        
        self.server.pool.submit(_run_worker, child_conn, self.server.server_address[0])
        new_port = parent_conn.recv()
        host_header = self.headers.get('Host', '127.0.0.1').split(':')[0]
        redirect_url = f'http://{host_header}:{new_port}{self.path}'
        
        self.send_response(307)
        self.send_header('Location', redirect_url)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def start_server(port, concurrency):
    server = http.server.HTTPServer(('0.0.0.0', port), MainHandler)
    with ProcessPoolExecutor(max_workers=concurrency) as pool:
        server.pool = pool  
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'port', 
        type=int,
    )
    parser.add_argument(
        'concurrency', 
        type=int, 
    )

    args = parser.parse_args()
    start_server(port=args.port, concurrency=args.concurrency)

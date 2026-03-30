import argparse
import http.server
import json
import logging
import requests
import shelve

logger = logging.getLogger('proxy')

def response_to_dict(response):
    return {
        'status_code': response.status_code,
        'url': response.url,
        'headers': dict(response.headers),
        'content': response.content,
        'encoding': response.encoding
    }

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    CACHE_FILE = "cache"

    def _check_black_list(self, path):
        banned = False
        rule = None
        for item in self.server.black_list:
            if item in path:
                banned = True
                rule = item
                break
        if banned:
            logger.info(f'Request with path {path} banned: [{rule}] in blacklist')
            self._send_response({'status_code': 200, 'content': f'page {path} in black_list'.encode('utf-8'), 'headers': {}})
        return banned

    def _send_response(self, response):
        if not isinstance(response, dict):
            response = response_to_dict(response)

        self.send_response(response['status_code'])
        for key, value in response['headers'].items():
            if key.lower() not in ('transfer-encoding', 'connection', 'content-encoding'):
                self.send_header(key, value)
        self.end_headers()
        if 'content' in response and response['content']:
            self.wfile.write(response['content'])
            
    def _send_error_response(self, message, code=500):
        encoded_content = str(message).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded_content)))
        self.end_headers()
        self.wfile.write(encoded_content)

    def _lookup_cache(self, key):
        try:
            with shelve.open(self.CACHE_FILE) as cache:
                return cache.get(key)
        except Exception:
            return None

    def _store_to_cache(self, key, value):
        with shelve.open(self.CACHE_FILE) as cache:
            cache[key] = value

    def _delete_from_cache(self, key):
        with shelve.open(self.CACHE_FILE) as cache:
            if key in cache:
                del cache[key]
            
    def _forwarded_headers(self):
        forward_headers = dict(self.headers)
        forward_headers.pop('Host', None)
        forward_headers.pop('host', None)
        return forward_headers

    def do_GET(self):
        scheme = 'http'
        url = f'{scheme}://{self.path.lstrip('/')}'

        if self._check_black_list(url):
            return

        key = f'get_{url}'
    
        cached_value = self._lookup_cache(key)
        
        forward_headers = self._forwarded_headers()
        if cached_value:
            cached_headers = cached_value['response']['headers']
            etag = cached_headers.get('ETag')
            last_modified = cached_headers.get('Last-Modified')
            if etag:
                forward_headers['If-None-Match'] = etag
            if last_modified:
                forward_headers['If-Modified-Since'] = last_modified
        try:
            response = requests.get(url, headers=forward_headers, timeout=10)
        except Exception as e:
            self._send_error_response(f'Internal Error: {e}')
            logger.info(f"GET {url}; Code: 500 [Not Cached]")
            return

        if response.status_code == 304:
            self._send_response(cached_value['response'])
            logger.info(f"GET {url}; Code: 304 [From Cache]")
            return

        self._send_response(response)

        if response.status_code == 200:
            cache_value = {'response': response_to_dict(response)}
            self._store_to_cache(key, cache_value)
            logger.info(f"GET {url}; Code: 200 [Cached]")
        elif response.status_code > 399:
            self._delete_from_cache(key)
            logger.info(f"GET {url}; Code: {response.status_code} [Deleted From Cache]")

    def do_POST(self):
        scheme = 'http'
        url = f'{scheme}://{self.path.lstrip('/')}'

        if self._check_black_list(url):
            return

        try:
            content_length = int(self.headers['Content-Length'])
        except Exception:
            self._send_error_response('Missing Content-Length', 400)
            logger.info(f"POST {url}; Code: 400 [Not Cached]")
            return
            
        post_data = self.rfile.read(content_length)

        forward_headers = self._forwarded_headers()
        try:
            response = requests.post(url, headers=forward_headers, data=post_data, timeout=10)
        except Exception as e:
            self._send_error_response(f'Internal Error: {e}', 500)
            logger.info(f"POST {url}; Code: 500 [Not Cached]")
            return

        self._send_response(response)
        logger.info(f"POST {url}; Code: {response.status_code} [Not Cached]")

    def log_message(self, format, *args):
        pass

def start_server(port, black_list):
    server = http.server.HTTPServer(('0.0.0.0', port), ProxyHandler)
    try:
        with open(black_list) as bl:
            server.black_list = [x.strip() for x in bl.read().split(',')]
    except Exception as e:
        server.black_list = []
    server.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Proxy cache")

    parser.add_argument(
        '--port', 
        type=int,
        default=8080
    )

    parser.add_argument(
        '--black_list',
        type=str,
        default=None,
    )

    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('proxy.log', encoding='utf-8')
    logger.addHandler(handler)

    args = parser.parse_args()

    start_server(port=args.port, black_list=args.black_list)

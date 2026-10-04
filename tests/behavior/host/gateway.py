"""Private GitHub substitute plus CONNECT proxy restricted to the configured model endpoint."""
import http.server
import json
import os
from pathlib import Path
import select
import socket
import socketserver
import sys
import threading
import urllib.parse
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from github_stub import GithubStub

ROOT = Path(sys.argv[1]).resolve()
API = urllib.parse.urlsplit(os.environ['ANTHROPIC_BASE_URL'])
LOCK = threading.Lock()


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Never log tokens or request bodies.

    def do_CONNECT(self):
        allowed = f'{API.hostname}:{API.port or 443}'
        if self.path != allowed:
            self.send_error(403, 'Model endpoint only');return
        try:
            remote = socket.create_connection((API.hostname, API.port or 443), timeout=30)
            self.send_response(200, 'Connection established');self.end_headers()
            sockets = [self.connection, remote]
            while True:
                ready, _, _ = select.select(sockets, [], [], 120)
                if not ready:
                    break
                for source in ready:
                    data = source.recv(65536)
                    if not data:
                        return
                    (remote if source is self.connection else self.connection).sendall(data)
        finally:
            if 'remote' in locals():
                remote.close()

    def do_POST(self):
        if self.path != '/gh':
            self.send_error(404);return
        try:
            size = int(self.headers.get('Content-Length', 0))
            if size < 1 or size > 100000:
                raise ValueError('invalid request size')
            value = json.loads(self.rfile.read(size))
            cwd = Path(value['cwd']).resolve()
            if not cwd.is_relative_to(ROOT / 'repo') or not all(isinstance(x, str) for x in value['args']):
                raise ValueError('invalid checkout or arguments')
            with LOCK:
                code, output = GithubStub(ROOT).call(value['args'], cwd)
            body = json.dumps({'code': code, 'output': output}).encode()
            self.send_response(200);self.send_header('Content-Type', 'application/json');self.send_header('Content-Length', str(len(body)));self.end_headers();self.wfile.write(body)
        except (ValueError, KeyError, OSError) as exc:
            self.send_error(400, str(exc))


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


Server(('0.0.0.0', 8080), Handler).serve_forever()

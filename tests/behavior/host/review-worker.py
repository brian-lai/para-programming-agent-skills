"""Credential-free shell service inside the read-only reviewer container."""
import http.server
import json
from pathlib import Path
import re
from worker import execute


def review_command(value):
    if not isinstance(value, dict) or set(value) - {'review_id', 'command', 'timeout'}:
        raise ValueError('invalid review request')
    identity = value.get('review_id', '')
    if not isinstance(identity, str) or not re.fullmatch(r'review-[0-9a-f]{32}', identity):
        raise ValueError('invalid review identity')
    capsule = Path('/review-capsules') / identity
    manifest = json.loads((capsule / 'manifest.json').read_text())
    if manifest['review_id'] != identity:
        raise ValueError('capsule identity mismatch')
    return execute(value, str(capsule / 'source'))


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        if self.path != '/execute':
            self.send_error(404);return
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size <= 100000:
                raise ValueError('invalid request size')
            result = review_command(json.loads(self.rfile.read(size)))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            result = {'exit_code': 1, 'output': str(exc)}
        body = json.dumps(result).encode()
        self.send_response(200);self.send_header('Content-Length', str(len(body)));self.end_headers();self.wfile.write(body)


if __name__ == '__main__':
    http.server.ThreadingHTTPServer(('0.0.0.0', 8091), Handler).serve_forever()

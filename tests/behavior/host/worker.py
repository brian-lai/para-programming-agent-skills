"""Untrusted shell worker. This container has fixture mounts and no model credentials."""
import http.server
import json
import os
from pathlib import Path
import signal
import subprocess
import sys


def execute(value, default_cwd):
    command = value['command']
    if not isinstance(command, str):
        raise ValueError('command must be a string')
    cwd = value.get('cwd') or default_cwd
    timeout = min(max(int(value.get('timeout', 60)), 1), 120)
    p = subprocess.Popen(['bash', '-lc', command], cwd=cwd, text=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, start_new_session=True)
    try:
        output, _ = p.communicate(timeout=timeout)
        return {'exit_code': p.returncode, 'output': output[-2000000:]}
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        output, _ = p.communicate()
        return {'exit_code': 124, 'output': output[-2000000:] + '\nCommand timed out.'}


def serve(default_cwd):
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            if self.path != '/execute':
                self.send_error(404);return
            try:
                size = int(self.headers.get('Content-Length', 0))
                if size < 1 or size > 2000000:
                    raise ValueError('invalid request size')
                value = json.loads(self.rfile.read(size))
                result = execute(value, default_cwd)
            except (OSError, ValueError, KeyError) as exc:
                result = {'exit_code': 1, 'output': str(exc)}
            body = json.dumps(result).encode()
            self.send_response(200);self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)));self.end_headers();self.wfile.write(body)

    http.server.ThreadingHTTPServer(('0.0.0.0', 8090), Handler).serve_forever()


if __name__ == '__main__':
    serve(str(Path(sys.argv[1])))

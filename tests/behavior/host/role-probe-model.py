"""Synthetic Messages stream for CLI capability tests; no real model or credentials.

Forces forbidden calls even when absent from the advertised tool list. Request
logs retain tool names and probe actions only, never request bodies or headers.
"""
import http.server
import json
import threading
from pathlib import Path

LOG = Path('/evidence/model-events.jsonl')
LOCK = threading.Lock()
DONE = threading.Event()


def action(body):
    tools = [t['name'] for t in body.get('tools', [])]
    messages = json.dumps(body.get('messages', []))
    # Role is determined by the actual API tool pool, not a request from the LLM.
    reviewer = 'mcp__review__Bash' in tools and 'mcp__fixture__Bash' not in tools
    background = 'BACKGROUND_PROBE' in messages
    role = ('background' if background else 'foreground') if reviewer else 'author'
    if reviewer:
        sequence = [
            ('writer', 'mcp__fixture__Bash', {'command': 'FORBIDDEN_WRITER'}),
            ('nested', 'Agent', {'subagent_type': 'para-reviewer', 'description': 'Forbidden nested probe', 'prompt': 'NESTED_PROBE'}),
            ('allowed', 'mcp__review__Bash', {'command': role.upper() + '_CONTROL'}),
        ]
    else:
        sequence = [
            ('allowed', 'mcp__fixture__Bash', {'command': 'AUTHOR_CONTROL'}),
            ('unknown', 'Agent', {'subagent_type': 'general-purpose', 'description': 'Unregistered type probe', 'prompt': 'UNKNOWN_PROBE'}),
            ('foreground', 'Agent', {'subagent_type': 'para-reviewer', 'description': 'Foreground role probe', 'prompt': 'FOREGROUND_PROBE', 'run_in_background': False}),
            ('background', 'Agent', {'subagent_type': 'para-reviewer', 'description': 'Background role probe', 'prompt': 'BACKGROUND_PROBE', 'run_in_background': True}),
        ]
    for label, name, arguments in sequence:
        identifier = 'toolu_probe_' + role + '_' + label
        if identifier not in messages:
            return role, tools, identifier, name, arguments
    if role == 'background':
        DONE.set()
    if role == 'author':
        DONE.wait(20)
    return role, tools, 'complete', None, None


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if self.path.endswith('/count_tokens'):
            result = json.dumps({'input_tokens': 1}).encode()
            self.send_response(200);self.send_header('Content-Type', 'application/json');self.end_headers();self.wfile.write(result);return
        role, tools, identifier, name, arguments = action(body)
        with LOCK:
            with LOG.open('a') as stream:
                stream.write(json.dumps({'role': role, 'tools': tools, 'action': identifier, 'tool': name}) + '\n')
        block = {'type': 'tool_use', 'id': identifier, 'name': name, 'input': {}} if name else {'type': 'text', 'text': ''}
        delta = {'type': 'input_json_delta', 'partial_json': json.dumps(arguments)} if name else {'type': 'text_delta', 'text': 'PROBE_COMPLETE ' + role}
        message = {'id': 'msg_' + role + '_' + identifier, 'type': 'message', 'role': 'assistant',
            'model': 'claude-sonnet-5-5', 'content': [], 'stop_reason': None, 'stop_sequence': None,
            'usage': {'input_tokens': 1, 'output_tokens': 1}}
        events = [
            ('message_start', {'type': 'message_start', 'message': message}),
            ('content_block_start', {'type': 'content_block_start', 'index': 0, 'content_block': block}),
            ('content_block_delta', {'type': 'content_block_delta', 'index': 0, 'delta': delta}),
            ('content_block_stop', {'type': 'content_block_stop', 'index': 0}),
            ('message_delta', {'type': 'message_delta', 'delta': {'stop_reason': 'tool_use' if name else 'end_turn', 'stop_sequence': None}, 'usage': {'output_tokens': 1}}),
            ('message_stop', {'type': 'message_stop'}),
        ]
        payload = ''.join('event: ' + event + '\ndata: ' + json.dumps(data) + '\n\n' for event, data in events).encode()
        self.send_response(200);self.send_header('Content-Type', 'text/event-stream');self.send_header('Content-Length', str(len(payload)));self.end_headers();self.wfile.write(payload)


http.server.ThreadingHTTPServer(('0.0.0.0', 8080), Handler).serve_forever()

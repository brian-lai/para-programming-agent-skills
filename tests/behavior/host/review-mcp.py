"""Fixed review adapter in collector; worker bytes remain text, evidence is private."""
import json
from pathlib import Path
import re
import sys
import time
import urllib.request
import uuid

EVIDENCE = Path('/review-evidence/events')
TOOL = {'name': 'Bash', 'description': 'Inspect an immutable review capsule. cwd is its source directory. Read ../manifest.json and ../packet for target and context. Copy source to /tmp for tests requiring writes. Only scratch is writable; no author checkout or network services are accessible.',
    'inputSchema': {'type': 'object', 'additionalProperties': False, 'properties': {'review_id': {'type': 'string'}, 'command': {'type': 'string'}, 'timeout': {'type': 'integer'}}, 'required': ['review_id', 'command']}}


def request_worker(arguments):
    request = urllib.request.Request('http://review-worker:8091/execute', data=json.dumps(arguments).encode(), headers={'Content-Type': 'application/json'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=135) as response:
        return response.read(2100000).decode('utf-8', errors='replace')


def call(arguments):
    if (not isinstance(arguments, dict) or set(arguments) - {'review_id', 'command', 'timeout'}
            or not isinstance(arguments.get('review_id'), str) or not re.fullmatch(r'review-[0-9a-f]{32}', arguments['review_id'])
            or not isinstance(arguments.get('command'), str) or len(arguments['command']) > 90000):
        raise ValueError('invalid review tool arguments')
    identity = 'event-' + uuid.uuid4().hex
    record = {'version': 1, 'event_id': identity, 'input': arguments, 'started': time.time()}
    EVIDENCE.mkdir(exist_ok=True)
    # Retain incomplete requests too. The model cannot choose or replace an event ID.
    path = EVIDENCE / (identity + '.json')
    with path.open('x') as f:
        json.dump(record, f)
    try:
        result = request_worker(arguments)
        record.update(result=result, finished=time.time())
    except (OSError, ValueError) as exc:
        record.update(error=type(exc).__name__ + ': ' + str(exc), finished=time.time())
        raise
    finally:
        path.write_text(json.dumps(record) + '\n')
    return json.dumps({'review_event_id': identity, 'result': result})


def handle(message):
    if 'id' not in message:
        return None
    envelope = {'jsonrpc': '2.0', 'id': message['id']}
    method = message.get('method')
    if method == 'initialize':
        result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'para-review', 'version': '1'}}
    elif method == 'ping':
        result = {}
    elif method == 'tools/list':
        result = {'tools': [TOOL]}
    elif method == 'tools/call' and message.get('params', {}).get('name') == 'Bash':
        try:
            result = {'content': [{'type': 'text', 'text': call(message['params'].get('arguments', {}))}]}
        except (OSError, ValueError) as exc:
            result = {'content': [{'type': 'text', 'text': str(exc)}], 'isError': True}
    else:
        return dict(envelope, error={'code': -32601, 'message': 'Unsupported method or tool'})
    return dict(envelope, result=result)


if __name__ == '__main__':
    for line in sys.stdin:
        try:
            response = handle(json.loads(line))
        except (ValueError, KeyError, TypeError):
            response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid request'}}
        if response is not None:
            print(json.dumps(response), flush=True)

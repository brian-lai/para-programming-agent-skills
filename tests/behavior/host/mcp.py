"""Trusted stdio MCP adapter: worker output is always text inside a tool result.

Only this fixed adapter and the model CLI run in the collector container. Shell
commands run across HTTP in another PID/mount namespace. Never relay raw worker
bytes to stdio or treat a worker-supplied object as a protocol envelope.
"""
import json
import sys
import urllib.request

TOOL = {'name': 'Bash', 'description': 'Run a shell command in the isolated fixture checkout. Use this for Git, gh, file reads/edits and tests. No model credentials or real services are available here.',
        'inputSchema': {'type': 'object', 'properties': {
            'command': {'type': 'string'}, 'cwd': {'type': 'string', 'description': 'Optional absolute working directory.'},
            'timeout': {'type': 'integer', 'description': 'Command timeout in seconds, at most 120.'}}, 'required': ['command']}}


def worker_call(arguments):
    request = urllib.request.Request('http://worker:8090/execute', data=json.dumps(arguments).encode(), headers={'Content-Type': 'application/json'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=135) as response:
        # Even a compromised worker can return only a bounded text payload.
        return response.read(2100000).decode('utf-8', errors='replace')


def handle(message):
    method = message.get('method')
    if 'id' not in message:
        return None
    envelope = {'jsonrpc': '2.0', 'id': message['id']}
    if method == 'initialize':
        result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'para-fixture', 'version': '1'}}
    elif method == 'ping':
        result = {}
    elif method == 'tools/list':
        result = {'tools': [TOOL]}
    elif method == 'tools/call' and message.get('params', {}).get('name') == 'Bash':
        try:
            payload = worker_call(message['params'].get('arguments', {}))
            result = {'content': [{'type': 'text', 'text': payload}]}
        except (OSError, ValueError) as exc:
            result = {'content': [{'type': 'text', 'text': str(exc)}], 'isError': True}
    else:
        return dict(envelope, error={'code': -32601, 'message': 'Unsupported method or tool'})
    return dict(envelope, result=result)


def main():
    for line in sys.stdin:
        try:
            response = handle(json.loads(line))
        except (ValueError, KeyError, TypeError) as exc:
            response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': str(exc)}}
        if response is not None:
            print(json.dumps(response), flush=True)


if __name__ == '__main__':
    main()

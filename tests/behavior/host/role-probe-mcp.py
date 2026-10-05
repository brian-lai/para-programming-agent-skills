"""Capability-probe-only MCP server. It records invocations but NEVER runs commands."""
import json
import sys

role = sys.argv[1]
for line in sys.stdin:
    request = json.loads(line)
    if 'id' not in request:
        continue
    method = request.get('method')
    if method == 'initialize':
        result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}},
                  'serverInfo': {'name': 'para-role-probe-' + role, 'version': '1'}}
    elif method == 'tools/list':
        result = {'tools': [{'name': 'Bash', 'description': 'Dummy role probe; records arguments, executes no command.',
                  'inputSchema': {'type': 'object', 'properties': {'command': {'type': 'string'}}, 'required': ['command']}}]}
    elif method == 'tools/call' and request.get('params', {}).get('name') == 'Bash':
        result = {'content': [{'type': 'text', 'text': json.dumps({'probe_backend': role,
                  'arguments': request['params'].get('arguments'), 'executed_command': False})}]}
    elif method == 'ping':
        result = {}
    else:
        print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'error': {'code': -32601, 'message': 'unknown operation'}}), flush=True)
        continue
    print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result}), flush=True)

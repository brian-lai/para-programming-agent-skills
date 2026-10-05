"""Contracts for the isolated reviewer host (not an installed-skill dependency)."""


def role_definitions():
    return {
        'para-author': {
            'description': 'Author and orchestrate the fixture task.',
            'prompt': 'Carry out the task using its instructions. Delegate independent reviews to para-reviewer.',
            'tools': ['Agent(para-reviewer)', 'mcp__fixture__Bash'],
        },
        'para-reviewer': {
            'description': 'Independently review a supplied artifact using the isolated review tool.',
            'prompt': 'Review the supplied target independently. Use only mcp__review__Bash; return evidence and the reviewed target. Do not delegate further.',
            'tools': ['mcp__review__Bash'],
            'disallowedTools': ['Agent', 'Task', 'Bash', 'Read', 'Write', 'Edit', 'mcp__fixture__Bash'],
        },
    }


def validate_review_capability(evidence):
    required = ('foreground_restricted', 'background_restricted', 'unknown_agent_rejected',
                'nested_delegation_rejected', 'writer_tool_rejected')
    if evidence.get('version') != 1 or any(evidence.get(key) is not True for key in required):
        raise ValueError('review role restrictions are not verified')


def assess_role_probe(events, api_events):
    """Inspect actual native dispatch results from the synthetic-model CLI probe."""
    calls, results = {}, {}
    for event in events:
        for part in event.get('message', {}).get('content', []):
            if part.get('type') == 'tool_use':
                calls[part['id']] = (event.get('parent_tool_use_id'), part)
            elif part.get('type') == 'tool_result':
                results[part['tool_use_id']] = (event.get('parent_tool_use_id'), part)

    def denied(role, label, name, phrase):
        identifier = 'toolu_probe_' + role + '_' + label
        parent = None if role == 'author' else 'toolu_probe_author_' + role
        call = calls.get(identifier);response = results.get(identifier)
        return bool(call and response and call[0] == response[0] == parent and call[1].get('name') == name
                    and response[1].get('is_error') is True and phrase in str(response[1].get('content')))

    def restricted(role):
        pools = [set(row.get('tools', [])) for row in api_events if row.get('role') == role]
        identifier = 'toolu_probe_' + role + '_allowed'
        call = calls.get(identifier);response = results.get(identifier)
        return bool(pools and all(pool == {'mcp__review__Bash'} for pool in pools) and call and response
                    and call[0] == response[0] == 'toolu_probe_author_' + role
                    and call[1].get('name') == 'mcp__review__Bash' and not response[1].get('is_error'))

    return {'version': 1,
            'foreground_restricted': restricted('foreground'), 'background_restricted': restricted('background'),
            'unknown_agent_rejected': denied('author', 'unknown', 'Agent', "Agent type 'general-purpose' not found"),
            'nested_delegation_rejected': all(denied(role, 'nested', 'Agent', 'No such tool available: Agent') for role in ('foreground', 'background')),
            'writer_tool_rejected': all(denied(role, 'writer', 'mcp__fixture__Bash', 'No such tool available: mcp__fixture__Bash') for role in ('foreground', 'background'))}


def validate_review_record(record):
    import re
    if not isinstance(record, dict) or not all(isinstance(record.get(key), str) and record[key] for key in ('review_id', 'native_task_id', 'target')):
        raise ValueError('missing review, native task or target identity')
    if not re.fullmatch('[0-9a-f]{40}', record['target']):
        raise ValueError('PR target must be a full commit identity')

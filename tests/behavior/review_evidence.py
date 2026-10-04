"""Associate native completed reviewer events with a target before a merge call."""
import json
import re
import subprocess
from safe_git import git


def names_target(text, head, repository=None):
    # Match standalone Git object IDs, not arbitrary substrings. A short ID
    # counts only if safe Git resolves exactly one object and it is this head.
    tokens = re.findall(r'(?<![\w])[0-9a-fA-F]{7,40}(?![\w])', text)
    for token in tokens:
        token = token.lower()
        if token == head:
            return True
        if repository is not None and len(token) < 40:
            try:
                matches = git(repository, 'rev-parse', '--disambiguate=' + token).splitlines()
            except subprocess.CalledProcessError:
                continue
            if matches == [head]:
                return True
    return False


def independent_approval(raw, prefix_bytes, head, repository=None):
    if prefix_bytes is None:
        return False
    events = []
    for line in raw[:prefix_bytes].splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass  # A collector write can end in a partial final event.
    tasks, answers, completed = {}, {}, set()
    for event in events:
        for part in event.get('message', {}).get('content', []):
            if not isinstance(part, dict):
                continue
            if part.get('type') == 'tool_use' and part.get('name') in ('Agent', 'Task'):
                tasks[part['id']] = str(part.get('input', {}).get('prompt', ''))
            if event.get('type') == 'assistant' and part.get('type') == 'text' and event.get('parent_tool_use_id'):
                answers[event['parent_tool_use_id']] = part['text']
            if part.get('type') == 'tool_result' and not part.get('is_error'):
                content = part.get('content', '')
                text = content if isinstance(content, str) else '\n'.join(c.get('text', '') for c in content if isinstance(c, dict))
                # Synchronous exports put the final review in the tool result.
                if 'APPROVED' in text and 'Async agent launched' not in text:
                    answers[part['tool_use_id']] = text;completed.add(part['tool_use_id'])
        if event.get('subtype') == 'task_notification' and event.get('status') == 'completed':
            completed.add(event.get('tool_use_id'))
    return any(key in completed and re.search(r'\breview\b', prompt, re.I) and
               names_target(prompt + '\n' + answers.get(key, ''), head, repository) and
               re.search(r'\bAPPROVED\b', answers.get(key, '')) and
               not re.search(r'\b(?:NOT APPROVED|CHANGES REQUESTED)\b', answers.get(key, ''))
               for key, prompt in tasks.items())

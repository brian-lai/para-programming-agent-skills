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



def approved_verdict(text):
    """Recognize explicit unconditional decisions, not mentions of approval."""
    lines = [re.sub(r'[*`#]', '', line).strip() for line in text.splitlines()]
    for line in lines:
        if re.match(r'^(?:Verdict:\s*)?approve(?:d)?\b', line, re.I):
            if re.search(r'\b(if|after|once|pending|provided)\b|subject to|with fixes', line, re.I):
                return False
            return not re.search(r'\b(?:not approved|do not approve|changes requested)\b', text, re.I)
    return False


def completed_isolated_review(events, task, prompt, head, repository):
    answer, complete = '', False
    for event in events:
        for part in event.get('message', {}).get('content', []):
            if event.get('type') == 'assistant' and event.get('parent_tool_use_id') == task and part.get('type') == 'text':
                answer = part['text']
            if part.get('type') == 'tool_result' and part.get('tool_use_id') == task and not part.get('is_error'):
                content = part.get('content', '')
                text = content if isinstance(content, str) else '\n'.join(c.get('text', '') for c in content if isinstance(c, dict))
                if 'Async agent launched' not in text and approved_verdict(text):
                    answer, complete = text, True
        if event.get('subtype') == 'task_notification' and event.get('tool_use_id') == task and event.get('status') == 'completed':
            complete = True
    return complete and approved_verdict(answer) and names_target(prompt + '\n' + answer, head, repository)


def isolated_approval(root, raw, prefix_bytes, head, bindings=None):
    """Require protected adapter events from a completed target-bound native reviewer.

    Missing/corrupt host artifacts raise ValueError (incomplete evidence). A
    captured but absent/mismatched review returns False (ineligible approval).
    Caller separately validates role capability and container boundary records.
    """
    import hashlib
    from review_isolation import file_manifest
    if prefix_bytes is None:
        return False
    events = []
    for line in raw[:prefix_bytes].splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    tasks, calls, responses = {}, {}, {}
    for event in events:
        parent = event.get('parent_tool_use_id')
        for part in event.get('message', {}).get('content', []):
            if part.get('type') == 'tool_use':
                if not parent and part.get('name') in ('Agent', 'Task') and part.get('input', {}).get('subagent_type') == 'para-reviewer':
                    tasks[part['id']] = event
                if parent:
                    calls[part['id']] = (parent, part)
            if part.get('type') == 'tool_result' and parent:
                responses[part['tool_use_id']] = (parent, part)
    for task, spawn in tasks.items():
        prompt = next(p['input'].get('prompt', '') for p in spawn['message']['content'] if p.get('id') == task)
        if not completed_isolated_review(events, task, prompt, head, root / 'remote.git'):
            continue
        task_calls = [(key, part) for key, (parent, part) in calls.items() if parent == task]
        if not task_calls or any(p.get('name') != 'mcp__review__Bash' for _, p in task_calls):
            continue
        useful, valid, associated = 0, True, []
        for key, part in task_calls:
            response = responses.get(key)
            if not response or response[0] != task:
                valid = False;break
            if response[1].get('is_error'):
                continue  # A captured rejected call grants no evidence of inspection.
            content = response[1].get('content')
            try:
                text = content if isinstance(content, str) else '\n'.join(p['text'] for p in content if p.get('type') == 'text')
                wrapper = json.loads(text)
                identity = wrapper.get('review_event_id', '')
                review_id = part.get('input', {}).get('review_id', '')
                if not re.fullmatch('event-[0-9a-f]{32}', identity) or not re.fullmatch('review-[0-9a-f]{32}', review_id):
                    valid = False;break
                path = root / 'review-evidence/events' / (identity + '.json')
                record = json.loads(path.read_text())
                if (record.get('version') != 1 or record.get('event_id') != identity or record.get('input') != part['input']
                        or record.get('result') != wrapper.get('result') or 'finished' not in record or record.get('error')):
                    valid = False;break
                capsule_path = root / 'review-capsules' / review_id
                capsule = json.loads((capsule_path / 'manifest.json').read_text())
                if capsule.get('mode') != 'pr' or capsule.get('target') != head or capsule.get('review_id') != review_id:
                    valid = False;break
                original_digest = capsule.pop('manifest_digest')
                if hashlib.sha256(json.dumps(capsule, sort_keys=True).encode()).hexdigest() != original_digest:
                    raise ValueError('capsule manifest hash mismatch')
                files = file_manifest(capsule_path);files.pop('manifest.json')
                if files != capsule['files'] or hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest() != capsule['capsule_digest']:
                    raise ValueError('capsule content hash mismatch')
                worker = json.loads(record['result'])
                if worker.get('exit_code') == 0:
                    useful += 1
                    associated.append({'version': 1, 'trial_id': root.name, 'review_id': review_id, 'native_task_id': task,
                        'native_tool_id': key, 'event_id': identity, 'target': head, 'manifest_digest': original_digest,
                        'event_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            except (OSError, KeyError, TypeError) as exc:
                raise ValueError('missing or invalid isolated review evidence: ' + str(exc)) from exc
        if valid and useful:
            if bindings is not None:
                bindings.extend(associated)
            return True
    return False


def validate_isolation(root, final=True):
    """Validate protected trial records; absence never upgrades a legacy capture."""
    from review_isolation import role_definitions, validate_review_capability, assess_role_probe
    try:
        policy = json.loads((root / 'review-policy.json').read_text())
        boundary = json.loads((root / 'review-boundary.json').read_text())
        capability_root = root / 'review-evidence/capability'
        capability = json.loads((capability_root / 'probe.json').read_text())
        events = [json.loads(line) for line in (capability_root / 'transcript.jsonl').read_text().splitlines()]
        pools = [json.loads(line) for line in (capability_root / 'model-events.jsonl').read_text().splitlines()]
        validate_review_capability(assess_role_probe(events, pools))
        if (policy.get('version') != 1 or policy.get('roles') != role_definitions()
                or capability.get('status') != 'verified' or capability.get('roles') != policy['roles']
                or capability.get('image_id') != policy.get('image_id')
                or boundary.get('version') != 1 or boundary.get('status') != 'verified'
                or final and boundary.get('cleanup_confirmed') is not True):
            raise ValueError('unverified or inconsistent reviewer boundary')
        return policy
    except (OSError, KeyError, TypeError) as exc:
        raise ValueError('missing isolation evidence: ' + str(exc)) from exc

"""Paired comparisons and bounded native-host capture; no LLM API integration."""
from collections import Counter
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


def compare(baseline, candidate):
    def keyed(rows):
        keys = [(r['case_id'], r['case_version'], r['trial'], r.get('variant', 0)) for r in rows]
        if len(set(keys)) != len(keys):
            raise ValueError('duplicate trial')
        return dict(zip(keys, rows))
    for row in baseline + candidate:
        if 'assertions' in row:
            derived = [a['id'] for a in row['assertions'] if a.get('critical') and not a['pass']]
            if row.get('critical_failures') != derived:
                raise ValueError('critical failure summary disagrees with assertions')
    a, b = keyed(baseline), keyed(candidate)
    if a.keys() != b.keys():
        raise ValueError('unpaired or missing trials')
    for key in a:
        for field in ('host', 'host_version', 'model', 'settings', 'evidence_kind', 'observed_models'):
            if a[key].get(field) != b[key].get(field):
                raise ValueError(f'pair mismatch: {key} {field}')
    added = {'simple_workflow_no_pr', 'simple_workflow_lifecycle', 'resume_after_pr_created', 'stale_review_head', 'partial_archive'}
    def summary(rows):
        revisions = sorted({r['skill_revision'] for r in rows})
        def total(field):
            values = [r.get('usage', {}).get(field) for r in rows]
            return sum(values) if all(v is not None for v in values) else None
        return {'trials': len(rows), 'outcomes': dict(Counter(r['outcome'] for r in rows)),
                'critical_failures': sum(len(r['critical_failures']) for r in rows) if all(r.get('critical_failures') is not None for r in rows) else None,
                'incomplete_critical_evidence': sum(r.get('critical_evidence_complete') is not True for r in rows),
                'input_tokens': total('input_tokens'), 'output_tokens': total('output_tokens'),
                'tool_calls': sum(r['tool_calls'] for r in rows) if all(r.get('tool_calls') is not None for r in rows) else None,
                'questions': sum(r['questions'] for r in rows) if all(r.get('questions') is not None for r in rows) else None,
                'unsupported_findings': sum(r['unsupported_findings'] for r in rows) if all(r.get('unsupported_findings') is not None for r in rows) else None,
                'elapsed_seconds': sum(r.get('elapsed_seconds', 0) for r in rows),
                'mixed_revisions': len(revisions) > 1,
                'by_revision': {rev: {'trials': sum(r['skill_revision'] == rev for r in rows),
                    'outcomes': dict(Counter(r['outcome'] for r in rows if r['skill_revision'] == rev))} for rev in revisions}}
    return {'pairs': len(a), 'baseline': summary(baseline), 'candidate': summary(candidate),
            'groups': {name: {'baseline': summary([r for r in baseline if (r['case_id'] in added) == is_added]),
                              'candidate': summary([r for r in candidate if (r['case_id'] in added) == is_added])}
                       for name, is_added in [('common_tasks', False), ('added_or_extended_workflow_capability', True)]},
            'trial_results': {'baseline': baseline, 'candidate': candidate},
            'limitation': 'Diagnostic sample; incomplete harness evidence and failures are retained. Mixed revisions are not one fully tested candidate.'}


def run_bounded(command, transcript, wall_seconds, tool_limit, env=None, cwd=None):
    """Capture native stdout unchanged, enforcing wall time and observed aggregate tool calls."""
    transcript = Path(transcript)
    start = time.monotonic();reason = None;ids = set();buffer = b''
    with transcript.open('wb') as out, transcript.with_suffix('.stderr').open('wb') as err:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=err, env=env, cwd=cwd, start_new_session=True)
        selector = selectors.DefaultSelector();selector.register(process.stdout, selectors.EVENT_READ)
        while selector.get_map() or process.poll() is None:
            if time.monotonic() - start >= wall_seconds:
                reason = 'wall_timeout';break
            for key, _ in selector.select(timeout=min(0.1, max(0.001, wall_seconds - (time.monotonic() - start)))):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj);continue
                out.write(chunk);out.flush();buffer += chunk
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    try:
                        event = json.loads(line)
                        for part in event.get('message', {}).get('content', []):
                            if isinstance(part, dict) and part.get('type') == 'tool_use':
                                ids.add(part.get('id') or str(len(ids)))
                    except (ValueError, AttributeError):
                        pass
            if len(ids) > tool_limit:
                reason = 'tool_limit';break
        selector.close()
        if reason:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait(timeout=10)
        process.stdout.close()
    return {'elapsed_seconds': time.monotonic() - start, 'termination_reason': reason,
            'tool_calls': len(ids), 'exit_code': process.returncode}

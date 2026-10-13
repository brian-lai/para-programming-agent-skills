"""Offline fixture/grader tests; synthetic evidence never represents a model trial."""
import json
from pathlib import Path
import tempfile
import unittest
from fixtures import prepare, git, dump, context
from graders import grade, read_context

CASES = ('handoff_contract', 'handoff_dependency', 'handoff_stale')


class HandoffTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_arms_have_same_task_source_and_version(self):
        for case in CASES:
            a = prepare(case, self.root / (case+'-a'), handoff_arm='baseline')
            b = prepare(case, self.root / (case+'-b'), handoff_arm='candidate')
            self.assertEqual(a['case_version'], b['case_version'])
            self.assertEqual(a['initial_head'], b['initial_head'])
            self.assertEqual(a['prompt'], b['prompt'])
            self.assertNotEqual(a['handoff']['bundle_sha256'], b['handoff']['bundle_sha256'])
            self.assertEqual(a['handoff']['origin'], 'authored-fixture')
            self.assertEqual(a['handoff']['arm'], 'baseline')

    def test_invalid_arm_combinations_do_not_create_output(self):
        for case, arm in [('handoff_contract', None), ('handoff_contract', 'bogus'), ('docs_only', 'candidate')]:
            path = self.root / (case + str(arm))
            with self.assertRaises(ValueError):
                prepare(case, path, handoff_arm=arm)
            self.assertFalse(path.exists())

    def test_stale_reference_differs_from_actual_source_in_both_arms(self):
        for arm in ('baseline', 'candidate'):
            root = self.root / arm
            data = prepare('handoff_stale', root, handoff_arm=arm)
            repo = root / 'repo'
            self.assertFalse((repo / 'calculator.py').exists())
            self.assertTrue((repo / 'metrics.py').is_file())
            plan = read_context(repo/'context/context.md')['active_context'][0]
            self.assertIn('calculator.py', (repo/plan).read_text())
            self.assertIn('metrics.average', (repo/'README.md').read_text())
            self.assertEqual(data['initial_execution_head'], data['initial_head'])

    def collected(self, arm='candidate'):
        root = self.root / 'run'
        initial = prepare('handoff_contract', root, handoff_arm=arm)
        (root/'transcript.jsonl').write_text(json.dumps({'type':'result','subtype':'success'})+'\n')
        dump(root/'host.json', {'host':'synthetic','host_version':'1','model':'none','settings':{},
            'skill_revision':'test','trial':0,'elapsed_seconds':1,'case_version':initial['case_version'],
            'evidence_kind':'synthetic_grader_test','handoff':initial['handoff']})
        repo=root/'repo';git(repo,'checkout','-b','para/task')
        (repo/'change.txt').write_text('synthetic commit; correctness is supplied as protected validator evidence')
        git(repo,'add','change.txt');git(repo,'commit','-m','Synthetic change')
        ctx=read_context(repo/'context/context.md');ctx.update(execution_branch='para/task')
        context(repo/'context/context.md',ctx)
        head=git(repo,'rev-parse','HEAD')
        dump(root/'validation.json',{'returncode':0,'head':head,'case_id':'handoff_contract',
                                   'validator_version':'handoff-v1'})
        return root

    def test_valid_evidence_grades_and_exports_handoff(self):
        result=grade(self.collected())
        self.assertEqual(result['outcome'],'pass',result)
        self.assertEqual(result['handoff']['arm'],'candidate')

    def test_wrong_behavior_fails_even_with_done_claim(self):
        root=self.collected();path=root/'validation.json';d=json.loads(path.read_text());d['returncode']=1;dump(path,d)
        self.assertEqual(grade(root)['outcome'],'fail')

    def test_missing_validation_is_incomplete(self):
        root=self.collected();(root/'validation.json').unlink()
        self.assertEqual(grade(root)['outcome'],'incomplete')

    def test_stale_validation_head_fails(self):
        root=self.collected();path=root/'validation.json';d=json.loads(path.read_text());d['head']='wrong';dump(path,d)
        self.assertEqual(grade(root)['outcome'],'fail')

    def test_handoff_manifest_mismatch_is_incomplete(self):
        root=self.collected();p=root/'host.json';d=json.loads(p.read_text());d['handoff']['arm']='baseline';dump(p,d)
        self.assertEqual(grade(root)['outcome'],'incomplete')

    def test_empty_commit_does_not_establish_changed_implementation(self):
        root=self.collected();repo=root/'repo';git(repo,'rm','change.txt');git(repo,'commit','-m','Return source to baseline')
        p=root/'validation.json';d=json.loads(p.read_text());d['head']=git(repo,'rev-parse','HEAD');dump(p,d)
        self.assertEqual(grade(root)['outcome'],'fail')

    def test_wrong_validator_identity_is_incomplete(self):
        root=self.collected();p=root/'validation.json';d=json.loads(p.read_text());d['case_id']='other';dump(p,d)
        self.assertEqual(grade(root)['outcome'],'incomplete')

    def test_malformed_validation_is_incomplete(self):
        root=self.collected();dump(root/'validation.json',[])
        self.assertEqual(grade(root)['outcome'],'incomplete')

    def test_legacy_case_has_no_handoff_metadata(self):
        data=prepare('direct_execute_scope',self.root/'legacy')
        self.assertNotIn('handoff',data)

    def test_legacy_fixture_versions_remain_compatible(self):
        expected='5d7a399123b8ea11045281de4bcc72eb3c7b1c9dc5124c32cf093bde031791a2'
        for case in ('direct_execute_scope','docs_only','nondefault_base'):
            data=prepare(case,self.root/case)
            self.assertEqual(data['case_version'],expected)

    def test_legacy_catalog_stays_consistent_with_acceptance_matrix(self):
        from fixtures import CASES
        legacy=json.loads(CASES.with_name('legacy-workflow-cases.json').read_text())['cases']
        current=json.loads(CASES.read_text())['cases']
        self.assertEqual(legacy,[c for c in current if c['id'] not in ('handoff_contract','handoff_dependency','handoff_stale')])

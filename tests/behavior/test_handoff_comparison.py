import copy
import unittest
from comparison import compare
from test_comparison import trial


def row(arm):
    value=trial();value['case_id']='handoff_contract';value['handoff']={
        'arm':arm,'origin':'authored-fixture','bundle_sha256':('a' if arm=='baseline' else 'b')*64,
        'bundle_hashes':{'handoff_contract/baseline.json':'a'*64,'handoff_contract/candidate.json':'b'*64}}
    value['usage']={'input_tokens':100,'output_tokens':20};value['tool_calls']=4
    return value


class HandoffComparisonTest(unittest.TestCase):
    def test_artifact_arms_can_differ_with_fixed_skills(self):
        result=compare([row('baseline')],[row('candidate')])
        self.assertEqual(result['candidate']['per_completed_case']['input_tokens'],100)

    def test_handoff_identity_and_skills_cannot_drift(self):
        for key in ('skill_revision','handoff','settings'):
            a,b=row('baseline'),row('candidate')
            if key=='handoff':b[key]['bundle_hashes']['handoff_contract/baseline.json']='c'*64
            elif key=='settings':b[key]['effort']='other'
            else:b[key]='different'
            with self.subTest(key=key),self.assertRaises(ValueError):compare([a],[b])

    def test_wrong_arm_missing_or_wrong_digest_rejected(self):
        for defect in ('arm','missing','digest'):
            a,b=row('baseline'),row('candidate')
            if defect=='arm':b['handoff']['arm']='baseline'
            elif defect=='missing':b.pop('handoff')
            else:b['handoff']['bundle_sha256']='d'*64
            with self.subTest(defect=defect),self.assertRaises(ValueError):compare([a],[b])

    def test_failed_attempt_cost_is_in_numerator(self):
        a,b=row('baseline'),row('candidate');a2,b2=copy.deepcopy(a),copy.deepcopy(b)
        a2['trial']=b2['trial']=2;b2['outcome']='fail'
        result=compare([a,a2],[b,b2])['candidate']
        self.assertEqual(result['per_completed_case']['input_tokens'],200)
        self.assertEqual(result['outcomes'],{'pass':1,'fail':1})

    def test_zero_successes_and_unknown_cost_stay_null(self):
        a,b=row('baseline'),row('candidate');b['outcome']='fail'
        self.assertIsNone(compare([a],[b])['candidate']['per_completed_case']['input_tokens'])
        b['outcome']='pass';b['usage']['input_tokens']=None
        self.assertIsNone(compare([a],[b])['candidate']['per_completed_case']['input_tokens'])

    def test_incomplete_attempts_and_unknown_time_are_retained(self):
        a,b=row('baseline'),row('candidate');a2,b2=copy.deepcopy(a),copy.deepcopy(b)
        a2['trial']=b2['trial']=2;b2['outcome']='incomplete';b2['elapsed_seconds']=None
        result=compare([a,a2],[b,b2])['candidate']
        self.assertEqual(result['per_completed_case']['tool_calls'],8)
        self.assertIsNone(result['elapsed_seconds'])
        self.assertIsNone(result['per_completed_case']['elapsed_seconds'])

    def test_malformed_metadata_is_rejected(self):
        a,b=row('baseline'),row('candidate');b['handoff']=[]
        with self.assertRaises(ValueError):compare([a],[b])

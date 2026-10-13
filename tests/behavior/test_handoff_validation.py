import importlib.util
import os
from pathlib import Path
import types
import unittest
from unittest.mock import patch
from handoff_validation import contract_code, validation_code

spec=importlib.util.spec_from_file_location('handoff_trial_runner',Path(__file__).resolve().parents[2]/'scripts/run-skill-trial.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


class HandoffValidationTest(unittest.TestCase):
    def test_contract_rejects_wrong_arithmetic_and_accepts_correct(self):
        module=types.ModuleType('calculator')
        def ratio(total,count):
            if count==0:raise ValueError('empty count')
            return total/count
        module.ratio=ratio
        with patch.dict('sys.modules',calculator=module):exec(contract_code('handoff_contract'),{})
        module.ratio=lambda total,count: 5
        with patch.dict('sys.modules',calculator=module),self.assertRaises(AssertionError):exec(contract_code('handoff_contract'),{})

    def test_dependency_checks_weighting_and_boundary(self):
        pricing=types.ModuleType('pricing');invoice=types.ModuleType('invoice')
        pricing.subtotal=lambda items:sum(p*q for p,q in items)
        invoice.total=lambda items:pricing.subtotal(items)+(5 if 0<pricing.subtotal(items)<50 else 0)
        with patch.dict('sys.modules',pricing=pricing,invoice=invoice):exec(contract_code('handoff_dependency'),{})
        invoice.total=lambda items:pricing.subtotal(items)+5
        with patch.dict('sys.modules',pricing=pricing,invoice=invoice),self.assertRaises(AssertionError):exec(contract_code('handoff_dependency'),{})

    def test_dispatch_and_unknown_case(self):
        self.assertIn('from metrics import average',contract_code('handoff_stale'))
        code=validation_code('handoff_contract')
        self.assertIn('checkout',code)
        self.assertIn('unittest',code)
        with self.assertRaises(ValueError):validation_code('docs_only')

    def test_invalid_arm_is_rejected_before_model_or_docker(self):
        args=types.SimpleNamespace(case='handoff_contract',handoff_arm='wrong')
        with patch.dict(os.environ,{},clear=True),patch.object(runner,'docker') as docker,self.assertRaisesRegex(ValueError,'handoff'):
            runner.run(args)
        docker.assert_not_called()

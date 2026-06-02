# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.evm_ml_forecast import forecast_overrun


class TestEVMMLForecast(FrappeTestCase):
	def test_forecast_returns_risk_bands(self):
		contract = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contract:
			self.skipTest("No contract")
		out = forecast_overrun(contract[0])
		self.assertIn(out["cost_overrun_risk"], ("low", "medium", "high"))
		self.assertEqual(out["model"], "evm_rule_v1")

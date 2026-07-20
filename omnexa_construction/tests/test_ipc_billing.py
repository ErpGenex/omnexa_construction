# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.ipc_billing import compute_ipc_amounts


class TestIpcBilling(FrappeTestCase):
	def test_first_certificate_period_equals_cumulative(self):
		out = compute_ipc_amounts(
			billable_contract_value=1_000_000,
			cumulative_completion_percent=40,
			prior_certified_completion_percent=0,
			retention_percent=10,
			advance_recovery=0,
		)
		self.assertAlmostEqual(out["cumulative_value_billed"], 400_000)
		self.assertAlmostEqual(out["prior_cumulative_billed"], 0)
		self.assertAlmostEqual(out["gross_amount"], 400_000)
		self.assertAlmostEqual(out["retention_deduction"], 40_000)
		self.assertAlmostEqual(out["net_amount"], 360_000)

	def test_second_certificate_period_is_increment(self):
		out = compute_ipc_amounts(
			billable_contract_value=1_000_000,
			cumulative_completion_percent=55,
			prior_certified_completion_percent=40,
			retention_percent=10,
			advance_recovery=5000,
		)
		self.assertAlmostEqual(out["gross_amount"], 150_000)
		self.assertAlmostEqual(out["retention_deduction"], 15_000)
		self.assertAlmostEqual(out["net_amount"], 130_000)

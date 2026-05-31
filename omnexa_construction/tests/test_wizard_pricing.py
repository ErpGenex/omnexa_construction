# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.pricing import (
	compute_ipc_amounts_with_discount,
	detail_amount,
	money,
)


class TestWizardPricing(FrappeTestCase):
	def test_detail_amount_split_rates(self):
		class D:
			quantity = 10
			unit_rate = 0
			labor_rate = 100
			material_rate = 50
			equipment_rate = 10

		self.assertEqual(detail_amount(D()), money(10 * 160))

	def test_ipc_discount_reduces_net(self):
		base = compute_ipc_amounts_with_discount(
			billable_contract_value=1_000_000,
			cumulative_completion_percent=50,
			prior_certified_completion_percent=0,
			retention_percent=5,
			advance_recovery=0,
			discount_percent=2,
		)
		no_disc = compute_ipc_amounts_with_discount(
			billable_contract_value=1_000_000,
			cumulative_completion_percent=50,
			prior_certified_completion_percent=0,
			retention_percent=5,
			advance_recovery=0,
			discount_percent=0,
		)
		self.assertLess(base["net_amount"], no_disc["net_amount"])

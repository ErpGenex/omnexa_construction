# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests import IntegrationTestCase

from omnexa_construction.evm_metrics import evm_snapshot, schedule_percent_planned


class TestEvmWbsIntegration(IntegrationTestCase):
	def test_evm_snapshot_keys(self):
		contracts = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contracts:
			self.skipTest("No project contract")
		snap = evm_snapshot(contracts[0])
		for key in ("bac", "pv", "ev", "vac", "tcpi", "schedule_source", "committed_cost"):
			self.assertIn(key, snap)

	def test_schedule_percent_planned(self):
		pct = schedule_percent_planned("2026-01-01", "2026-12-31", "2026-06-15")
		self.assertGreater(pct, 0)
		self.assertLess(pct, 100)

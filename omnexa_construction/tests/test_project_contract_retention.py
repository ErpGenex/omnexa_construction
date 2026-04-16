# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.contract_financials import retention_held_from_certified_ipc


class TestProjectContractRetention(FrappeTestCase):
	@patch(
		"omnexa_construction.contract_financials.frappe.db.sql",
		return_value=[[12500.5]],
	)
	def test_retention_held_sums_ipc(self, _sql):
		self.assertEqual(retention_held_from_certified_ipc("CNT-1"), 12500.5)

	@patch(
		"omnexa_construction.contract_financials.frappe.db.sql",
		return_value=[],
	)
	def test_retention_held_no_rows(self, _sql):
		self.assertEqual(retention_held_from_certified_ipc("CNT-2"), 0.0)

	def test_retention_held_skips_sql_without_contract(self):
		self.assertEqual(retention_held_from_certified_ipc(""), 0.0)

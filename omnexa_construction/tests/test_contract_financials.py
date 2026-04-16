# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.contract_financials import approved_change_order_impact, billable_contract_value


class TestContractFinancials(FrappeTestCase):
	@patch("omnexa_construction.contract_financials.frappe.db.get_value", return_value=1000.0)
	@patch("omnexa_construction.contract_financials.frappe.db.sql", return_value=[[250.0]])
	def test_billable_contract_value_includes_change_orders(self, _sql, _gv):
		self.assertEqual(billable_contract_value("CNT-TEST"), 1250.0)

	@patch("omnexa_construction.contract_financials.frappe.db.sql", return_value=[])
	def test_approved_change_order_impact_empty(self, _sql):
		self.assertEqual(approved_change_order_impact("CNT-X"), 0.0)

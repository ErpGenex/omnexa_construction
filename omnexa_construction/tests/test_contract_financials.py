# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.contract_financials import (
	approved_change_order_impact,
	billable_contract_value,
	certified_ipc_net_total,
	claims_active_count,
	eot_approved_count,
	refresh_project_contract_financials,
)


class TestContractFinancials(FrappeTestCase):
	@patch("omnexa_construction.contract_financials.frappe.db.get_value", return_value=1000.0)
	@patch("omnexa_construction.contract_financials.frappe.db.sql", return_value=[[250.0]])
	def test_billable_contract_value_includes_change_orders(self, _sql, _gv):
		self.assertEqual(billable_contract_value("CNT-TEST"), 1250.0)

	@patch("omnexa_construction.contract_financials.frappe.db.sql", return_value=[])
	def test_approved_change_order_impact_empty(self, _sql):
		self.assertEqual(approved_change_order_impact("CNT-X"), 0.0)

	@patch("omnexa_construction.contract_financials.frappe.db.sql", return_value=[[500.0]])
	def test_certified_ipc_net_total(self, _sql):
		self.assertEqual(certified_ipc_net_total("CNT-1"), 500.0)

	@patch("omnexa_construction.contract_financials.frappe.db.count", return_value=2)
	def test_eot_approved_count(self, _count):
		self.assertEqual(eot_approved_count("CNT-1"), 2)

	@patch("omnexa_construction.contract_financials.frappe.db.count", return_value=1)
	def test_claims_active_count(self, _count):
		self.assertEqual(claims_active_count("CNT-1"), 1)

	@patch("omnexa_construction.contract_financials.retention_held_from_certified_ipc", return_value=75.0)
	@patch("omnexa_construction.contract_financials.approved_change_order_impact", return_value=200.0)
	@patch("omnexa_construction.contract_financials.frappe.db.exists", return_value=True)
	@patch("omnexa_construction.contract_financials.frappe.db.get_value", return_value=1000.0)
	@patch("omnexa_construction.contract_financials.frappe.db.set_value")
	def test_refresh_project_contract_financials(self, set_value, _gv, _exists, _co, _ret):
		refresh_project_contract_financials("CNT-REF")
		set_value.assert_called_once_with(
			"Project Contract",
			"CNT-REF",
			{
				"approved_change_orders_value": 200.0,
				"revised_contract_value": 1200.0,
				"retention_held_to_date": 75.0,
			},
			update_modified=False,
		)

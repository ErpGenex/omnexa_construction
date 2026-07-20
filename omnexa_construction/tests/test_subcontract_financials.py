# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.subcontract_financials import (
	refresh_subcontract_work_order_amounts,
	subcontract_certified_total,
	subcontract_paid_total,
)


class TestSubcontractFinancials(FrappeTestCase):
	@patch("omnexa_construction.subcontract_financials.frappe.db.sql", return_value=[[1500.0]])
	def test_subcontract_certified_total(self, _sql):
		self.assertEqual(subcontract_certified_total("SCW-1"), 1500.0)

	@patch("omnexa_construction.subcontract_financials.frappe.db.sql", return_value=[[900.0]])
	def test_subcontract_paid_total(self, _sql):
		self.assertEqual(subcontract_paid_total("SCW-1"), 900.0)

	@patch("omnexa_construction.subcontract_financials.subcontract_paid_total", return_value=900.0)
	@patch("omnexa_construction.subcontract_financials.subcontract_certified_total", return_value=2000.0)
	@patch("omnexa_construction.subcontract_financials.frappe.db.exists", return_value=True)
	@patch("omnexa_construction.subcontract_financials.frappe.db.get_value", return_value=4000.0)
	@patch("omnexa_construction.subcontract_financials.frappe.db.set_value")
	def test_refresh_subcontract_work_order_amounts(self, set_value, _gv, _exists, _cert, _paid):
		refresh_subcontract_work_order_amounts("SCW-1")
		set_value.assert_called_once_with(
			"Subcontract Work Order",
			"SCW-1",
			{
				"amount_certified": 2000.0,
				"amount_paid": 900.0,
				"progress_percent": 50.0
	},
			update_modified=False,
		)

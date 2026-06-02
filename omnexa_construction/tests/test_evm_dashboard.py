# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.omnexa_construction.report.construction_evm_dashboard.construction_evm_dashboard import (
	_columns,
	execute,
)


class TestEvmDashboard(FrappeTestCase):
	def test_columns_defined(self):
		cols = _columns()
		names = {c["fieldname"] for c in cols}
		self.assertIn("cpi", names)
		self.assertIn("spi", names)

	@patch(
		"omnexa_construction.omnexa_construction.report.construction_evm_dashboard.construction_evm_dashboard.evm_snapshot",
		return_value={"project_contract": "CTR-1", "contract_title": "Demo", "ev": 100, "pv": 90, "ac": 80, "cpi": 1.1, "spi": 1.0},
	)
	@patch(
		"omnexa_construction.omnexa_construction.report.construction_evm_dashboard.construction_evm_dashboard.get_all_filters",
		return_value={},
	)
	@patch(
		"omnexa_construction.omnexa_construction.report.construction_evm_dashboard.construction_evm_dashboard.frappe.get_all",
		return_value=[frappe._dict(name="CTR-1")],
	)
	def test_execute_returns_chart(self, _all, _filters, _snap):
		columns, data, _msg, chart, summary = execute({"company": "Test Co"})
		self.assertEqual(len(data), 1)
		self.assertEqual(chart["type"], "bar")
		self.assertTrue(summary)
		labels = {row.get("label") for row in summary}
		self.assertIn("Delayed Contracts", labels)
		self.assertIn("Avg SV Days", labels)

# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.portfolio_api import get_portfolio_dashboard


class TestPortfolioApi(FrappeTestCase):
	def test_portfolio_dashboard_returns_expected_keys(self):
		company = frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("No company on site")
		out = get_portfolio_dashboard(company)
		for key in (
			"contract_count",
			"total_bac",
			"open_ipc",
			"open_ncr",
			"open_rfi",
			"open_disputes",
			"open_early_warnings",
			"contracts",
		):
			self.assertIn(key, out)

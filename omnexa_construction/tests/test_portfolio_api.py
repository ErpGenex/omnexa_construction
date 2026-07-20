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
			"total_ev",
			"portfolio_spi",
			"avg_schedule_variance_days",
			"delayed_contracts",
			"at_risk_contracts",
			"on_track_contracts",
			"open_ipc",
			"open_ncr",
			"open_rfi",
			"open_disputes",
			"open_early_warnings",
			"contracts",
		):
			self.assertIn(key, out)
		if out.get("contracts"):
			self.assertIn("schedule_health_status", out["contracts"][0])

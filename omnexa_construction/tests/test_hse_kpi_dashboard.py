# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.hse_kpi_dashboard import get_hse_kpi_dashboard


class TestHSEKPIDashboard(FrappeTestCase):
	def test_dashboard(self):
		company = frappe.defaults.get_defaults().company
		out = get_hse_kpi_dashboard(company)
		self.assertIn("iso_45001_score", out)

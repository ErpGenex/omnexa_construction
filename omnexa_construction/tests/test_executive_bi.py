# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.executive_bi import get_executive_bi_dashboard


class TestExecutiveBI(FrappeTestCase):
	def test_bi_dashboard(self):
		company = frappe.defaults.get_defaults().company
		out = get_executive_bi_dashboard(company)
		self.assertEqual(out["bi_version"], "1.0")
		self.assertIn("contract_count", out)
